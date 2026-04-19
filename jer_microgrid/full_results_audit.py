from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .reporting import dataframe_to_latex_table
from .utils import ensure_dir


plt.rcParams.update({
    'figure.dpi': 140,
    'savefig.dpi': 300,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'svg.fonttype': 'none',
})


PRIMARY_RUNS = ('outputs_compact_full', 'outputs_medium_full', 'outputs_24h_core_eval')
DERIVED_RUNS = ('outputs_cross_benchmark_evidence', 'outputs_parameter_audit')


def _iter_result_dirs(repo_root: Path, *, excluded_names: set[str] | None = None) -> list[Path]:
    excluded_names = excluded_names or set()
    dirs = []
    for path in repo_root.iterdir():
        if not path.is_dir():
            continue
        if path.name in excluded_names:
            continue
        if path.name.startswith(('outputs_', 'review_', 'publication_smoke')):
            dirs.append(path)
    return sorted(dirs, key=lambda p: p.name.lower())


def _maybe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _load_manifest(path: Path) -> dict[str, Any]:
    manifest_path = path / 'run_manifest.json'
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text(encoding='utf-8'))


def _metric_means_by_controller(path: Path) -> dict[str, dict[str, float]]:
    metrics_path = path / 'main_metrics_by_scenario_day.csv'
    if not metrics_path.exists():
        return {}
    metrics_df = pd.read_csv(metrics_path)
    out: dict[str, dict[str, float]] = {}
    for controller, g in metrics_df.groupby('controller', sort=False):
        out[str(controller)] = {
            key: float(value)
            for key, value in g.mean(numeric_only=True).to_dict().items()
        }
    return out


def _classify_result_dir(name: str) -> tuple[str, str]:
    if name in PRIMARY_RUNS:
        return 'primary_postfix', 'Independent benchmark evidence'
    if name == 'outputs_24h_eval':
        return 'incomplete', 'Discarded incomplete early run'
    if name == 'outputs_24h_eval_retry':
        return 'redundant_retry', 'Redundant 24 h retry / regression evidence'
    if name in DERIVED_RUNS:
        return 'derived_audit', 'Derived audit / secondary evidence'
    if name.startswith(('review_', 'publication_smoke')):
        return 'smoke_regression', 'Smoke / regression verification'
    return 'other', 'Unclassified'


def _safe_len(value: Any) -> int:
    if isinstance(value, (list, tuple)):
        return len(value)
    return 0


def _summarize_result_dir(path: Path) -> dict[str, Any]:
    manifest = _load_manifest(path)
    metric_means = _metric_means_by_controller(path)
    runtime_df = _maybe_read_csv(path / 'runtime_summary.csv')
    claims_df = _maybe_read_csv(path / 'claims_by_scenario.csv')
    publication_sel = path / 'publication' / 'publication_selection.json'
    publication_data = {}
    if publication_sel.exists():
        publication_data = json.loads(publication_sel.read_text(encoding='utf-8'))

    synth = manifest.get('synthetic', {})
    exp = manifest.get('experiment', {})
    hours = synth.get('hours', manifest.get('hours'))
    scenarios = synth.get('scenario_names', manifest.get('scenario_names', []))
    seeds = exp.get('seeds', manifest.get('seeds', []))
    proposed_units = 0
    metrics_df = _maybe_read_csv(path / 'main_metrics_by_scenario_day.csv')
    if not metrics_df.empty and 'controller' in metrics_df.columns:
        proposed_units = int((metrics_df['controller'] == 'Proposed').sum())

    proposed = metric_means.get('Proposed', {})
    gr = metric_means.get('GR', {})
    rs = metric_means.get('RS', {})
    fbrl = metric_means.get('FBRL', {})
    nc = metric_means.get('NC', {})
    mpc = metric_means.get('MPC_ref', metric_means.get('MPC_best_balanced', {}))

    proposed_cpu = float('nan')
    mpc_cpu = float('nan')
    if not runtime_df.empty:
        if 'Controller' in runtime_df.columns:
            proposed_row = runtime_df[runtime_df['Controller'] == 'Proposed']
            if not proposed_row.empty:
                proposed_cpu = float(proposed_row.iloc[0]['MeanCpuMs'])
            mpc_row = runtime_df[runtime_df['Controller'].isin(['MPC_ref', 'MPC_best_balanced', 'MPC_best_ramp'])]
            if not mpc_row.empty:
                mpc_cpu = float(mpc_row.iloc[0]['MeanCpuMs'])

    publication_holdout_valid = publication_data.get('holdout_valid')
    if publication_holdout_valid is None and path.name.startswith(('review_', 'publication_smoke')) and _safe_len(seeds) <= 1:
        publication_holdout_valid = False

    category, evidence_role = _classify_result_dir(path.name)
    return {
        'result_dir': path.name,
        'category': category,
        'evidence_role': evidence_role,
        'hours': hours,
        'scenario_count': _safe_len(scenarios),
        'seed_count': _safe_len(seeds),
        'profiles': proposed_units,
        'file_count': sum(1 for p in path.rglob('*') if p.is_file()),
        'has_manifest': bool(manifest),
        'has_main_metrics': bool(metric_means),
        'has_runtime': (path / 'runtime_summary.csv').exists(),
        'has_publication': (path / 'publication').exists(),
        'has_figures': (path / 'fig').exists() or (path / 'figures').exists(),
        'has_claims_by_scenario': not claims_df.empty,
        'publication_holdout_valid': publication_holdout_valid,
        'proposed_ramp95': proposed.get('ramp95_kw_per_min'),
        'proposed_cap_violation_pct': proposed.get('cap_violation_pct_total'),
        'proposed_throughput_kwh': proposed.get('throughput_kwh'),
        'proposed_lfp_cycle_loss_pct': proposed.get('lfp_cycle_loss_pct'),
        'gr_ramp95': gr.get('ramp95_kw_per_min'),
        'gr_cap_violation_pct': gr.get('cap_violation_pct_total'),
        'gr_throughput_kwh': gr.get('throughput_kwh'),
        'gr_lfp_cycle_loss_pct': gr.get('lfp_cycle_loss_pct'),
        'rs_throughput_kwh': rs.get('throughput_kwh'),
        'rs_lfp_cycle_loss_pct': rs.get('lfp_cycle_loss_pct'),
        'fbrl_throughput_kwh': fbrl.get('throughput_kwh'),
        'fbrl_lfp_cycle_loss_pct': fbrl.get('lfp_cycle_loss_pct'),
        'nc_cap_violation_pct': nc.get('cap_violation_pct_total'),
        'mpc_ramp95': mpc.get('ramp95_kw_per_min'),
        'mpc_cap_violation_pct': mpc.get('cap_violation_pct_total'),
        'mpc_lfp_cycle_loss_pct': mpc.get('lfp_cycle_loss_pct'),
        'proposed_mean_cpu_ms': proposed_cpu,
        'mpc_mean_cpu_ms': mpc_cpu,
    }


def _add_signature_groups(catalog_df: pd.DataFrame) -> pd.DataFrame:
    sig_cols = [
        'hours', 'scenario_count', 'seed_count', 'profiles',
        'proposed_ramp95', 'proposed_cap_violation_pct', 'proposed_throughput_kwh',
        'proposed_lfp_cycle_loss_pct', 'gr_throughput_kwh', 'gr_lfp_cycle_loss_pct',
        'rs_throughput_kwh', 'rs_lfp_cycle_loss_pct', 'fbrl_throughput_kwh', 'fbrl_lfp_cycle_loss_pct',
    ]
    signature = (
        catalog_df[sig_cols]
        .fillna('NA')
        .astype(str)
        .agg('|'.join, axis=1)
    )
    codes, _ = pd.factorize(signature)
    catalog_df = catalog_df.copy()
    catalog_df['signature_group'] = codes + 1
    return catalog_df


def _build_primary_controller_summary(repo_root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for run_name in PRIMARY_RUNS:
        run_dir = repo_root / run_name
        manifest = _load_manifest(run_dir)
        hours = int(manifest.get('synthetic', {}).get('hours', 0))
        metrics_df = _maybe_read_csv(run_dir / 'main_metrics_by_scenario_day.csv')
        if metrics_df.empty:
            continue
        for controller, g in metrics_df.groupby('controller', sort=False):
            if controller not in {'Proposed', 'GR', 'NC', 'RS', 'FBRL', 'MPC_ref', 'MPC_best_balanced'}:
                continue
            rows.append({
                'benchmark_id': run_name,
                'hours': hours,
                'controller': str(controller),
                'ramp95_kw_per_min': float(g['ramp95_kw_per_min'].mean()),
                'cap_violation_pct_total': float(g['cap_violation_pct_total'].mean()),
                'throughput_kwh': float(g['throughput_kwh'].mean()),
                'lfp_cycle_loss_pct': float(g['lfp_cycle_loss_pct'].mean()),
            })
    return pd.DataFrame(rows).sort_values(['hours', 'controller']).reset_index(drop=True)


def _build_primary_evidence_summary(catalog_df: pd.DataFrame) -> pd.DataFrame:
    df = catalog_df[catalog_df['category'] == 'primary_postfix'].copy()
    if df.empty:
        return df
    df['throughput_vs_gr_delta_kwh'] = df['proposed_throughput_kwh'] - df['gr_throughput_kwh']
    df['lfp_cycle_loss_vs_gr_delta_pctpt'] = df['proposed_lfp_cycle_loss_pct'] - df['gr_lfp_cycle_loss_pct']
    df['throughput_reduction_vs_rs_pct'] = 100.0 * (1.0 - df['proposed_throughput_kwh'] / df['rs_throughput_kwh'])
    df['throughput_reduction_vs_fbrl_pct'] = 100.0 * (1.0 - df['proposed_throughput_kwh'] / df['fbrl_throughput_kwh'])
    df['lfp_cycle_loss_reduction_vs_rs_pct'] = 100.0 * (1.0 - df['proposed_lfp_cycle_loss_pct'] / df['rs_lfp_cycle_loss_pct'])
    df['lfp_cycle_loss_reduction_vs_fbrl_pct'] = 100.0 * (1.0 - df['proposed_lfp_cycle_loss_pct'] / df['fbrl_lfp_cycle_loss_pct'])
    df['cap_gain_vs_nc_pctpt'] = df['nc_cap_violation_pct'] - df['proposed_cap_violation_pct']
    df['cpu_speedup_vs_mpc'] = df['mpc_mean_cpu_ms'] / df['proposed_mean_cpu_ms']
    keep = [
        'result_dir', 'hours', 'profiles', 'proposed_ramp95', 'proposed_cap_violation_pct',
        'proposed_throughput_kwh', 'proposed_lfp_cycle_loss_pct',
        'gr_throughput_kwh', 'gr_lfp_cycle_loss_pct', 'throughput_vs_gr_delta_kwh',
        'lfp_cycle_loss_vs_gr_delta_pctpt',
        'throughput_reduction_vs_rs_pct', 'throughput_reduction_vs_fbrl_pct',
        'lfp_cycle_loss_reduction_vs_rs_pct', 'lfp_cycle_loss_reduction_vs_fbrl_pct',
        'cap_gain_vs_nc_pctpt', 'cpu_speedup_vs_mpc',
    ]
    return df[keep].sort_values('hours').reset_index(drop=True)


def _build_smoke_regression_summary(catalog_df: pd.DataFrame) -> pd.DataFrame:
    keep_df = catalog_df[catalog_df['category'].isin(['smoke_regression', 'redundant_retry'])].copy()
    if keep_df.empty:
        return keep_df
    cols = [
        'result_dir', 'category', 'signature_group', 'hours', 'seed_count',
        'has_runtime', 'has_publication', 'publication_holdout_valid',
        'proposed_ramp95', 'proposed_cap_violation_pct', 'proposed_throughput_kwh',
    ]
    return keep_df[cols].sort_values(['category', 'result_dir']).reset_index(drop=True)


def _build_results_overview(catalog_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for category, g in catalog_df.groupby('category', sort=False):
        rows.append({
            'Category': category,
            'Directories': int(len(g)),
            'Examples': ', '.join(g['result_dir'].head(3).tolist()),
            'Role': str(g['evidence_role'].iloc[0]),
        })
    return pd.DataFrame(rows)


def _build_parameter_top_table(repo_root: Path) -> pd.DataFrame:
    path = repo_root / 'outputs_parameter_audit' / 'candidate_stability_summary.csv'
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    keep = [
        'candidate', 'base_soft_low', 'prep_power_cap_kw', 'lookahead_gain', 'min_useful_cmd_kw',
        'mean_hold_score_vs_gr', 'std_hold_score_vs_gr', 'mean_hold_rank',
        'mean_hold_cap_delta_vs_gr', 'mean_hold_throughput_delta_vs_gr',
    ]
    return df[keep].head(8).reset_index(drop=True)


def _plot_cross_benchmark_tradeoff(controller_df: pd.DataFrame, output_path: Path) -> None:
    if controller_df.empty:
        return
    ensure_dir(output_path.parent)
    color_map = {
        'Proposed': '#0a5c36',
        'GR': '#4f6d7a',
        'NC': '#8c3d3d',
        'RS': '#c97b00',
        'FBRL': '#7a3ea1',
        'MPC_ref': '#005f99',
        'MPC_best_balanced': '#005f99',
    }
    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    for controller, g in controller_df.groupby('controller', sort=False):
        g = g.sort_values('hours')
        color = color_map.get(controller, '#333333')
        ax.plot(g['ramp95_kw_per_min'], g['throughput_kwh'], marker='o', linewidth=1.6, color=color, label=controller)
        for _, row in g.iterrows():
            ax.annotate(f"{int(row['hours'])} h", (row['ramp95_kw_per_min'], row['throughput_kwh']),
                        textcoords='offset points', xytext=(4, 4), fontsize=7, color=color)
    ax.set_xlabel('Ramp95 (kW/min)')
    ax.set_ylabel('Throughput (kWh)')
    ax.set_title('Cross-benchmark trade-off across all independent tiers')
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _plot_runtime_speedup(primary_df: pd.DataFrame, output_path: Path) -> None:
    if primary_df.empty:
        return
    ensure_dir(output_path.parent)
    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    labels = [f"{int(h)} h" for h in primary_df['hours']]
    ax.bar(labels, primary_df['cpu_speedup_vs_mpc'], color=['#6c8ebf', '#93c47d', '#e69138'])
    ax.set_ylabel('MPC / Proposed speedup')
    ax.set_title('Runtime gap preserved across independent benchmarks')
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _plot_cycle_life_loss(controller_df: pd.DataFrame, output_path: Path) -> None:
    if controller_df.empty:
        return
    keep = controller_df[controller_df['controller'].isin(['Proposed', 'GR', 'RS', 'FBRL', 'MPC_ref', 'MPC_best_balanced'])].copy()
    if keep.empty:
        return
    ensure_dir(output_path.parent)
    color_map = {
        'Proposed': '#0a5c36',
        'GR': '#4f6d7a',
        'RS': '#c97b00',
        'FBRL': '#7a3ea1',
        'MPC_ref': '#005f99',
        'MPC_best_balanced': '#005f99',
    }
    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    for controller, g in keep.groupby('controller', sort=False):
        g = g.sort_values('hours')
        color = color_map.get(controller, '#333333')
        ax.plot(g['hours'], g['lfp_cycle_loss_pct'], marker='o', linewidth=1.8, color=color, label=controller)
    ax.set_xlabel('Benchmark horizon (h)')
    ax.set_ylabel('Modeled LFP cycle-life loss (%)')
    ax.set_title('Chemistry-calibrated cycling life loss across independent tiers')
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _plot_claim_heatmap(repo_root: Path, output_path: Path) -> None:
    rows = []
    for run_name in PRIMARY_RUNS:
        claims_path = repo_root / run_name / 'claims_by_scenario.csv'
        if not claims_path.exists():
            continue
        claims_df = pd.read_csv(claims_path)
        if claims_df.empty:
            continue
        claims_df['nonworse_rate'] = claims_df['all4_nonworse_count'] / claims_df['Pairs']
        rows.append(claims_df[['Scenario', 'Baseline', 'all4_nonworse_count', 'Pairs']])
    if not rows:
        return
    combined = pd.concat(rows, ignore_index=True)
    agg = combined.groupby(['Scenario', 'Baseline'], as_index=False).sum(numeric_only=True)
    agg['nonworse_rate'] = agg['all4_nonworse_count'] / agg['Pairs']
    pivot = agg.pivot(index='Scenario', columns='Baseline', values='nonworse_rate').fillna(0.0)
    ensure_dir(output_path.parent)
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    im = ax.imshow(pivot.to_numpy(dtype=float), aspect='auto', vmin=0.0, vmax=1.0, cmap='YlGn')
    ax.set_xticks(range(pivot.shape[1]))
    ax.set_xticklabels([str(c) for c in pivot.columns], rotation=20)
    ax.set_yticks(range(pivot.shape[0]))
    ax.set_yticklabels([str(i) for i in pivot.index])
    ax.set_title('Scenario-wise non-worse rate across all independent runs')
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.iloc[i, j]:.2f}", ha='center', va='center', fontsize=7)
    fig.colorbar(im, ax=ax, label='All-4 non-worse fraction')
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _plot_parameter_plateau(repo_root: Path, output_path: Path) -> None:
    group_path = repo_root / 'outputs_parameter_audit' / 'candidate_param_group_summary.csv'
    if not group_path.exists():
        return
    group_df = pd.read_csv(group_path)
    if group_df.empty:
        return
    ensure_dir(output_path.parent)
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.2))
    for ax, parameter, title in [
        (axes[0], 'base_soft_low', 'Reserve anchor sweep'),
        (axes[1], 'prep_power_cap_kw', 'Preparation-cap sweep'),
    ]:
        g = group_df[group_df['parameter'] == parameter].sort_values('value')
        ax.plot(g['value'], g['mean_hold_score_vs_gr'], marker='o', color='#0a5c36')
        ax.set_xlabel(parameter)
        ax.set_ylabel('Mean hold score vs GR')
        ax.set_title(title)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _render_audit_md(*, catalog_df: pd.DataFrame, overview_df: pd.DataFrame,
                     primary_df: pd.DataFrame, smoke_df: pd.DataFrame,
                     parameter_df: pd.DataFrame) -> str:
    lines = ['# Full Results Audit', '']
    lines.append('## Directory Roles')
    lines.append('')
    lines.append(_df_to_markdown(overview_df))
    lines.append('')
    lines.append('## Primary Benchmark Summary')
    lines.append('')
    lines.append(_df_to_markdown(primary_df))
    lines.append('')
    lines.append('## Smoke / Regression Summary')
    lines.append('')
    lines.append(_df_to_markdown(smoke_df))
    lines.append('')
    lines.append('## Parameter Stability Top-8')
    lines.append('')
    lines.append(_df_to_markdown(parameter_df))
    lines.append('')
    lines.append('## Full Catalog')
    lines.append('')
    lines.append(_df_to_markdown(catalog_df))
    return '\n'.join(lines)


def _df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return '_empty_'
    cols = list(df.columns)
    header = '| ' + ' | '.join(str(c) for c in cols) + ' |'
    sep = '| ' + ' | '.join('---' for _ in cols) + ' |'
    body = []
    for _, row in df.iterrows():
        body.append('| ' + ' | '.join(str(row[c]) for c in cols) + ' |')
    return '\n'.join([header, sep] + body)


def run_full_results_audit(output_dir: str | Path = 'outputs_full_results_audit') -> dict[str, pd.DataFrame]:
    repo_root = Path.cwd()
    outdir = ensure_dir(repo_root / output_dir)
    figdir = ensure_dir(outdir / 'fig')

    catalog_rows = [
        _summarize_result_dir(path)
        for path in _iter_result_dirs(repo_root, excluded_names={Path(output_dir).name})
    ]
    catalog_df = pd.DataFrame(catalog_rows).sort_values('result_dir').reset_index(drop=True)
    catalog_df = _add_signature_groups(catalog_df)

    primary_summary_df = _build_primary_evidence_summary(catalog_df)
    smoke_summary_df = _build_smoke_regression_summary(catalog_df)
    overview_df = _build_results_overview(catalog_df)
    parameter_top_df = _build_parameter_top_table(repo_root)
    controller_summary_df = _build_primary_controller_summary(repo_root)

    catalog_df.to_csv(outdir / 'results_directory_catalog.csv', index=False)
    primary_summary_df.to_csv(outdir / 'primary_benchmark_summary.csv', index=False)
    smoke_summary_df.to_csv(outdir / 'smoke_regression_summary.csv', index=False)
    overview_df.to_csv(outdir / 'results_overview.csv', index=False)
    parameter_top_df.to_csv(outdir / 'parameter_stability_top.csv', index=False)
    controller_summary_df.to_csv(outdir / 'primary_controller_tradeoff.csv', index=False)

    (outdir / 'results_directory_catalog.tex').write_text(
        dataframe_to_latex_table(catalog_df, 'Full results-directory catalog.', 'tab:results_catalog_auto'),
        encoding='utf-8',
    )
    (outdir / 'primary_benchmark_summary.tex').write_text(
        dataframe_to_latex_table(primary_summary_df, 'Primary independent benchmark summary.', 'tab:primary_summary_auto'),
        encoding='utf-8',
    )
    (outdir / 'smoke_regression_summary.tex').write_text(
        dataframe_to_latex_table(smoke_summary_df, 'Smoke and regression summary.', 'tab:smoke_summary_auto'),
        encoding='utf-8',
    )
    (outdir / 'parameter_stability_top.tex').write_text(
        dataframe_to_latex_table(parameter_top_df, 'Top parameter-stability candidates.', 'tab:param_top_auto'),
        encoding='utf-8',
    )

    _plot_cross_benchmark_tradeoff(controller_summary_df, figdir / 'cross_benchmark_tradeoff.pdf')
    _plot_runtime_speedup(primary_summary_df, figdir / 'runtime_speedup.pdf')
    _plot_cycle_life_loss(controller_summary_df, figdir / 'cross_benchmark_cycle_loss.pdf')
    _plot_claim_heatmap(repo_root, figdir / 'scenario_nonworse_heatmap.pdf')
    _plot_parameter_plateau(repo_root, figdir / 'parameter_plateau.pdf')

    audit_md = _render_audit_md(
        catalog_df=catalog_df,
        overview_df=overview_df,
        primary_df=primary_summary_df,
        smoke_df=smoke_summary_df,
        parameter_df=parameter_top_df,
    )
    (outdir / 'full_results_audit.md').write_text(audit_md, encoding='utf-8')
    return {
        'catalog_df': catalog_df,
        'primary_summary_df': primary_summary_df,
        'smoke_summary_df': smoke_summary_df,
        'overview_df': overview_df,
        'parameter_top_df': parameter_top_df,
        'controller_summary_df': controller_summary_df,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Build a full audit over every results directory.')
    parser.add_argument('--output-dir', type=str, default='outputs_full_results_audit')
    args = parser.parse_args()
    run_full_results_audit(args.output_dir)


if __name__ == '__main__':
    main()
