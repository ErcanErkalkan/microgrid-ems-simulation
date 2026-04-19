from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from .config import SiteConfig
from .controllers import ProposedController, build_controller, get_proposed_controller_params
from .metrics import compute_group_metrics
from .publication import PUBLICATION_CANDIDATES, PUBLICATION_METRICS, PUBLICATION_SEARCH_KEYS
from .simulation import attach_profile_columns, simulate_controller
from .utils import ensure_dir, save_json


BENCHMARK_SOURCES: list[tuple[str, int, Path]] = [
    ('compact_6h', 6, Path('outputs_compact_full')),
    ('medium_12h', 12, Path('outputs_medium_full')),
    ('core_24h', 24, Path('outputs_24h_core_eval')),
]


def _profile_iterator(dataset: pd.DataFrame):
    group_cols = ['benchmark_id', 'scenario', 'seed', 'scenario_seed']
    for _, g in dataset.groupby(group_cols, sort=False):
        yield g.reset_index(drop=True)


def _load_combined_dataset(repo_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    blocks: list[pd.DataFrame] = []
    catalog_rows: list[dict[str, Any]] = []
    for benchmark_id, hours, rel_dir in BENCHMARK_SOURCES:
        run_dir = repo_root / rel_dir
        dataset = pd.read_csv(run_dir / 'synthetic_dataset.csv')
        dataset['benchmark_id'] = benchmark_id
        dataset['benchmark_hours'] = hours
        blocks.append(dataset)
        for (scenario, seed), g in dataset.groupby(['scenario', 'seed'], sort=False):
            catalog_rows.append({
                'benchmark_id': benchmark_id,
                'benchmark_hours': hours,
                'scenario': str(scenario),
                'seed': int(seed),
                'ticks': int(len(g)),
                'scenario_seed': str(g['scenario_seed'].iloc[0]),
            })
    catalog_df = pd.DataFrame(catalog_rows).sort_values(
        ['benchmark_hours', 'scenario', 'seed']
    ).reset_index(drop=True)
    return pd.concat(blocks, ignore_index=True), catalog_df


def _candidate_pool(site: SiteConfig) -> list[dict[str, float | str]]:
    pool: list[dict[str, float | str]] = []
    seen: set[tuple[float, float, float, float]] = set()
    default_params = get_proposed_controller_params(site)
    configs = list(PUBLICATION_CANDIDATES)
    configs.append({key: float(default_params[key]) for key in PUBLICATION_SEARCH_KEYS})
    for cfg in configs:
        signature = tuple(float(cfg[key]) for key in PUBLICATION_SEARCH_KEYS)
        if signature in seen:
            continue
        seen.add(signature)
        pool.append({'candidate': f'Candidate_{len(pool) + 1:02d}', **cfg})
    return pool


def _run_proposed_candidate(
    dataset: pd.DataFrame,
    site: SiteConfig,
    candidate_cfg: dict[str, float],
    label: str,
) -> pd.DataFrame:
    per_tick = []
    for profile in _profile_iterator(dataset):
        ctrl = ProposedController(site)
        for key, value in candidate_cfg.items():
            setattr(ctrl, key, value)
        sim = simulate_controller(profile, ctrl, site)
        tick = attach_profile_columns(sim.series, profile)
        tick['benchmark_id'] = str(profile['benchmark_id'].iloc[0])
        tick['benchmark_hours'] = int(profile['benchmark_hours'].iloc[0])
        tick['controller'] = label
        per_tick.append(tick)
    tick_df = pd.concat(per_tick, ignore_index=True)
    return compute_group_metrics(
        tick_df,
        site,
        ['controller', 'benchmark_id', 'benchmark_hours', 'scenario', 'seed', 'scenario_seed', 'day_id'],
    )


def _run_named_controller(dataset: pd.DataFrame, site: SiteConfig, controller_name: str) -> pd.DataFrame:
    per_tick = []
    for profile in _profile_iterator(dataset):
        ctrl = build_controller(controller_name, site)
        sim = simulate_controller(profile, ctrl, site)
        tick = attach_profile_columns(sim.series, profile)
        tick['benchmark_id'] = str(profile['benchmark_id'].iloc[0])
        tick['benchmark_hours'] = int(profile['benchmark_hours'].iloc[0])
        tick['controller'] = controller_name
        per_tick.append(tick)
    tick_df = pd.concat(per_tick, ignore_index=True)
    return compute_group_metrics(
        tick_df,
        site,
        ['controller', 'benchmark_id', 'benchmark_hours', 'scenario', 'seed', 'scenario_seed', 'day_id'],
    )


def _mean_key_metrics(metrics_df: pd.DataFrame) -> pd.Series:
    return metrics_df[PUBLICATION_METRICS].mean()


def _score_vs_gr(candidate_mean: pd.Series, gr_mean: pd.Series) -> float:
    delta = candidate_mean - gr_mean
    return float(
        1.0 * delta['ramp95_kw_per_min']
        + 2.0 * delta['cap_violation_pct_total']
        + 0.25 * delta['throughput_kwh']
        + 75.0 * delta['idod']
        + 0.05 * delta['flip_per_day']
    )


def _build_split_specs() -> list[dict[str, Any]]:
    return [
        {
            'split_id': 'seed0_to_seed1',
            'train': lambda df: df['seed'] == 0,
            'holdout': lambda df: df['seed'] == 1,
            'canonical': True,
        },
        {
            'split_id': 'seed1_to_seed0',
            'train': lambda df: df['seed'] == 1,
            'holdout': lambda df: df['seed'] == 0,
            'canonical': False,
        },
        {
            'split_id': 'short_medium_to_core',
            'train': lambda df: df['benchmark_id'].isin(['compact_6h', 'medium_12h']),
            'holdout': lambda df: df['benchmark_id'].isin(['core_24h']),
            'canonical': False,
        },
        {
            'split_id': 'core_to_short_medium',
            'train': lambda df: df['benchmark_id'].isin(['core_24h']),
            'holdout': lambda df: df['benchmark_id'].isin(['compact_6h', 'medium_12h']),
            'canonical': False,
        },
        {
            'split_id': 'mild_to_severe',
            'train': lambda df: df['scenario'].isin(['mixed', 'cloud_edge']),
            'holdout': lambda df: df['scenario'].isin(['wind_gust', 'load_step']),
            'canonical': False,
        },
        {
            'split_id': 'severe_to_mild',
            'train': lambda df: df['scenario'].isin(['wind_gust', 'load_step']),
            'holdout': lambda df: df['scenario'].isin(['mixed', 'cloud_edge']),
            'canonical': False,
        },
    ]


def _score_candidates_for_subset(
    candidate_metrics_df: pd.DataFrame,
    gr_metrics_df: pd.DataFrame,
    candidate_pool: list[dict[str, float | str]],
    candidate_mask: pd.Series,
    gr_mask: pd.Series,
) -> pd.DataFrame:
    candidate_subset = candidate_metrics_df[candidate_mask].copy()
    gr_subset = gr_metrics_df[gr_mask].copy()
    gr_mean = _mean_key_metrics(gr_subset)
    rows: list[dict[str, Any]] = []
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
    rows: list[dict[str, Any]] = []
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


def _build_param_group_summary(stability_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key in PUBLICATION_SEARCH_KEYS:
        for value, g in stability_df.groupby(key):
            rows.append({
                'parameter': key,
                'value': float(value),
                'n_candidates': int(len(g)),
                'mean_hold_score_vs_gr': float(g['mean_hold_score_vs_gr'].mean()),
                'min_hold_score_vs_gr': float(g['mean_hold_score_vs_gr'].min()),
                'max_hold_score_vs_gr': float(g['mean_hold_score_vs_gr'].max()),
                'mean_hold_rank': float(g['mean_hold_rank'].mean()),
                'mean_hold_cap_delta_vs_gr': float(g['mean_hold_cap_delta_vs_gr'].mean()),
                'mean_hold_throughput_delta_vs_gr': float(g['mean_hold_throughput_delta_vs_gr'].mean()),
                'mean_hold_lfp_cycle_loss_delta_vs_gr': float(g['mean_hold_lfp_cycle_loss_delta_vs_gr'].mean()),
                'mean_hold_idod_delta_vs_gr': float(g['mean_hold_idod_delta_vs_gr'].mean()),
            })
    return pd.DataFrame(rows).sort_values(['parameter', 'value']).reset_index(drop=True)


def _build_shared_sensitivity_variants() -> list[tuple[str, str, SiteConfig]]:
    base = SiteConfig()
    variants: list[tuple[str, str, SiteConfig]] = []
    for value in [15.0, 20.0, 25.0]:
        variants.append(('r_max_kw_per_tick', f'{value:g}', replace(base, r_max_kw_per_tick=value)))
    for value in [1, 3, 5]:
        variants.append(('t_min_ticks', f'{value}', replace(base, t_min_ticks=value)))
    for value in [3, 5, 7]:
        variants.append(('w_f', f'{value}', replace(base, w_f=value)))
    for value in [5, 10, 15]:
        variants.append(('horizon_k', f'{value}', replace(base, horizon_k=value)))
    return variants


def _build_shared_sensitivity(dataset: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    default_site = SiteConfig()
    default_metrics = _run_named_controller(dataset, default_site, 'Proposed')
    default_mean = _mean_key_metrics(default_metrics)
    for parameter, value_label, site_variant in _build_shared_sensitivity_variants():
        metrics_df = _run_named_controller(dataset, site_variant, 'Proposed')
        metrics_mean = _mean_key_metrics(metrics_df)
        rows.append({
            'parameter': parameter,
            'value': value_label,
            **{metric: float(metrics_mean[metric]) for metric in PUBLICATION_METRICS},
            **{f'{metric}_delta_vs_default': float(metrics_mean[metric] - default_mean[metric]) for metric in PUBLICATION_METRICS},
        })
    return pd.DataFrame(rows).sort_values(['parameter', 'value']).reset_index(drop=True)


def _render_parameter_audit_md(
    *,
    catalog_df: pd.DataFrame,
    canonical_df: pd.DataFrame,
    stability_df: pd.DataFrame,
    group_df: pd.DataFrame,
    shared_df: pd.DataFrame,
    default_params: dict[str, Any],
) -> str:
    lines: list[str] = []
    lines.append('# Parameter Audit')
    lines.append('')
    lines.append('## Combined Benchmark Scope')
    lines.append('')
    lines.append(f'- Total scenario-day units: `{len(catalog_df)}`')
    lines.append(f'- Benchmark tiers: `{sorted(catalog_df["benchmark_id"].unique().tolist())}`')
    lines.append(f'- Scenario families: `{sorted(catalog_df["scenario"].unique().tolist())}`')
    lines.append('')
    lines.append('## Canonical Split')
    lines.append('')
    lines.append('- Train units: all seed `0` profiles across 6 h, 12 h, and 24 h tiers')
    lines.append('- Hold-out units: all seed `1` profiles across 6 h, 12 h, and 24 h tiers')
    lines.append('')
    lines.append('## Default Parameters')
    lines.append('')
    for key in PUBLICATION_SEARCH_KEYS:
        lines.append(f'- `{key}` = `{default_params[key]}`')
    lines.append('')
    lines.append('## Canonical Candidate Ranking')
    lines.append('')
    lines.append(_dataframe_to_markdown(canonical_df.head(8)))
    lines.append('')
    lines.append('## Stability Summary')
    lines.append('')
    lines.append(_dataframe_to_markdown(stability_df.head(8)))
    lines.append('')
    lines.append('## Grouped Search-Parameter Summary')
    lines.append('')
    lines.append(_dataframe_to_markdown(group_df))
    lines.append('')
    lines.append('## Shared-Parameter Sensitivity')
    lines.append('')
    lines.append(_dataframe_to_markdown(shared_df))
    lines.append('')
    lines.append('## Interpretation')
    lines.append('')
    lines.append('- The searched parameter block is intentionally narrow: only four aggressiveness parameters are varied.')
    lines.append('- Default settings are defended by a plateau argument rather than a single-point optimum claim.')
    lines.append('- The shared control-loop parameters are checked by direct sensitivity scans on the same combined benchmark.')
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


def run_parameter_audit(output_dir: str | Path = 'outputs_parameter_audit') -> dict[str, Any]:
    repo_root = Path.cwd()
    outdir = ensure_dir(repo_root / output_dir)
    site = SiteConfig()

    dataset, catalog_df = _load_combined_dataset(repo_root)
    catalog_df.to_csv(outdir / 'combined_benchmark_catalog.csv', index=False)

    candidate_pool = _candidate_pool(site)
    candidate_blocks = []
    for candidate in candidate_pool:
        cfg = {key: float(candidate[key]) for key in PUBLICATION_SEARCH_KEYS}
        candidate_blocks.append(_run_proposed_candidate(dataset, site, cfg, str(candidate['candidate'])))
    candidate_metrics_df = pd.concat(candidate_blocks, ignore_index=True)
    candidate_metrics_df.to_csv(outdir / 'candidate_metrics_by_unit.csv', index=False)

    gr_metrics_df = _run_named_controller(dataset, site, 'GR')
    gr_metrics_df.to_csv(outdir / 'gr_metrics_by_unit.csv', index=False)

    split_rows: list[dict[str, Any]] = []
    canonical_df: pd.DataFrame | None = None
    for spec in _build_split_specs():
        train_candidate_mask = spec['train'](candidate_metrics_df)
        hold_candidate_mask = spec['holdout'](candidate_metrics_df)
        train_gr_mask = spec['train'](gr_metrics_df)
        hold_gr_mask = spec['holdout'](gr_metrics_df)
        if not bool(train_candidate_mask.any()) or not bool(hold_candidate_mask.any()):
            continue
        train_df = _score_candidates_for_subset(
            candidate_metrics_df, gr_metrics_df, candidate_pool, train_candidate_mask, train_gr_mask
        )
        hold_df = _score_candidates_for_subset(
            candidate_metrics_df, gr_metrics_df, candidate_pool, hold_candidate_mask, hold_gr_mask
        )
        hold_df['hold_rank'] = hold_df['score_vs_gr'].rank(method='min', ascending=True).astype(int)
        if spec['canonical']:
            canonical_df = hold_df.copy()
        merged = train_df[['candidate', 'score_vs_gr']].rename(columns={'score_vs_gr': 'train_score_vs_gr'}).merge(
            hold_df[['candidate', 'score_vs_gr', 'hold_rank'] + [f'{metric}_delta_vs_gr' for metric in PUBLICATION_METRICS]].rename(
                columns={'score_vs_gr': 'hold_score_vs_gr'}
            ),
            on='candidate',
            how='inner',
        )
        for candidate in candidate_pool:
            label = str(candidate['candidate'])
            row = merged[merged['candidate'] == label].iloc[0].to_dict()
            row.update({
                'split_id': spec['split_id'],
                **{key: float(candidate[key]) for key in PUBLICATION_SEARCH_KEYS},
            })
            split_rows.append(row)

    if canonical_df is None:
        raise RuntimeError('Canonical candidate ranking could not be built.')

    canonical_df.to_csv(outdir / 'candidate_canonical_holdout.csv', index=False)
    split_scores_df = pd.DataFrame(split_rows).sort_values(['split_id', 'hold_rank', 'candidate']).reset_index(drop=True)
    split_scores_df.to_csv(outdir / 'candidate_split_scores.csv', index=False)

    stability_df = _build_candidate_stability(split_scores_df)
    stability_df.to_csv(outdir / 'candidate_stability_summary.csv', index=False)

    group_df = _build_param_group_summary(stability_df)
    group_df.to_csv(outdir / 'candidate_param_group_summary.csv', index=False)

    shared_df = _build_shared_sensitivity(dataset)
    shared_df.to_csv(outdir / 'shared_parameter_sensitivity.csv', index=False)

    default_params = get_proposed_controller_params(site)
    audit_md = _render_parameter_audit_md(
        catalog_df=catalog_df,
        canonical_df=canonical_df,
        stability_df=stability_df,
        group_df=group_df,
        shared_df=shared_df,
        default_params=default_params,
    )
    (outdir / 'parameter_audit.md').write_text(audit_md, encoding='utf-8')

    save_json(outdir / 'parameter_audit_manifest.json', {
        'benchmarks': [
            {'benchmark_id': benchmark_id, 'hours': hours, 'path': str(path)}
            for benchmark_id, hours, path in BENCHMARK_SOURCES
        ],
        'search_keys': list(PUBLICATION_SEARCH_KEYS),
        'candidate_pool': candidate_pool,
    })

    return {
        'catalog_df': catalog_df,
        'canonical_df': canonical_df,
        'stability_df': stability_df,
        'group_df': group_df,
        'shared_df': shared_df,
    }


def main() -> None:
    run_parameter_audit()


if __name__ == '__main__':
    main()
