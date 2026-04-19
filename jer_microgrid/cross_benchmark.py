from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


RUNS = [
    ('compact_6h', Path('outputs_compact_full')),
    ('medium_12h', Path('outputs_medium_full')),
    ('core_24h', Path('outputs_24h_core_eval')),
]


def _load_manifest(run_dir: Path) -> dict:
    manifest_path = run_dir / 'run_manifest.json'
    return json.loads(manifest_path.read_text(encoding='utf-8'))


def _load_metrics(run_dir: Path) -> pd.DataFrame:
    return pd.read_csv(run_dir / 'main_metrics_by_scenario_day.csv')


def _load_runtime(run_dir: Path) -> pd.DataFrame:
    return pd.read_csv(run_dir / 'runtime_summary.csv')


def _load_claims(run_dir: Path) -> pd.DataFrame:
    return pd.read_csv(run_dir / 'claims_summary_table.csv')


def _pick_controller(df: pd.DataFrame, preferred: list[str]) -> str:
    available = set(df['controller'].astype(str).unique())
    for name in preferred:
        if name in available:
            return name
    raise ValueError(f'None of the preferred controllers {preferred} found.')


def _pick_runtime(runtime_df: pd.DataFrame, preferred: list[str]) -> str:
    available = set(runtime_df['Controller'].astype(str).unique())
    for name in preferred:
        if name in available:
            return name
    raise ValueError(f'None of the preferred controllers {preferred} found in runtime table.')


def build_cross_benchmark_outputs(output_dir: str | Path = 'outputs_cross_benchmark_evidence') -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict] = []
    claim_rows: list[dict] = []
    catalog_rows: list[dict] = []

    for benchmark_id, run_dir in RUNS:
        manifest = _load_manifest(run_dir)
        metrics_df = _load_metrics(run_dir)
        runtime_df = _load_runtime(run_dir)
        claims_df = _load_claims(run_dir)

        hours = int(manifest['synthetic']['hours']) if 'synthetic' in manifest else int(manifest['hours'])
        scenarios = manifest['synthetic']['scenario_names'] if 'synthetic' in manifest else manifest['scenario_names']
        seeds = manifest['experiment']['seeds'] if 'experiment' in manifest else manifest['seeds']

        proposed_name = _pick_controller(metrics_df, ['Proposed'])
        nc_name = _pick_controller(metrics_df, ['NC'])
        gr_name = _pick_controller(metrics_df, ['GR'])
        rs_name = _pick_controller(metrics_df, ['RS'])
        fbrl_name = _pick_controller(metrics_df, ['FBRL'])
        mpc_name = _pick_controller(metrics_df, ['MPC_ref', 'MPC_best_balanced', 'MPC_best_ramp'])

        proposed_runtime_name = _pick_runtime(runtime_df, ['Proposed'])
        mpc_runtime_name = _pick_runtime(runtime_df, ['MPC_ref', 'MPC_best_balanced', 'MPC_best_ramp'])

        unit_cols = ['scenario', 'seed']
        if 'day_id' in metrics_df.columns:
            unit_cols.append('day_id')

        unique_units = (
            metrics_df[metrics_df['controller'] == proposed_name][unit_cols]
            .drop_duplicates()
            .shape[0]
        )

        def row_for(controller_name: str) -> pd.Series:
            controller_block = metrics_df[metrics_df['controller'] == controller_name]
            if controller_block.empty:
                raise ValueError(f'Missing controller block for {controller_name} in {run_dir}')
            return controller_block.mean(numeric_only=True)

        proposed = row_for(proposed_name)
        nc = row_for(nc_name)
        gr = row_for(gr_name)
        rs = row_for(rs_name)
        fbrl = row_for(fbrl_name)
        mpc = row_for(mpc_name)

        proposed_cpu = float(runtime_df.loc[runtime_df['Controller'] == proposed_runtime_name, 'MeanCpuMs'].iloc[0])
        mpc_cpu = float(runtime_df.loc[runtime_df['Controller'] == mpc_runtime_name, 'MeanCpuMs'].iloc[0])

        summary_rows.append({
            'benchmark_id': benchmark_id,
            'source_dir': str(run_dir),
            'hours': hours,
            'profiles': unique_units,
            'scenario_count': len(scenarios),
            'seed_count': len(seeds),
            'proposed_ramp95': float(proposed['ramp95_kw_per_min']),
            'proposed_cap_violation_pct': float(proposed['cap_violation_pct_total']),
            'proposed_throughput_kwh': float(proposed['throughput_kwh']),
            'proposed_lfp_cycle_loss_pct': float(proposed['lfp_cycle_loss_pct']),
            'proposed_flip_per_day': float(proposed['flip_per_day']),
            'gr_ramp95': float(gr['ramp95_kw_per_min']),
            'gr_cap_violation_pct': float(gr['cap_violation_pct_total']),
            'gr_throughput_kwh': float(gr['throughput_kwh']),
            'gr_lfp_cycle_loss_pct': float(gr['lfp_cycle_loss_pct']),
            'rs_throughput_kwh': float(rs['throughput_kwh']),
            'rs_lfp_cycle_loss_pct': float(rs['lfp_cycle_loss_pct']),
            'fbrl_throughput_kwh': float(fbrl['throughput_kwh']),
            'fbrl_lfp_cycle_loss_pct': float(fbrl['lfp_cycle_loss_pct']),
            'mpc_ramp95': float(mpc['ramp95_kw_per_min']),
            'mpc_cap_violation_pct': float(mpc['cap_violation_pct_total']),
            'mpc_throughput_kwh': float(mpc['throughput_kwh']),
            'mpc_lfp_cycle_loss_pct': float(mpc['lfp_cycle_loss_pct']),
            'nc_ramp95': float(nc['ramp95_kw_per_min']),
            'nc_cap_violation_pct': float(nc['cap_violation_pct_total']),
            'proposed_mean_cpu_ms': proposed_cpu,
            'mpc_mean_cpu_ms': mpc_cpu,
        })

        claim_block = claims_df.copy()
        claim_block['benchmark_id'] = benchmark_id
        claim_block['hours'] = hours
        claim_block['profiles'] = unique_units
        claim_block['Baseline'] = claim_block['Baseline'].replace({
            'MPC_best_balanced': 'MPC_ref',
            'MPC_best_ramp': 'MPC_ref',
        })
        claim_block = claim_block.drop_duplicates(subset=['Reference', 'Baseline', 'benchmark_id'])
        claim_rows.extend(claim_block.to_dict(orient='records'))

        catalog_rows.append({
            'benchmark_id': benchmark_id,
            'source_dir': str(run_dir),
            'hours': hours,
            'scenario_names': '|'.join(scenarios),
            'seeds': '|'.join(str(x) for x in seeds),
            'profiles': unique_units,
            'controllers_available': '|'.join(sorted(metrics_df['controller'].astype(str).unique())),
        })

    summary_df = pd.DataFrame(summary_rows).sort_values('hours').reset_index(drop=True)
    claims_out_df = pd.DataFrame(claim_rows).sort_values(['hours', 'Baseline']).reset_index(drop=True)
    catalog_df = pd.DataFrame(catalog_rows).sort_values('hours').reset_index(drop=True)

    summary_df.to_csv(output_path / 'cross_benchmark_summary.csv', index=False)
    claims_out_df.to_csv(output_path / 'cross_benchmark_claims.csv', index=False)
    catalog_df.to_csv(output_path / 'cross_benchmark_catalog.csv', index=False)
    return summary_df, claims_out_df, catalog_df


if __name__ == '__main__':
    build_cross_benchmark_outputs()
