from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .config import ExperimentConfig, SiteConfig, SyntheticConfig
from .controllers import ProposedController, get_proposed_controller_params
from .metrics import compute_group_metrics
from .pipeline import _profile_iterator, _run_named_controller_on_dataset
from .reporting import (
    build_claims_by_scenario_table,
    build_claims_summary_table,
    build_main_comparison_table,
    dataframe_to_latex_table,
)
from .simulation import attach_profile_columns, simulate_controller
from .stats_utils import paired_stats_table
from .synth import generate_dataset
from .utils import ensure_dir, save_json


PUBLICATION_SEARCH_KEYS = (
    'base_soft_low', 'prep_power_cap_kw', 'lookahead_gain', 'min_useful_cmd_kw'
)

PUBLICATION_CANDIDATES: list[dict[str, float]] = [
    {'base_soft_low': 0.32, 'prep_power_cap_kw': 3.0, 'lookahead_gain': 0.01, 'min_useful_cmd_kw': 0.25},
    {'base_soft_low': 0.32, 'prep_power_cap_kw': 4.0, 'lookahead_gain': 0.01, 'min_useful_cmd_kw': 0.25},
    {'base_soft_low': 0.32, 'prep_power_cap_kw': 5.0, 'lookahead_gain': 0.01, 'min_useful_cmd_kw': 0.25},
    {'base_soft_low': 0.32, 'prep_power_cap_kw': 4.0, 'lookahead_gain': 0.02, 'min_useful_cmd_kw': 0.25},
    {'base_soft_low': 0.32, 'prep_power_cap_kw': 4.0, 'lookahead_gain': 0.01, 'min_useful_cmd_kw': 0.50},
    {'base_soft_low': 0.34, 'prep_power_cap_kw': 3.0, 'lookahead_gain': 0.01, 'min_useful_cmd_kw': 0.25},
    {'base_soft_low': 0.34, 'prep_power_cap_kw': 4.0, 'lookahead_gain': 0.01, 'min_useful_cmd_kw': 0.25},
    {'base_soft_low': 0.34, 'prep_power_cap_kw': 4.0, 'lookahead_gain': 0.02, 'min_useful_cmd_kw': 0.25},
    {'base_soft_low': 0.34, 'prep_power_cap_kw': 4.0, 'lookahead_gain': 0.02, 'min_useful_cmd_kw': 0.50},
    {'base_soft_low': 0.36, 'prep_power_cap_kw': 4.0, 'lookahead_gain': 0.02, 'min_useful_cmd_kw': 0.50},
    {'base_soft_low': 0.36, 'prep_power_cap_kw': 5.0, 'lookahead_gain': 0.04, 'min_useful_cmd_kw': 0.50},
    {'base_soft_low': 0.38, 'prep_power_cap_kw': 5.0, 'lookahead_gain': 0.04, 'min_useful_cmd_kw': 0.50},
]

PUBLICATION_BASELINES = ['NC', 'GR', 'RS', 'FBRL']
PUBLICATION_METRICS = [
    'ramp95_kw_per_min',
    'cap_violation_pct_total',
    'throughput_kwh',
    'lfp_cycle_loss_pct',
    'idod',
    'flip_per_day',
]


def _split_seeds_for_publication(seeds: list[int]) -> tuple[list[int], list[int]]:
    ordered = sorted(dict.fromkeys(int(s) for s in seeds))
    if len(ordered) <= 1:
        return ordered, ordered
    train = ordered[::2]
    holdout = ordered[1::2]
    if not holdout:
        holdout = train
    return train, holdout


def _holdout_is_valid(train_seeds: list[int], holdout_seeds: list[int]) -> bool:
    return bool(train_seeds and holdout_seeds and set(train_seeds) != set(holdout_seeds))


def _build_repeated_seed_splits(seeds: list[int]) -> list[tuple[list[int], list[int]]]:
    ordered = sorted(dict.fromkeys(int(s) for s in seeds))
    if len(ordered) <= 1:
        return [(ordered, ordered)]

    half = max(1, len(ordered) // 2)
    split_candidates = [
        (ordered[::2], ordered[1::2]),
        (ordered[1::2], ordered[::2]),
        (ordered[:half], ordered[half:]),
        (ordered[half:], ordered[:half]),
        ([s for i, s in enumerate(ordered) if i % 3 != 0], [s for i, s in enumerate(ordered) if i % 3 == 0]),
    ]

    unique: list[tuple[list[int], list[int]]] = []
    seen = set()
    for train, holdout in split_candidates:
        train_norm = tuple(sorted(dict.fromkeys(train)))
        holdout_norm = tuple(sorted(dict.fromkeys(holdout)))
        if not train_norm or not holdout_norm:
            continue
        key = (train_norm, holdout_norm)
        if key in seen:
            continue
        seen.add(key)
        unique.append((list(train_norm), list(holdout_norm)))
    return unique


def _run_proposed_candidate(dataset: pd.DataFrame, site: SiteConfig, candidate_cfg: dict[str, float], label: str) -> pd.DataFrame:
    per_tick = []
    for profile in _profile_iterator(dataset):
        ctrl = ProposedController(site)
        for key, value in candidate_cfg.items():
            setattr(ctrl, key, value)
        sim = simulate_controller(profile, ctrl, site)
        tick = attach_profile_columns(sim.series, profile)
        tick['controller'] = label
        per_tick.append(tick)
    tick_df = pd.concat(per_tick, ignore_index=True)
    return compute_group_metrics(tick_df, site, ['controller', 'scenario', 'seed', 'scenario_seed', 'day_id'])


def _mean_key_metrics(metrics_df: pd.DataFrame) -> pd.Series:
    return metrics_df[PUBLICATION_METRICS].mean()


def _score_vs_gr(candidate_mean: pd.Series, gr_mean: pd.Series) -> float:
    delta = candidate_mean - gr_mean
    return float(
        1.0 * delta['ramp95_kw_per_min'] +
        2.0 * delta['cap_violation_pct_total'] +
        0.25 * delta['throughput_kwh'] +
        75.0 * delta['idod'] +
        0.05 * delta['flip_per_day']
    )


def _candidate_pool(site: SiteConfig) -> list[dict[str, float | str]]:
    pool = []
    seen: set[tuple[float, float, float, float]] = set()
    default_params = get_proposed_controller_params(site)
    default_cfg = {key: float(default_params[key]) for key in PUBLICATION_SEARCH_KEYS}
    configs = list(PUBLICATION_CANDIDATES)
    configs.append(default_cfg)
    for idx, cfg in enumerate(configs, start=1):
        signature = tuple(float(cfg[key]) for key in PUBLICATION_SEARCH_KEYS)
        if signature in seen:
            continue
        seen.add(signature)
        pool.append({'candidate': f'Candidate_{len(pool) + 1:02d}', **cfg})
    return pool


def _run_candidate_pool(dataset: pd.DataFrame, site: SiteConfig, candidate_pool: list[dict[str, float | str]]) -> pd.DataFrame:
    blocks = []
    for candidate in candidate_pool:
        cfg = {key: float(candidate[key]) for key in PUBLICATION_SEARCH_KEYS}
        blocks.append(_run_proposed_candidate(dataset, site, cfg, str(candidate['candidate'])))
    return pd.concat(blocks, ignore_index=True)


def _candidate_scores_for_subset(candidate_metrics_df: pd.DataFrame, gr_metrics_df: pd.DataFrame,
                                 candidate_pool: list[dict[str, float | str]], seeds: list[int]) -> pd.DataFrame:
    candidate_subset = candidate_metrics_df[candidate_metrics_df['seed'].isin(seeds)].copy()
    gr_subset = gr_metrics_df[gr_metrics_df['seed'].isin(seeds)].copy()
    gr_mean = _mean_key_metrics(gr_subset)
    rows = []
    for candidate in candidate_pool:
        label = str(candidate['candidate'])
        candidate_metrics = candidate_subset[candidate_subset['controller'] == label].copy()
        candidate_mean = _mean_key_metrics(candidate_metrics)
        delta = candidate_mean - gr_mean
        rows.append({
            'candidate': label,
            **{key: float(candidate[key]) for key in PUBLICATION_SEARCH_KEYS},
            **{f'{metric}_mean': float(candidate_mean[metric]) for metric in PUBLICATION_METRICS},
            **{f'{metric}_delta_vs_gr': float(delta[metric]) for metric in PUBLICATION_METRICS},
            'score_vs_gr': _score_vs_gr(candidate_mean, gr_mean),
        })
    return pd.DataFrame(rows).sort_values('score_vs_gr').reset_index(drop=True)


def _build_candidate_stability(candidate_split_scores_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for candidate, g in candidate_split_scores_df.groupby('candidate'):
        first = g.iloc[0]
        rows.append({
            'candidate': candidate,
            **{key: float(first[key]) for key in PUBLICATION_SEARCH_KEYS},
            'mean_train_score_vs_gr': float(g['train_score_vs_gr'].mean()),
            'mean_hold_score_vs_gr': float(g['hold_score_vs_gr'].mean()),
            'std_hold_score_vs_gr': float(g['hold_score_vs_gr'].std(ddof=1)) if len(g) > 1 else 0.0,
            'max_hold_score_vs_gr': float(g['hold_score_vs_gr'].max()),
            'mean_hold_rank': float(g['hold_rank'].mean()),
            'best_hold_rank_count': int((g['hold_rank'] == 1).sum()),
            'mean_hold_ramp_delta_vs_gr': float(g['ramp95_kw_per_min_delta_vs_gr'].mean()),
            'mean_hold_cap_delta_vs_gr': float(g['cap_violation_pct_total_delta_vs_gr'].mean()),
            'mean_hold_throughput_delta_vs_gr': float(g['throughput_kwh_delta_vs_gr'].mean()),
            'mean_hold_lfp_cycle_loss_delta_vs_gr': float(g['lfp_cycle_loss_pct_delta_vs_gr'].mean()),
            'mean_hold_idod_delta_vs_gr': float(g['idod_delta_vs_gr'].mean()),
            'mean_hold_flip_delta_vs_gr': float(g['flip_per_day_delta_vs_gr'].mean()),
        })
    return pd.DataFrame(rows).sort_values(
        ['mean_hold_score_vs_gr', 'max_hold_score_vs_gr', 'mean_hold_cap_delta_vs_gr']
    ).reset_index(drop=True)


def _render_publication_audit_md(*, train_seeds: list[int], holdout_seeds: list[int], holdout_valid: bool,
                                 default_params: dict[str, Any],
                                 selected_row: pd.Series, selected_stability_row: pd.Series | None,
                                 stability_df: pd.DataFrame, holdout_summary: pd.DataFrame,
                                 claims_df: pd.DataFrame, claims_by_scenario_df: pd.DataFrame,
                                 pairwise_stats_df: pd.DataFrame) -> str:
    lines = []
    lines.append('# Publication Audit')
    lines.append('')
    lines.append('## Scope')
    lines.append('')
    lines.append('This audit reports the canonical train/hold-out split together with repeated-split stability checks for the Proposed controller.')
    lines.append('Its goal is not to guarantee publication; it documents how defensible the controller claims are under repeatable selection and hold-out checks.')
    lines.append('')
    lines.append('## Canonical Split')
    lines.append('')
    lines.append(f'- Train seeds: `{train_seeds}`')
    lines.append(f'- Hold-out seeds: `{holdout_seeds}`')
    if not holdout_valid:
        lines.append('- Hold-out validity: `invalid` (single-seed smoke run; reported hold-out files are resubstitution diagnostics only)')
    else:
        lines.append('- Hold-out validity: `valid`')
    lines.append('')
    lines.append('## Selected Candidate')
    lines.append('')
    lines.append(f'- Candidate label: `{selected_row["candidate"]}`')
    lines.append(f'- Canonical train score vs GR: `{selected_row["score_vs_gr"]:.4f}`')
    if selected_stability_row is not None:
        lines.append(f'- Repeated-split mean hold score vs GR: `{selected_stability_row["mean_hold_score_vs_gr"]:.4f}`')
        lines.append(f'- Repeated-split std hold score vs GR: `{selected_stability_row["std_hold_score_vs_gr"]:.4f}`')
        lines.append(f'- Repeated-split mean hold cap delta vs GR: `{selected_stability_row["mean_hold_cap_delta_vs_gr"]:.4f}`')
        lines.append(f'- Repeated-split mean hold rank: `{selected_stability_row["mean_hold_rank"]:.2f}`')
    lines.append('- Selected parameters:')
    for key in PUBLICATION_SEARCH_KEYS:
        lines.append(f'  - `{key}` = `{selected_row[key]}`')
    lines.append('')
    lines.append('## Default Proposed Parameters')
    lines.append('')
    for key, value in default_params.items():
        if key in PUBLICATION_SEARCH_KEYS:
            lines.append(f'- `{key}` = `{value}`')
    lines.append('')
    lines.append('## Candidate Stability Top-5')
    lines.append('')
    lines.append(_dataframe_to_markdown(stability_df.head(5)))
    lines.append('')
    lines.append('## Hold-out Main Means')
    lines.append('')
    lines.append(_dataframe_to_markdown(holdout_summary))
    lines.append('')
    lines.append('## Hold-out Claim Audit')
    lines.append('')
    lines.append(_dataframe_to_markdown(claims_df))
    lines.append('')
    lines.append('## Hold-out Claim Audit By Scenario')
    lines.append('')
    lines.append(_dataframe_to_markdown(claims_by_scenario_df))
    lines.append('')
    lines.append('## Hold-out Pairwise Stats')
    lines.append('')
    lines.append(_dataframe_to_markdown(pairwise_stats_df))
    lines.append('')
    lines.append('## Interpretation')
    lines.append('')
    lines.append('- `score_vs_gr < 0` means the selected candidate beats GR under the weighted publication score used by this audit.')
    lines.append('- Repeated-split stability is stricter than a single split: lower mean hold score and lower variance imply a more robust candidate choice.')
    lines.append('- The claim audit is stricter than the score: it reports per-metric delta means and win/tie/loss counts rather than a single scalar.')
    lines.append('- A publishable manuscript still needs human-authored novelty positioning, related-work review, venue selection, and careful claim wording.')
    return '\n'.join(lines)


def _dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return '_empty_'
    cols = list(df.columns)
    header = '| ' + ' | '.join(str(c) for c in cols) + ' |'
    sep = '| ' + ' | '.join('---' for _ in cols) + ' |'
    body = []
    for _, row in df.iterrows():
        body.append('| ' + ' | '.join(str(row[c]) for c in cols) + ' |')
    return '\n'.join([header, sep] + body)


def run_publication_package(site: SiteConfig, synth: SyntheticConfig, exp: ExperimentConfig, output_dir: str | Path) -> dict[str, Any]:
    outdir = ensure_dir(output_dir)
    dataset = generate_dataset(list(exp.seeds), site, synth)
    train_seeds, holdout_seeds = _split_seeds_for_publication(list(exp.seeds))
    holdout_valid = _holdout_is_valid(train_seeds, holdout_seeds)
    holdout_dataset = dataset[dataset['seed'].isin(holdout_seeds)].copy()

    candidate_pool = _candidate_pool(site)
    candidate_metrics_df = _run_candidate_pool(dataset, site, candidate_pool)
    gr_metrics_df = _run_named_controller_on_dataset(dataset, 'GR', site)[1]

    train_rank_df = _candidate_scores_for_subset(candidate_metrics_df, gr_metrics_df, candidate_pool, train_seeds)
    holdout_rank_df = _candidate_scores_for_subset(candidate_metrics_df, gr_metrics_df, candidate_pool, holdout_seeds)
    selected_row = train_rank_df.iloc[0].copy()
    selected_cfg = {key: float(selected_row[key]) for key in PUBLICATION_SEARCH_KEYS}
    selected_label = str(selected_row['candidate'])

    split_rows = []
    for split_id, (split_train, split_holdout) in enumerate(_build_repeated_seed_splits(list(exp.seeds)), start=1):
        split_train_df = _candidate_scores_for_subset(candidate_metrics_df, gr_metrics_df, candidate_pool, split_train)
        split_holdout_df = _candidate_scores_for_subset(candidate_metrics_df, gr_metrics_df, candidate_pool, split_holdout)
        split_holdout_df['hold_rank'] = split_holdout_df['score_vs_gr'].rank(method='min', ascending=True).astype(int)
        metric_delta_cols = [f'{metric}_delta_vs_gr' for metric in PUBLICATION_METRICS]
        merged = split_train_df[['candidate', 'score_vs_gr']].rename(columns={'score_vs_gr': 'train_score_vs_gr'}).merge(
            split_holdout_df[['candidate', 'score_vs_gr', 'hold_rank'] + metric_delta_cols],
            on='candidate',
            how='inner',
        )
        merged = merged.rename(columns={'score_vs_gr': 'hold_score_vs_gr'})
        merged['split_id'] = split_id
        for key in PUBLICATION_SEARCH_KEYS:
            merged[key] = split_holdout_df.set_index('candidate')[key].reindex(merged['candidate']).to_numpy()
        split_rows.append(merged)
    candidate_split_scores_df = pd.concat(split_rows, ignore_index=True)
    stability_df = _build_candidate_stability(candidate_split_scores_df)
    selected_stability = stability_df[stability_df['candidate'] == selected_label].copy()
    selected_stability_row = selected_stability.iloc[0] if not selected_stability.empty else None

    selected_holdout_metrics = candidate_metrics_df[
        (candidate_metrics_df['controller'] == selected_label) &
        (candidate_metrics_df['seed'].isin(holdout_seeds))
    ].copy()
    selected_holdout_metrics['controller'] = 'Proposed'

    baseline_blocks = []
    for controller_name in PUBLICATION_BASELINES:
        baseline_blocks.append(_run_named_controller_on_dataset(holdout_dataset, controller_name, site)[1])
    holdout_metrics_df = pd.concat([selected_holdout_metrics] + baseline_blocks, ignore_index=True)

    holdout_summary_df = build_main_comparison_table(
        holdout_metrics_df[holdout_metrics_df['controller'].isin(['Proposed'] + PUBLICATION_BASELINES)]
    )
    claims_df = build_claims_summary_table(holdout_metrics_df, 'Proposed', PUBLICATION_BASELINES)
    claims_by_scenario_df = build_claims_by_scenario_table(holdout_metrics_df, 'Proposed', PUBLICATION_BASELINES)

    pairwise_rows = []
    for baseline in PUBLICATION_BASELINES:
        pairwise_rows.append(
            paired_stats_table(
                holdout_metrics_df[holdout_metrics_df['controller'].isin(['Proposed', baseline])],
                'Proposed',
                baseline,
                metrics=PUBLICATION_METRICS,
            )
        )
    pairwise_stats_df = pd.concat(pairwise_rows, ignore_index=True)

    default_params = get_proposed_controller_params(site)
    audit_md = _render_publication_audit_md(
        train_seeds=train_seeds,
        holdout_seeds=holdout_seeds,
        holdout_valid=holdout_valid,
        default_params=default_params,
        selected_row=selected_row,
        selected_stability_row=selected_stability_row,
        stability_df=stability_df,
        holdout_summary=holdout_summary_df,
        claims_df=claims_df,
        claims_by_scenario_df=claims_by_scenario_df,
        pairwise_stats_df=pairwise_stats_df,
    )

    train_rank_df.to_csv(outdir / 'candidate_search_train.csv', index=False)
    holdout_rank_df.to_csv(outdir / 'candidate_search_holdout.csv', index=False)
    candidate_split_scores_df.to_csv(outdir / 'candidate_search_repeated.csv', index=False)
    stability_df.to_csv(outdir / 'candidate_stability_summary.csv', index=False)
    holdout_summary_df.to_csv(outdir / 'holdout_main_comparison_table.csv', index=False)
    claims_df.to_csv(outdir / 'holdout_claims_summary.csv', index=False)
    claims_by_scenario_df.to_csv(outdir / 'holdout_claims_by_scenario.csv', index=False)
    pairwise_stats_df.to_csv(outdir / 'holdout_pairwise_stats.csv', index=False)
    (outdir / 'holdout_main_comparison_table.tex').write_text(
        dataframe_to_latex_table(holdout_summary_df, 'Hold-out main comparison table.', 'tab:holdout_main_auto'),
        encoding='utf-8',
    )
    (outdir / 'holdout_claims_summary.tex').write_text(
        dataframe_to_latex_table(claims_df, 'Hold-out claim audit summary.', 'tab:holdout_claims_auto'),
        encoding='utf-8',
    )
    (outdir / 'holdout_claims_by_scenario.tex').write_text(
        dataframe_to_latex_table(
            claims_by_scenario_df,
            'Hold-out claim audit summary by scenario.',
            'tab:holdout_claims_scenario_auto',
        ),
        encoding='utf-8',
    )
    (outdir / 'holdout_pairwise_stats.tex').write_text(
        dataframe_to_latex_table(pairwise_stats_df, 'Hold-out paired statistics against baselines.', 'tab:holdout_stats_auto'),
        encoding='utf-8',
    )
    (outdir / 'publication_audit.md').write_text(audit_md, encoding='utf-8')
    save_json(outdir / 'publication_selection.json', {
        'train_seeds': train_seeds,
        'holdout_seeds': holdout_seeds,
        'holdout_valid': holdout_valid,
        'default_proposed_params': default_params,
        'selected_candidate': {
            'label': selected_label,
            **selected_cfg,
            'canonical_train_score_vs_gr': float(selected_row['score_vs_gr']),
        },
        'selected_candidate_stability': None if selected_stability_row is None else {
            'mean_hold_score_vs_gr': float(selected_stability_row['mean_hold_score_vs_gr']),
            'std_hold_score_vs_gr': float(selected_stability_row['std_hold_score_vs_gr']),
            'max_hold_score_vs_gr': float(selected_stability_row['max_hold_score_vs_gr']),
            'mean_hold_rank': float(selected_stability_row['mean_hold_rank']),
            'mean_hold_cap_delta_vs_gr': float(selected_stability_row['mean_hold_cap_delta_vs_gr']),
        },
    })

    return {
        'train_rank_df': train_rank_df,
        'holdout_rank_df': holdout_rank_df,
        'candidate_split_scores_df': candidate_split_scores_df,
        'stability_df': stability_df,
        'holdout_summary_df': holdout_summary_df,
        'claims_df': claims_df,
        'claims_by_scenario_df': claims_by_scenario_df,
        'pairwise_stats_df': pairwise_stats_df,
        'output_dir': str(outdir),
    }
