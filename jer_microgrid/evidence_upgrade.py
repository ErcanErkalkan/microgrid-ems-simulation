from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from .config import SiteConfig, SyntheticConfig
from .pipeline import _run_named_controller_on_dataset
from .reporting import (
    build_claims_by_scenario_table,
    build_claims_summary_table,
    build_main_comparison_table,
    build_runtime_table,
    dataframe_to_latex_table,
)
from .stats_utils import paired_stats_table
from .synth import generate_dataset
from .utils import ensure_dir, save_json, scenario_seed_id, time_of_use_peak_flag


LIGHTWEIGHT_CONTROLLERS = ['Proposed', 'NC', 'GR', 'RS', 'FBRL']
PRIMARY_METRICS = [
    'ramp95_kw_per_min',
    'cap_violation_pct_total',
    'throughput_kwh',
    'lfp_cycle_loss_pct',
    'idod',
    'flip_per_day',
]
OPSD_15MIN_URL = 'https://data.open-power-system-data.org/time_series/2020-10-06/time_series_15min_singleindex.csv'
OPSD_USECOLS = [
    'utc_timestamp',
    'DE_load_actual_entsoe_transparency',
    'DE_solar_generation_actual',
    'DE_wind_generation_actual',
]
SEASON_MAP = {
    12: 'winter',
    1: 'winter',
    2: 'winter',
    3: 'spring',
    4: 'spring',
    5: 'spring',
    6: 'summer',
    7: 'summer',
    8: 'summer',
    9: 'fall',
    10: 'fall',
    11: 'fall',
}


def _save_pairwise_tables(metrics_df: pd.DataFrame, outdir: Path, baselines: list[str]) -> pd.DataFrame:
    pairwise_blocks = []
    for baseline in baselines:
        pairwise_blocks.append(
            paired_stats_table(
                metrics_df[metrics_df['controller'].isin(['Proposed', baseline])],
                'Proposed',
                baseline,
                metrics=PRIMARY_METRICS,
            )
        )
    pairwise_df = pd.concat(pairwise_blocks, ignore_index=True)
    pairwise_df.to_csv(outdir / 'paired_stats_all_baselines.csv', index=False)
    (outdir / 'paired_stats_all_baselines.tex').write_text(
        dataframe_to_latex_table(
            pairwise_df,
            'Paired statistics: Proposed versus every lightweight baseline.',
            'tab:evidence_pairwise_auto',
        ),
        encoding='utf-8',
    )
    return pairwise_df


def _save_common_tables(metrics_df: pd.DataFrame, tick_df: pd.DataFrame, outdir: Path) -> dict[str, pd.DataFrame]:
    main_df = build_main_comparison_table(metrics_df)
    claims_df = build_claims_summary_table(metrics_df, 'Proposed', [c for c in LIGHTWEIGHT_CONTROLLERS if c != 'Proposed'])
    claims_by_scenario_df = build_claims_by_scenario_table(
        metrics_df,
        'Proposed',
        [c for c in LIGHTWEIGHT_CONTROLLERS if c != 'Proposed'],
    )
    runtime_df = build_runtime_table(tick_df)
    pairwise_df = _save_pairwise_tables(metrics_df, outdir, [c for c in LIGHTWEIGHT_CONTROLLERS if c != 'Proposed'])

    main_df.to_csv(outdir / 'main_comparison_table.csv', index=False)
    claims_df.to_csv(outdir / 'claims_summary_table.csv', index=False)
    claims_by_scenario_df.to_csv(outdir / 'claims_by_scenario.csv', index=False)
    runtime_df.to_csv(outdir / 'runtime_summary.csv', index=False)

    (outdir / 'main_comparison_table.tex').write_text(
        dataframe_to_latex_table(main_df, 'Main comparison table for the evidence-upgrade benchmark.', 'tab:evidence_main_auto'),
        encoding='utf-8',
    )
    (outdir / 'claims_summary_table.tex').write_text(
        dataframe_to_latex_table(claims_df, 'Directional claim audit for the evidence-upgrade benchmark.', 'tab:evidence_claims_auto'),
        encoding='utf-8',
    )
    (outdir / 'claims_by_scenario.tex').write_text(
        dataframe_to_latex_table(
            claims_by_scenario_df,
            'Scenario-wise directional claim audit for the evidence-upgrade benchmark.',
            'tab:evidence_claims_scenario_auto',
        ),
        encoding='utf-8',
    )
    (outdir / 'runtime_summary.tex').write_text(
        dataframe_to_latex_table(runtime_df, 'Runtime summary for the evidence-upgrade benchmark.', 'tab:evidence_runtime_auto'),
        encoding='utf-8',
    )

    return {
        'main_df': main_df,
        'claims_df': claims_df,
        'claims_by_scenario_df': claims_by_scenario_df,
        'runtime_df': runtime_df,
        'pairwise_df': pairwise_df,
    }


def build_extended_synthetic_evidence(
    *,
    output_dir: str | Path = 'outputs_extended_synthetic_evidence',
    seeds: list[int] | None = None,
) -> dict[str, Any]:
    outdir = ensure_dir(output_dir)
    site = SiteConfig()
    synth = SyntheticConfig(hours=24)
    seed_list = list(range(20)) if seeds is None else list(seeds)

    dataset = generate_dataset(seed_list, site, synth)
    dataset.to_csv(outdir / 'synthetic_dataset.csv', index=False)

    tick_blocks = []
    metrics_blocks = []
    for controller_name in LIGHTWEIGHT_CONTROLLERS:
        tick_df, metrics_df = _run_named_controller_on_dataset(dataset, controller_name, site)
        tick_blocks.append(tick_df)
        metrics_blocks.append(metrics_df)

    tick_df = pd.concat(tick_blocks, ignore_index=True)
    metrics_df = pd.concat(metrics_blocks, ignore_index=True)
    tick_df.to_csv(outdir / 'main_tick_results.csv', index=False)
    metrics_df.to_csv(outdir / 'main_metrics_by_scenario_day.csv', index=False)

    tables = _save_common_tables(metrics_df, tick_df, outdir)

    summary = {
        'artifact': 'extended_synthetic_evidence',
        'profiles': int(metrics_df[metrics_df['controller'] == 'Proposed'][['scenario_seed', 'day_id']].drop_duplicates().shape[0]),
        'seeds': seed_list,
        'scenarios': list(synth.scenario_names),
        'hours': synth.hours,
        'controllers': LIGHTWEIGHT_CONTROLLERS,
    }
    save_json(outdir / 'run_manifest.json', summary)
    return {
        'dataset': dataset,
        'tick_df': tick_df,
        'metrics_df': metrics_df,
        **tables,
        'summary': summary,
    }


def _opsd_cache_path(repo_root: Path) -> Path:
    return repo_root / 'data_cache' / 'opsd_de_2019_15min.csv'


def _load_opsd_2019(repo_root: Path) -> pd.DataFrame:
    cache_path = _opsd_cache_path(repo_root)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        df = pd.read_csv(cache_path, parse_dates=['utc_timestamp'])
        df['utc_timestamp'] = pd.to_datetime(df['utc_timestamp'], utc=True)
        return df

    df = pd.read_csv(OPSD_15MIN_URL, usecols=OPSD_USECOLS)
    df = df.dropna().copy()
    df['utc_timestamp'] = pd.to_datetime(df['utc_timestamp'], utc=True)
    df = df[(df['utc_timestamp'] >= '2019-01-01') & (df['utc_timestamp'] < '2020-01-01')].copy()
    df.to_csv(cache_path, index=False)
    return df


def _selected_opsd_days(df: pd.DataFrame) -> list[pd.Timestamp]:
    df = df.copy()
    df['date'] = df['utc_timestamp'].dt.date
    counts = df.groupby('date').size()
    full_days = set(counts[counts == 96].index)
    selected = []
    for month in range(1, 13):
        for day in [1, 8, 15, 22]:
            candidate = pd.Timestamp(year=2019, month=month, day=day, tz='UTC').date()
            if candidate in full_days:
                selected.append(candidate)
    return selected


def _build_trace_day(day_df: pd.DataFrame, *, seed: int, target_q95_kw: float) -> tuple[pd.DataFrame, dict[str, Any]]:
    season = SEASON_MAP[int(day_df['utc_timestamp'].dt.month.iloc[0])]
    day_label = day_df['utc_timestamp'].dt.strftime('%Y-%m-%d').iloc[0]
    day_min = (
        day_df.rename(
            columns={
                'utc_timestamp': 'timestamp',
                'DE_load_actual_entsoe_transparency': 'load_raw',
                'DE_solar_generation_actual': 'pv_raw',
                'DE_wind_generation_actual': 'wind_raw',
            }
        )[['timestamp', 'load_raw', 'pv_raw', 'wind_raw']]
        .set_index('timestamp')
        .resample('1min')
        .interpolate(method='time')
        .reset_index()
    )
    base_raw = day_min['load_raw'] - (day_min['pv_raw'] + day_min['wind_raw'])
    scale = float(target_q95_kw / max(base_raw.quantile(0.95), 1e-9))

    day_min['load_kw'] = day_min['load_raw'] * scale
    day_min['pv_kw'] = day_min['pv_raw'] * scale
    day_min['wind_kw'] = day_min['wind_raw'] * scale
    day_min['base_kw'] = base_raw * scale
    day_min['peak_flag'] = time_of_use_peak_flag(pd.DatetimeIndex(day_min['timestamp']))
    day_min['scenario'] = season
    day_min['seed'] = seed
    day_min['scenario_seed'] = scenario_seed_id(season, seed)
    day_min['day_id'] = 0
    day_min['source_day'] = day_label

    trace_meta = {
        'seed': seed,
        'season': season,
        'source_day': day_label,
        'scale_factor': scale,
        'raw_net_q95_mw': float(base_raw.quantile(0.95)),
    }
    return day_min[
        ['timestamp', 'load_kw', 'pv_kw', 'wind_kw', 'base_kw', 'peak_flag', 'scenario', 'seed', 'scenario_seed', 'day_id', 'source_day']
    ], trace_meta


def build_external_trace_evidence(
    *,
    output_dir: str | Path = 'outputs_external_trace_evidence',
    target_q95_kw: float = 45.0,
) -> dict[str, Any]:
    outdir = ensure_dir(output_dir)
    repo_root = Path(__file__).resolve().parents[1]
    site = SiteConfig()
    opsd_df = _load_opsd_2019(repo_root)
    selected_days = _selected_opsd_days(opsd_df)

    dataset_blocks = []
    trace_manifest = []
    for seed, source_day in enumerate(selected_days):
        day_df = opsd_df[opsd_df['utc_timestamp'].dt.date == source_day].copy()
        trace_df, trace_meta = _build_trace_day(day_df, seed=seed, target_q95_kw=target_q95_kw)
        dataset_blocks.append(trace_df)
        trace_manifest.append(trace_meta)

    dataset = pd.concat(dataset_blocks, ignore_index=True)
    dataset.to_csv(outdir / 'trace_dataset.csv', index=False)
    pd.DataFrame(trace_manifest).to_csv(outdir / 'trace_manifest.csv', index=False)

    tick_blocks = []
    metrics_blocks = []
    for controller_name in LIGHTWEIGHT_CONTROLLERS:
        tick_df, metrics_df = _run_named_controller_on_dataset(dataset, controller_name, site)
        tick_blocks.append(tick_df)
        metrics_blocks.append(metrics_df)

    tick_df = pd.concat(tick_blocks, ignore_index=True)
    metrics_df = pd.concat(metrics_blocks, ignore_index=True)
    tick_df.to_csv(outdir / 'main_tick_results.csv', index=False)
    metrics_df.to_csv(outdir / 'main_metrics_by_scenario_day.csv', index=False)

    tables = _save_common_tables(metrics_df, tick_df, outdir)

    summary = {
        'artifact': 'external_trace_evidence',
        'profiles': int(metrics_df[metrics_df['controller'] == 'Proposed'][['scenario_seed', 'day_id']].drop_duplicates().shape[0]),
        'trace_source': 'Open Power System Data time_series 2020-10-06',
        'trace_url': OPSD_15MIN_URL,
        'trace_region': 'DE',
        'trace_year': 2019,
        'selected_days': [str(day) for day in selected_days],
        'upsample': '15min_to_1min_linear',
        'target_q95_kw': target_q95_kw,
        'controllers': LIGHTWEIGHT_CONTROLLERS,
    }
    save_json(outdir / 'run_manifest.json', summary)
    return {
        'dataset': dataset,
        'tick_df': tick_df,
        'metrics_df': metrics_df,
        **tables,
        'summary': summary,
    }


def build_evidence_upgrade_summary(
    *,
    output_dir: str | Path = 'outputs_evidence_upgrade',
    synthetic_profiles: int,
    trace_profiles: int,
    synthetic_claims_df: pd.DataFrame,
    trace_claims_df: pd.DataFrame,
) -> Path:
    outdir = ensure_dir(output_dir)
    rows = []
    for baseline in ['NC', 'GR', 'RS', 'FBRL']:
        syn = synthetic_claims_df[synthetic_claims_df['Baseline'] == baseline].iloc[0]
        tr = trace_claims_df[trace_claims_df['Baseline'] == baseline].iloc[0]
        rows.append({
            'baseline': baseline,
            'synthetic_profiles': synthetic_profiles,
            'synthetic_cap_wins': int(syn['cap_violation_pct_total_wins']),
            'synthetic_throughput_wins': int(syn['throughput_kwh_wins']),
            'synthetic_cycle_loss_wins': int(syn['lfp_cycle_loss_pct_wins']),
            'trace_profiles': trace_profiles,
            'trace_cap_wins': int(tr['cap_violation_pct_total_wins']),
            'trace_throughput_wins': int(tr['throughput_kwh_wins']),
            'trace_cycle_loss_wins': int(tr['lfp_cycle_loss_pct_wins']),
        })
    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(outdir / 'evidence_upgrade_summary.csv', index=False)

    cols = list(summary_df.columns)
    header = '| ' + ' | '.join(cols) + ' |'
    sep = '| ' + ' | '.join('---' for _ in cols) + ' |'
    body = []
    for _, row in summary_df.iterrows():
        body.append('| ' + ' | '.join(str(row[col]) for col in cols) + ' |')

    md_lines = [
        '# Evidence Upgrade Summary',
        '',
        f'- Extended synthetic audit profiles: `{synthetic_profiles}`',
        f'- External trace-driven audit profiles: `{trace_profiles}`',
        '',
        '## Baseline-Wise Directional Counts',
        '',
        header,
        sep,
        *body,
        '',
        '## Interpretation',
        '',
        '- The extended synthetic audit broadens the internal stress-test evidence beyond the original small primary set.',
        '- The external trace-driven audit adds non-synthetic daily structure derived from official OPSD load/solar/wind time series.',
        '- The optimizer-based reference remains confined to the primary benchmark because its online solve path is substantially heavier than the lightweight controllers.',
    ]
    md_path = outdir / 'EVIDENCE_UPGRADE_REPORT.md'
    md_path.write_text('\n'.join(md_lines), encoding='utf-8')
    return md_path


def main() -> None:
    parser = argparse.ArgumentParser(description='Build broader evidence artifacts for the ESWA manuscript.')
    parser.add_argument('--output-root', type=str, default='outputs_evidence_upgrade')
    parser.add_argument('--synthetic-seeds', type=int, default=20)
    parser.add_argument('--target-q95-kw', type=float, default=45.0)
    args = parser.parse_args()

    root = ensure_dir(args.output_root)
    synthetic = build_extended_synthetic_evidence(
        output_dir=root / 'extended_synthetic',
        seeds=list(range(args.synthetic_seeds)),
    )
    trace = build_external_trace_evidence(
        output_dir=root / 'external_trace',
        target_q95_kw=float(args.target_q95_kw),
    )
    build_evidence_upgrade_summary(
        output_dir=root,
        synthetic_profiles=int(synthetic['summary']['profiles']),
        trace_profiles=int(trace['summary']['profiles']),
        synthetic_claims_df=synthetic['claims_df'],
        trace_claims_df=trace['claims_df'],
    )


if __name__ == '__main__':
    main()
