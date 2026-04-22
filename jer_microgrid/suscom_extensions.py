from __future__ import annotations

import argparse
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import SiteConfig, SyntheticConfig
from .controllers import build_controller
from .metrics import compute_group_metrics
from .reporting import build_runtime_table
from .simulation import attach_profile_columns, simulate_controller, soc_update
from .synth import generate_dataset
from .utils import ensure_dir, save_json


plt.rcParams.update({
    'figure.dpi': 140,
    'savefig.dpi': 300,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'svg.fonttype': 'none',
})


PRIMARY_SCAN_CONTROLLERS = ['Proposed', 'GR', 'A1', 'RS']
SCAN_SECONDS = [60, 30, 10]
ROBUSTNESS_CASES = [
    {'case': 'nominal', 'drop_prob': 0.00, 'delay_ticks': 0, 'description': 'Native input stream'},
    {'case': 'drop_2pct_zoh', 'drop_prob': 0.02, 'delay_ticks': 0, 'description': '2% missing samples, hold-last-sample'},
    {'case': 'drop_5pct_zoh', 'drop_prob': 0.05, 'delay_ticks': 0, 'description': '5% missing samples, hold-last-sample'},
    {'case': 'delay_1tick', 'drop_prob': 0.00, 'delay_ticks': 1, 'description': 'One-tick delayed measurement stream'},
    {'case': 'delay_2tick', 'drop_prob': 0.00, 'delay_ticks': 2, 'description': 'Two-tick delayed measurement stream'},
]


def _profile_iterator(dataset: pd.DataFrame):
    group_cols = [col for col in ['benchmark_id', 'scenario', 'seed', 'scenario_seed'] if col in dataset.columns]
    for _, g in dataset.groupby(group_cols, sort=False):
        yield g.reset_index(drop=True)


def _run_named_controller(dataset: pd.DataFrame, controller_name: str, site: SiteConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    per_tick = []
    for profile in _profile_iterator(dataset):
        ctrl = build_controller(controller_name, site)
        sim = simulate_controller(profile, ctrl, site)
        tick = attach_profile_columns(sim.series, profile)
        for extra_col in ['benchmark_id', 'benchmark_hours']:
            if extra_col in profile.columns:
                tick[extra_col] = profile[extra_col].to_numpy()
        tick['controller'] = controller_name
        per_tick.append(tick)
    tick_df = pd.concat(per_tick, ignore_index=True)
    group_cols = [col for col in ['controller', 'benchmark_id', 'benchmark_hours', 'scenario', 'seed', 'scenario_seed', 'day_id'] if col in tick_df.columns]
    metrics_df = compute_group_metrics(tick_df, site, group_cols)
    return tick_df, metrics_df


def _measurement_corrupted_base(true_base: np.ndarray, *, drop_prob: float, delay_ticks: int, seed: int) -> np.ndarray:
    delayed = np.asarray(true_base, dtype=float).copy()
    if delay_ticks > 0:
        delayed[delay_ticks:] = delayed[:-delay_ticks]
        delayed[:delay_ticks] = delayed[0]
    if drop_prob <= 0.0:
        return delayed
    rng = np.random.default_rng(seed)
    observed = delayed.copy()
    for t in range(1, observed.size):
        if rng.random() < drop_prob:
            observed[t] = observed[t - 1]
    return observed


def _simulate_with_channel_wrapper(
    profile: pd.DataFrame,
    controller_name: str,
    site: SiteConfig,
    *,
    drop_prob: float,
    delay_ticks: int,
) -> pd.DataFrame:
    ctrl = build_controller(controller_name, site)
    ctrl.reset()

    true_base = profile['base_kw'].to_numpy(dtype=float)
    observed_base = _measurement_corrupted_base(
        true_base,
        drop_prob=drop_prob,
        delay_ticks=delay_ticks,
        seed=int(profile['seed'].iloc[0]) + 1000 * int(profile['day_id'].iloc[0]) + 100000 * int(delay_ticks) + int(drop_prob * 1000),
    )
    peak = profile['peak_flag'].to_numpy(dtype=int)
    ts = profile['timestamp'].to_numpy()
    soc = site.soc_init
    rows: list[dict[str, Any]] = []

    for t in range(len(profile)):
        history = observed_base[: t + 1]
        t0 = time.perf_counter()
        cmd, debug = ctrl.step(t, history, soc, int(peak[t]))
        cpu_ms = (time.perf_counter() - t0) * 1000.0
        grid = true_base[t] - cmd
        soc_next = soc_update(soc, cmd, site)
        rows.append({
            'timestamp': ts[t],
            'base_kw': float(true_base[t]),
            'observed_base_kw': float(observed_base[t]),
            'cmd_kw': float(cmd),
            'grid_kw': float(grid),
            'soc': float(soc),
            'soc_next': float(soc_next),
            'mode': debug.get('mode', 'IDLE'),
            'rg_state': debug.get('rg_state', 'MID'),
            'desired_kw': debug.get('desired_kw', np.nan),
            'p_imp_cap': debug.get('p_imp_cap', np.nan),
            'p_exp_cap': debug.get('p_exp_cap', np.nan),
            'e_imp': debug.get('e_imp', np.nan),
            'e_exp': debug.get('e_exp', np.nan),
            'e1_imp': debug.get('e1_imp', np.nan),
            'e1_exp': debug.get('e1_exp', np.nan),
            'cpu_ms': float(cpu_ms),
        })
        soc = soc_next
    sim_df = pd.DataFrame(rows)
    return attach_profile_columns(sim_df, profile)


def _run_channel_robustness(
    dataset: pd.DataFrame,
    controller_name: str,
    site: SiteConfig,
    *,
    drop_prob: float,
    delay_ticks: int,
    case_label: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    per_tick = []
    for profile in _profile_iterator(dataset):
        tick = _simulate_with_channel_wrapper(
            profile,
            controller_name,
            site,
            drop_prob=drop_prob,
            delay_ticks=delay_ticks,
        )
        for extra_col in ['benchmark_id', 'benchmark_hours']:
            if extra_col in profile.columns:
                tick[extra_col] = profile[extra_col].to_numpy()
        tick['controller'] = controller_name
        tick['case'] = case_label
        per_tick.append(tick)
    tick_df = pd.concat(per_tick, ignore_index=True)
    metrics_df = compute_group_metrics(tick_df, site, ['controller', 'case', 'scenario', 'seed', 'scenario_seed', 'day_id'])
    return tick_df, metrics_df


def _scaled_timebase_site(base_site: SiteConfig, scan_seconds: int) -> SiteConfig:
    step_scale = scan_seconds / 60.0
    tick_multiplier = 60.0 / scan_seconds
    return replace(
        base_site,
        ts_hours=scan_seconds / 3600.0,
        r_max_kw_per_tick=base_site.r_max_kw_per_tick * step_scale,
        d_lim=base_site.d_lim * step_scale,
        w_f=max(1, int(round(base_site.w_f * tick_multiplier))),
        w_ema=max(1, int(round(base_site.w_ema * tick_multiplier))),
        horizon_k=max(1, int(round(base_site.horizon_k * tick_multiplier))),
        t_min_ticks=max(1, int(round(base_site.t_min_ticks * tick_multiplier))),
        h_rg_ticks=max(1, int(round(base_site.h_rg_ticks * tick_multiplier))),
    )


def _load_combined_released_dataset(repo_root: Path) -> pd.DataFrame:
    blocks = []
    for benchmark_id, hours, rel_dir in [
        ('compact_6h', 6, Path('outputs_compact_full')),
        ('medium_12h', 12, Path('outputs_medium_full')),
        ('core_24h', 24, Path('outputs_24h_core_eval')),
    ]:
        dataset = pd.read_csv(repo_root / rel_dir / 'synthetic_dataset.csv')
        dataset['benchmark_id'] = benchmark_id
        dataset['benchmark_hours'] = hours
        blocks.append(dataset)
    return pd.concat(blocks, ignore_index=True)


def _runtime_row(runtime_df: pd.DataFrame, controller: str) -> pd.Series:
    return runtime_df.loc[runtime_df['Controller'] == controller].iloc[0]


def _build_scan_time_summary(outdir: Path) -> pd.DataFrame:
    base_site = SiteConfig()
    synth = SyntheticConfig(hours=24)
    rows: list[dict[str, Any]] = []

    for scan_seconds in SCAN_SECONDS:
        site = _scaled_timebase_site(base_site, scan_seconds)
        dataset = generate_dataset([0, 1], site, synth)
        interval_ms = scan_seconds * 1000.0
        for controller_name in PRIMARY_SCAN_CONTROLLERS:
            tick_df, metrics_df = _run_named_controller(dataset, controller_name, site)
            runtime_df = build_runtime_table(tick_df)
            runtime_row = _runtime_row(runtime_df, controller_name)
            metrics_mean = metrics_df.mean(numeric_only=True)
            rows.append({
                'scan_seconds': int(scan_seconds),
                'controller': controller_name,
                'profiles': int(len(metrics_df)),
                'w_f_ticks': int(site.w_f),
                'horizon_k_ticks': int(site.horizon_k),
                't_min_ticks': int(site.t_min_ticks),
                'r_max_kw_per_tick': float(site.r_max_kw_per_tick),
                'mean_cpu_ms': float(runtime_row['MeanCpuMs']),
                'median_cpu_ms': float(runtime_row['MedianCpuMs']),
                'p95_cpu_ms': float(runtime_row['P95CpuMs']),
                'max_cpu_ms': float(runtime_row['MaxCpuMs']),
                'mean_occupancy_pct': float(100.0 * runtime_row['MeanCpuMs'] / interval_ms),
                'p95_occupancy_pct': float(100.0 * runtime_row['P95CpuMs'] / interval_ms),
                'max_occupancy_pct': float(100.0 * runtime_row['MaxCpuMs'] / interval_ms),
                'mean_slack_ms': float(interval_ms - runtime_row['MeanCpuMs']),
                'ramp95_kw_per_min': float(metrics_mean['ramp95_kw_per_min']),
                'cap_violation_pct_total': float(metrics_mean['cap_violation_pct_total']),
                'throughput_kwh': float(metrics_mean['throughput_kwh']),
                'lfp_cycle_loss_pct': float(metrics_mean['lfp_cycle_loss_pct']),
                'flip_per_day': float(metrics_mean['flip_per_day']),
            })
    df = pd.DataFrame(rows).sort_values(['scan_seconds', 'controller']).reset_index(drop=True)
    df.to_csv(outdir / 'scan_time_summary.csv', index=False)
    return df


def _build_forecast_compute_summary(repo_root: Path, outdir: Path) -> pd.DataFrame:
    dataset = _load_combined_released_dataset(repo_root)
    base_site = SiteConfig()
    rows: list[dict[str, Any]] = []

    variants = [
        ('w_f', 3, replace(base_site, w_f=3)),
        ('w_f', 5, replace(base_site, w_f=5)),
        ('w_f', 7, replace(base_site, w_f=7)),
        ('horizon_k', 5, replace(base_site, horizon_k=5)),
        ('horizon_k', 10, replace(base_site, horizon_k=10)),
        ('horizon_k', 15, replace(base_site, horizon_k=15)),
    ]
    for parameter, value, site_variant in variants:
        tick_df, metrics_df = _run_named_controller(dataset, 'Proposed', site_variant)
        runtime_df = build_runtime_table(tick_df)
        runtime_row = _runtime_row(runtime_df, 'Proposed')
        metrics_mean = metrics_df.mean(numeric_only=True)
        rows.append({
            'parameter': parameter,
            'value': int(value),
            'profiles': int(len(metrics_df)),
            'mean_cpu_ms': float(runtime_row['MeanCpuMs']),
            'median_cpu_ms': float(runtime_row['MedianCpuMs']),
            'p95_cpu_ms': float(runtime_row['P95CpuMs']),
            'max_cpu_ms': float(runtime_row['MaxCpuMs']),
            'ramp95_kw_per_min': float(metrics_mean['ramp95_kw_per_min']),
            'cap_violation_pct_total': float(metrics_mean['cap_violation_pct_total']),
            'throughput_kwh': float(metrics_mean['throughput_kwh']),
            'lfp_cycle_loss_pct': float(metrics_mean['lfp_cycle_loss_pct']),
        })
    df = pd.DataFrame(rows).sort_values(['parameter', 'value']).reset_index(drop=True)
    df.to_csv(outdir / 'forecast_compute_summary.csv', index=False)
    return df


def _build_robustness_summary(outdir: Path) -> pd.DataFrame:
    site = SiteConfig()
    synth = SyntheticConfig(hours=24)
    dataset = generate_dataset([0, 1], site, synth)
    rows: list[dict[str, Any]] = []

    for case in ROBUSTNESS_CASES:
        tick_df, metrics_df = _run_channel_robustness(
            dataset,
            'Proposed',
            site,
            drop_prob=float(case['drop_prob']),
            delay_ticks=int(case['delay_ticks']),
            case_label=str(case['case']),
        )
        runtime_df = build_runtime_table(tick_df)
        runtime_row = _runtime_row(runtime_df, 'Proposed')
        metrics_mean = metrics_df.mean(numeric_only=True)
        rows.append({
            'case': str(case['case']),
            'description': str(case['description']),
            'profiles': int(len(metrics_df)),
            'drop_prob': float(case['drop_prob']),
            'delay_ticks': int(case['delay_ticks']),
            'mean_cpu_ms': float(runtime_row['MeanCpuMs']),
            'median_cpu_ms': float(runtime_row['MedianCpuMs']),
            'p95_cpu_ms': float(runtime_row['P95CpuMs']),
            'max_cpu_ms': float(runtime_row['MaxCpuMs']),
            'ramp95_kw_per_min': float(metrics_mean['ramp95_kw_per_min']),
            'cap_violation_pct_total': float(metrics_mean['cap_violation_pct_total']),
            'throughput_kwh': float(metrics_mean['throughput_kwh']),
            'lfp_cycle_loss_pct': float(metrics_mean['lfp_cycle_loss_pct']),
            'flip_per_day': float(metrics_mean['flip_per_day']),
        })
    df = pd.DataFrame(rows).sort_values('case').reset_index(drop=True)
    df.to_csv(outdir / 'robustness_summary.csv', index=False)
    return df


def _build_ultralight_summary(repo_root: Path, outdir: Path) -> pd.DataFrame:
    site = SiteConfig()
    dataset = pd.read_csv(repo_root / 'outputs_24h_core_eval' / 'synthetic_dataset.csv')
    metrics_blocks = []
    runtime_blocks = []
    for controller_name in ['Proposed', 'GR', 'RS', 'A1']:
        tick_df, metrics_df = _run_named_controller(dataset, controller_name, site)
        label = 'A1_no_forecast' if controller_name == 'A1' else controller_name
        metrics_df = metrics_df.copy()
        metrics_df['controller'] = label
        runtime_df = build_runtime_table(tick_df)
        runtime_df['Controller'] = label
        metrics_blocks.append(metrics_df)
        runtime_blocks.append(runtime_df)
    metrics_df = pd.concat(metrics_blocks, ignore_index=True)
    runtime_df = pd.concat(runtime_blocks, ignore_index=True)

    rows: list[dict[str, Any]] = []
    for controller, g in metrics_df.groupby('controller', sort=False):
        runtime_row = _runtime_row(runtime_df, controller)
        rows.append({
            'controller': str(controller),
            'profiles': int(len(g)),
            'mean_cpu_ms': float(runtime_row['MeanCpuMs']),
            'median_cpu_ms': float(runtime_row['MedianCpuMs']),
            'p95_cpu_ms': float(runtime_row['P95CpuMs']),
            'max_cpu_ms': float(runtime_row['MaxCpuMs']),
            'ramp95_kw_per_min': float(g['ramp95_kw_per_min'].mean()),
            'cap_violation_pct_total': float(g['cap_violation_pct_total'].mean()),
            'throughput_kwh': float(g['throughput_kwh'].mean()),
            'lfp_cycle_loss_pct': float(g['lfp_cycle_loss_pct'].mean()),
            'flip_per_day': float(g['flip_per_day'].mean()),
        })
    df = pd.DataFrame(rows).sort_values('controller').reset_index(drop=True)
    df.to_csv(outdir / 'ultralight_baseline_summary.csv', index=False)
    return df


def _build_state_summary(outdir: Path) -> pd.DataFrame:
    site = SiteConfig()
    rows = [
        {'component': 'Base history ring buffer', 'type': 'rolling buffer', 'count': int(site.w_f + 1), 'notes': 'Samples needed to reproduce moving-average and trend terms'},
        {'component': 'Forecast scratch buffer', 'type': 'ephemeral array', 'count': int(site.horizon_k), 'notes': 'Short-horizon base forecast values'},
        {'component': 'Previous command', 'type': 'persistent scalar', 'count': 1, 'notes': 'Used for step clipping and action hold'},
        {'component': 'Previous mode label', 'type': 'persistent enum', 'count': 1, 'notes': 'PS / VF / PREP_CH / PREP_DIS / IDLE'},
        {'component': 'Reserve label', 'type': 'persistent enum', 'count': 1, 'notes': 'LOW / MID / HIGH'},
        {'component': 'Dwell counter', 'type': 'persistent integer', 'count': 1, 'notes': 'Supports bounded short action-hold logic'},
    ]
    df = pd.DataFrame(rows)
    df.to_csv(outdir / 'controller_state_summary.csv', index=False)
    return df


def _plot_scan_time_runtime(df: pd.DataFrame, output_path: Path) -> None:
    keep = df[df['controller'].isin(['Proposed', 'GR', 'A1', 'RS'])].copy()
    if keep.empty:
        return
    ensure_dir(output_path.parent)
    color_map = {'Proposed': '#0a5c36', 'GR': '#4f6d7a', 'A1': '#005f99', 'RS': '#c97b00'}
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.4))
    for controller, g in keep.groupby('controller', sort=False):
        g = g.sort_values('scan_seconds')
        label = 'A1 no-forecast' if controller == 'A1' else controller
        axes[0].plot(g['scan_seconds'], g['mean_cpu_ms'], marker='o', linewidth=1.8, color=color_map.get(controller, '#333333'), label=label)
        axes[1].plot(g['scan_seconds'], g['mean_occupancy_pct'], marker='o', linewidth=1.8, color=color_map.get(controller, '#333333'), label=label)
    axes[0].set_xlabel('Scan interval (s)')
    axes[0].set_ylabel('Mean runtime (ms/tick)')
    axes[0].set_title('Measured runtime vs scan interval')
    axes[1].set_xlabel('Scan interval (s)')
    axes[1].set_ylabel('Mean occupancy of tick budget (%)')
    axes[1].set_title('Runtime occupancy vs scan interval')
    axes[0].invert_xaxis()
    axes[1].invert_xaxis()
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _plot_scan_time_tradeoff(df: pd.DataFrame, output_path: Path) -> None:
    keep = df[df['controller'].isin(['Proposed', 'GR', 'A1', 'RS'])].copy()
    if keep.empty:
        return
    ensure_dir(output_path.parent)
    color_map = {60: '#0a5c36', 30: '#005f99', 10: '#c97b00'}
    marker_map = {'Proposed': 'o', 'GR': 's', 'A1': '^', 'RS': 'D'}
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    for _, row in keep.iterrows():
        label = f"{row['controller']} @ {int(row['scan_seconds'])} s"
        ax.scatter(row['ramp95_kw_per_min'], row['throughput_kwh'], s=55, marker=marker_map.get(str(row['controller']), 'o'), color=color_map.get(int(row['scan_seconds']), '#333333'))
        ax.annotate(label, (row['ramp95_kw_per_min'], row['throughput_kwh']), textcoords='offset points', xytext=(4, 4), fontsize=7)
    ax.set_xlabel('Ramp95 (kW/min)')
    ax.set_ylabel('Throughput (kWh)')
    ax.set_title('Scan-time extension: application trade-off')
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _plot_forecast_compute(df: pd.DataFrame, output_path: Path) -> None:
    if df.empty:
        return
    ensure_dir(output_path.parent)
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2))
    for ax, parameter, title in [
        (axes[0], 'w_f', 'Forecast window sensitivity'),
        (axes[1], 'horizon_k', 'Forecast horizon sensitivity'),
    ]:
        g = df[df['parameter'] == parameter].sort_values('value')
        ax.plot(g['value'], g['mean_cpu_ms'], marker='o', linewidth=1.8, color='#0a5c36', label='Mean runtime')
        ax.plot(g['value'], g['p95_cpu_ms'], marker='s', linewidth=1.2, color='#005f99', label='p95 runtime')
        ax.set_xlabel(parameter)
        ax.set_ylabel('Runtime (ms/tick)')
        ax.set_title(title)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _plot_robustness(df: pd.DataFrame, output_path: Path) -> None:
    if df.empty:
        return
    keep = df.copy()
    ensure_dir(output_path.parent)
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2))
    axes[0].bar(keep['case'], keep['cap_violation_pct_total'], color=['#0a5c36', '#6aa84f', '#93c47d', '#3d85c6', '#6fa8dc'])
    axes[0].set_ylabel('Cap violation (%)')
    axes[0].set_title('Measurement-wrapper robustness')
    axes[0].tick_params(axis='x', rotation=20)
    axes[1].plot(keep['case'], keep['throughput_kwh'], marker='o', linewidth=1.8, color='#0a5c36', label='Throughput')
    axes[1].plot(keep['case'], keep['ramp95_kw_per_min'], marker='s', linewidth=1.4, color='#c97b00', label='Ramp95')
    axes[1].tick_params(axis='x', rotation=20)
    axes[1].set_title('Robustness: throughput and ramp response')
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _plot_ultralight(df: pd.DataFrame, output_path: Path) -> None:
    if df.empty:
        return
    ensure_dir(output_path.parent)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    colors = {'Proposed': '#0a5c36', 'GR': '#4f6d7a', 'A1_no_forecast': '#005f99', 'RS': '#c97b00'}
    for _, row in df.iterrows():
        ax.scatter(row['mean_cpu_ms'], row['throughput_kwh'], s=65, color=colors.get(str(row['controller']), '#333333'))
        ax.annotate(str(row['controller']), (row['mean_cpu_ms'], row['throughput_kwh']), textcoords='offset points', xytext=(4, 4), fontsize=8)
    ax.set_xlabel('Mean runtime (ms/tick)')
    ax.set_ylabel('Throughput (kWh)')
    ax.set_title('Ultra-light baseline runtime vs cycling burden')
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _render_extension_md(
    scan_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    robustness_df: pd.DataFrame,
    ultralight_df: pd.DataFrame,
    state_df: pd.DataFrame,
) -> str:
    lines = ['# SUSCOM Extension Experiments', '']
    lines.append('## Completed extensions')
    lines.append('')
    lines.append('- Scan-time sensitivity at 60 s / 30 s / 10 s using physically rescaled tick parameters.')
    lines.append('- Forecast-window and horizon sensitivity from the compute-load angle on the released combined benchmark.')
    lines.append('- Missing-sample and delayed-sample robustness using an external hold-last-sample measurement wrapper.')
    lines.append('- Ultra-light baseline consolidation using GR, no-forecast A1, and RS already present in the released artifact.')
    lines.append('')
    lines.append('## Not completed')
    lines.append('')
    lines.append('- Edge-device / low-power hardware target test: no embedded target, PLC runtime, or HIL platform is present in the repository.')
    lines.append('')
    for title, df in [
        ('Scan-time summary', scan_df),
        ('Forecast/runtime sensitivity', forecast_df),
        ('Measurement-wrapper robustness', robustness_df),
        ('Ultra-light baseline summary', ultralight_df),
        ('Controller fixed-memory summary', state_df),
    ]:
        lines.append(f'## {title}')
        lines.append('')
        lines.append(_df_to_markdown(df))
        lines.append('')
    return '\n'.join(lines)


def _df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return '_empty_'
    cols = list(df.columns)
    header = '| ' + ' | '.join(str(c) for c in cols) + ' |'
    sep = '| ' + ' | '.join('---' for _ in cols) + ' |'
    body = ['| ' + ' | '.join(str(row[c]) for c in cols) + ' |' for _, row in df.iterrows()]
    return '\n'.join([header, sep] + body)


def run_suscom_extensions(output_dir: str | Path = 'outputs_suscom_extensions') -> dict[str, pd.DataFrame]:
    repo_root = Path.cwd()
    outdir = ensure_dir(repo_root / output_dir)
    figdir = ensure_dir(outdir / 'fig')

    scan_df = _build_scan_time_summary(outdir)
    forecast_df = _build_forecast_compute_summary(repo_root, outdir)
    robustness_df = _build_robustness_summary(outdir)
    ultralight_df = _build_ultralight_summary(repo_root, outdir)
    state_df = _build_state_summary(outdir)

    _plot_scan_time_runtime(scan_df, figdir / 'scan_time_runtime.pdf')
    _plot_scan_time_tradeoff(scan_df, figdir / 'scan_time_tradeoff.pdf')
    _plot_forecast_compute(forecast_df, figdir / 'forecast_compute_runtime.pdf')
    _plot_robustness(robustness_df, figdir / 'measurement_wrapper_robustness.pdf')
    _plot_ultralight(ultralight_df, figdir / 'ultralight_runtime_tradeoff.pdf')

    extension_md = _render_extension_md(scan_df, forecast_df, robustness_df, ultralight_df, state_df)
    (outdir / 'suscom_extension_report.md').write_text(extension_md, encoding='utf-8')

    save_json(outdir / 'run_manifest.json', {
        'scan_seconds': SCAN_SECONDS,
        'scan_controllers': PRIMARY_SCAN_CONTROLLERS,
        'robustness_cases': ROBUSTNESS_CASES,
        'completed': [
            'scan_time_sensitivity',
            'forecast_compute_sensitivity',
            'measurement_wrapper_robustness',
            'ultralight_baseline_summary',
            'controller_state_summary',
        ],
        'not_completed': [
            'edge_device_or_low_power_hardware_target_test',
        ],
    })

    return {
        'scan_df': scan_df,
        'forecast_df': forecast_df,
        'robustness_df': robustness_df,
        'ultralight_df': ultralight_df,
        'state_df': state_df,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Run supplementary SUSCOM-oriented extension experiments.')
    parser.add_argument('--output-dir', type=str, default='outputs_suscom_extensions')
    args = parser.parse_args()
    run_suscom_extensions(args.output_dir)


if __name__ == '__main__':
    main()
