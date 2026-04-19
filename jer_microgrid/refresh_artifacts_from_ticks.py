from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .config import CONTROLLERS_MAIN, PRIMARY_STRESS_METRICS, SiteConfig
from .metrics import compute_group_metrics
from .reporting import (
    build_claims_by_scenario_table,
    build_claims_summary_table,
    build_main_comparison_table,
    build_runtime_table,
    build_stress_proxy_table,
    dataframe_to_latex_table,
    save_tables,
)
from .stats_utils import paired_stats_table


def _load_site_from_manifest(run_dir: Path) -> SiteConfig:
    manifest_path = run_dir / 'run_manifest.json'
    if not manifest_path.exists():
        return SiteConfig()
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    site_payload = manifest.get('site')
    if isinstance(site_payload, dict):
        return SiteConfig(**site_payload)
    return SiteConfig()


def refresh_run(run_dir: str | Path) -> dict[str, pd.DataFrame]:
    run_path = Path(run_dir)
    site = _load_site_from_manifest(run_path)
    tick_df = pd.read_csv(run_path / 'main_tick_results.csv', low_memory=False)

    group_cols = [col for col in ['controller', 'reference_type', 'weight_label', 'scenario', 'seed', 'scenario_seed', 'day_id'] if col in tick_df.columns]
    metrics_df = compute_group_metrics(tick_df, site, group_cols)
    metrics_df.to_csv(run_path / 'main_metrics_by_scenario_day.csv', index=False)

    main_controllers = [name for name in CONTROLLERS_MAIN if name in set(metrics_df['controller'].astype(str).unique())]
    main_metrics_df = metrics_df[metrics_df['controller'].isin(main_controllers)].copy()

    main_table_df = build_main_comparison_table(main_metrics_df)
    stress_table_df = build_stress_proxy_table(main_metrics_df)
    claims_df = build_claims_summary_table(main_metrics_df, 'Proposed', [c for c in main_controllers if c != 'Proposed'])
    claims_by_scenario_df = build_claims_by_scenario_table(main_metrics_df, 'Proposed', [c for c in main_controllers if c != 'Proposed'])
    runtime_df = build_runtime_table(tick_df[tick_df['controller'].isin(main_controllers)])

    save_tables(
        run_path,
        main_df=main_table_df,
        stress_df=stress_table_df,
        claims_df=claims_df,
        claims_by_scenario_df=claims_by_scenario_df,
        runtime_df=runtime_df,
    )

    paired_metric_set = ['ramp95_kw_per_min', 'cap_violation_pct_total'] + list(dict.fromkeys(PRIMARY_STRESS_METRICS + ['flip_per_day']))
    pairwise_blocks = []
    for baseline in [c for c in main_controllers if c != 'Proposed']:
        pairwise_blocks.append(
            paired_stats_table(
                main_metrics_df[main_metrics_df['controller'].isin(['Proposed', baseline])],
                'Proposed',
                baseline,
                metrics=paired_metric_set,
            )
        )
    if pairwise_blocks:
        pairwise_df = pd.concat(pairwise_blocks, ignore_index=True)
        pairwise_df.to_csv(run_path / 'paired_stats_all_baselines.csv', index=False)
        (run_path / 'paired_stats_all_baselines.tex').write_text(
            dataframe_to_latex_table(pairwise_df, 'Paired statistics: Proposed versus every main baseline.', 'tab:stats_all_auto'),
            encoding='utf-8',
        )
    else:
        pairwise_df = pd.DataFrame()

    return {
        'metrics_df': metrics_df,
        'main_table_df': main_table_df,
        'stress_table_df': stress_table_df,
        'claims_df': claims_df,
        'claims_by_scenario_df': claims_by_scenario_df,
        'runtime_df': runtime_df,
        'pairwise_df': pairwise_df,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Refresh result summaries from existing tick-level artifacts.')
    parser.add_argument('run_dirs', nargs='+', help='Result directories containing main_tick_results.csv')
    args = parser.parse_args()
    for run_dir in args.run_dirs:
        refresh_run(run_dir)
        print(f'Refreshed summaries in {run_dir}')


if __name__ == '__main__':
    main()
