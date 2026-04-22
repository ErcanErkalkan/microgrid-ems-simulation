from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from .full_results_audit import (
    _build_primary_controller_summary,
    _plot_claim_heatmap,
    _plot_cross_benchmark_tradeoff,
    _plot_cycle_life_loss,
    _plot_parameter_plateau,
    _plot_runtime_speedup,
)
from .plotting import save_metric_boxplot, save_ramp_cdf, save_representative_timeseries
from .suscom_extensions import (
    _plot_forecast_compute,
    _plot_robustness,
    _plot_scan_time_runtime,
    _plot_ultralight,
)
from .utils import ensure_dir


PRIMARY_CONTROLLER_ORDER = ['GR', 'Proposed', 'RS', 'FBRL']


def _first_existing(paths: list[Path]) -> Path:
    for path in paths:
        if path.exists():
            return path
    joined = ', '.join(str(path) for path in paths)
    raise FileNotFoundError(f'None of the expected files exist: {joined}')


def _load_primary_tick_df(repo_root: Path) -> pd.DataFrame:
    tick_path = _first_existing([
        repo_root / 'outputs_24h_core_eval' / 'main_tick_results.csv',
        repo_root / 'outputs_24h_eval_retry' / 'main_tick_results.csv',
    ])
    df = pd.read_csv(tick_path, parse_dates=['timestamp'], low_memory=False)
    return df


def _load_primary_metrics_df(repo_root: Path) -> pd.DataFrame:
    metrics_path = _first_existing([
        repo_root / 'outputs_24h_core_eval' / 'main_metrics_by_scenario_day.csv',
        repo_root / 'outputs_24h_eval_retry' / 'main_metrics_by_scenario_day.csv',
    ])
    return pd.read_csv(metrics_path)


def _load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f'Missing required source table: {path}')
    return pd.read_csv(path)


def _choose_representative_seed(load_step_df: pd.DataFrame) -> int:
    best_seed = 0
    best_score = float('-inf')
    for seed, seed_df in load_step_df.groupby('seed', sort=False):
        proposed = seed_df[seed_df['controller'] == 'Proposed'].sort_values('timestamp')
        if proposed.empty:
            continue
        step_score = proposed['base_kw'].diff().abs().fillna(0.0).to_numpy(dtype=float)
        spread = (
            seed_df.pivot_table(index='timestamp', columns='controller', values='grid_kw', aggfunc='first')
            .sort_index()
        )
        divergence = np.zeros(len(proposed), dtype=float)
        if not spread.empty:
            spread_vals = spread.reindex(proposed['timestamp']).to_numpy(dtype=float)
            divergence = np.nanmax(spread_vals, axis=1) - np.nanmin(spread_vals, axis=1)
            divergence = np.nan_to_num(divergence, nan=0.0)
        score = float(step_score.max() + 0.35 * divergence.max())
        if score > best_score:
            best_score = score
            best_seed = int(seed)
    return best_seed


def _cycle_loss_controllers(metrics_df: pd.DataFrame) -> list[str]:
    available = set(metrics_df['controller'].astype(str))
    controllers = ['Proposed', 'GR']
    if 'MPC_ref' in available:
        controllers.append('MPC_ref')
    elif 'MPC_best_balanced' in available:
        controllers.append('MPC_best_balanced')
    controllers.append('FBRL')
    return [controller for controller in controllers if controller in available]


def _stage_box(ax: plt.Axes, x: float, y: float, w: float, h: float,
               title: str, body: str, facecolor: str) -> None:
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle='round,pad=0.25,rounding_size=0.9',
        linewidth=1.3,
        edgecolor='#516173',
        facecolor=facecolor,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h * 0.66, title, ha='center', va='center',
            fontsize=11.5, fontweight='bold', color='#17324d')
    ax.text(x + w / 2, y + h * 0.33, body, ha='center', va='center',
            fontsize=8.9, color='#1f2937', linespacing=1.25)


def _connect(ax: plt.Axes, start_x: float, start_y: float, end_x: float, end_y: float) -> None:
    arrow = FancyArrowPatch(
        (start_x, start_y),
        (end_x, end_y),
        arrowstyle='-|>',
        mutation_scale=14,
        linewidth=1.6,
        color='#5b84b1',
        shrinkA=0,
        shrinkB=0,
    )
    ax.add_patch(arrow)


def _draw_runtime_path_diagram(pdf_path: Path, png_path: Path) -> None:
    ensure_dir(pdf_path.parent)
    ensure_dir(png_path.parent)
    fig, ax = plt.subplots(figsize=(12.5, 3.8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 30)
    ax.axis('off')

    ax.text(
        50,
        27.3,
        'Fixed online execution order of the released supervisory artifact',
        ha='center',
        va='center',
        fontsize=17,
        fontweight='bold',
        color='#1f4e79',
    )

    stages = [
        (3.5, 'Meter inputs', 'Base load\nSOC, peak flag', '#dbeafe'),
        (17.5, 'Forecast', 'Saturated short-horizon\npreview', '#e8f5d7'),
        (31.5, 'Risk extraction', 'Current, peak, and\nnear-cap indicators', '#fdf0c8'),
        (45.5, 'Reserve shaping', 'Adaptive reserve\nband update', '#eee7fb'),
        (59.5, 'Priority rules', 'PS / VF /\nPREP / IDLE logic', '#d9ecff'),
        (73.5, 'Safe clipping', 'SOC-safe and\nstep-feasible bounds', '#dff3de'),
        (87.5, 'Command', 'Bounded battery\npower output', '#eef6d8'),
    ]

    box_w = 10.2
    box_h = 8.6
    y = 13.7
    for idx, (x, title, body, facecolor) in enumerate(stages):
        _stage_box(ax, x - box_w / 2, y, box_w, box_h, title, body, facecolor)
        if idx < len(stages) - 1:
            next_x = stages[idx + 1][0]
            _connect(ax, x + box_w / 2, y + box_h / 2, next_x - box_w / 2, y + box_h / 2)

    footer = FancyBboxPatch(
        (21.5, 5.1), 57.0, 4.0,
        boxstyle='round,pad=0.28,rounding_size=0.8',
        linewidth=1.2,
        edgecolor='#516173',
        facecolor='#f8fafc',
    )
    ax.add_patch(footer)
    ax.text(
        50,
        7.1,
        'Deterministic per tick  |  fixed-memory state  |  solver-free online path',
        ha='center',
        va='center',
        fontsize=11.0,
        fontweight='bold',
        color='#1f4e79',
    )
    ax.text(
        50,
        2.2,
        'Application-facing outcomes: ramp compliance, reduced switching, lower cycling burden',
        ha='center',
        va='center',
        fontsize=11.0,
        color='#374151',
    )

    fig.tight_layout(pad=0.4)
    fig.savefig(pdf_path)
    fig.savefig(png_path, dpi=300)
    plt.close(fig)


def _build_runtime_speedup_input(repo_root: Path) -> pd.DataFrame:
    path = repo_root / 'outputs_full_results_audit' / 'primary_benchmark_summary.csv'
    return _load_csv(path)


def _build_cross_benchmark_input(repo_root: Path) -> pd.DataFrame:
    controller_df = _build_primary_controller_summary(repo_root)
    if controller_df.empty:
        raise ValueError('Primary controller summary is empty; cannot regenerate cross-benchmark figures.')
    return controller_df


def _load_extension_tables(repo_root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ext_dir = repo_root / 'outputs_suscom_extensions'
    return (
        _load_csv(ext_dir / 'scan_time_summary.csv'),
        _load_csv(ext_dir / 'forecast_compute_summary.csv'),
        _load_csv(ext_dir / 'robustness_summary.csv'),
        _load_csv(ext_dir / 'ultralight_baseline_summary.csv'),
    )


def regenerate_manuscript_figures(repo_root: Path | None = None) -> dict[str, str]:
    repo_root = Path.cwd() if repo_root is None else Path(repo_root)
    suscom_dir = repo_root / 'SUSCOM'
    fig_dir = ensure_dir(suscom_dir / 'fig')
    figures_dir = ensure_dir(suscom_dir / 'figures')

    tick_df = _load_primary_tick_df(repo_root)
    metrics_df = _load_primary_metrics_df(repo_root)

    ramp_df = tick_df[tick_df['controller'].isin(PRIMARY_CONTROLLER_ORDER)].copy()
    save_ramp_cdf(ramp_df, fig_dir / 'ramp_cdf.pdf', PRIMARY_CONTROLLER_ORDER)

    load_step_df = tick_df[
        (tick_df['scenario'] == 'load_step') &
        (tick_df['controller'].isin(PRIMARY_CONTROLLER_ORDER))
    ].copy()
    representative_seed = _choose_representative_seed(load_step_df)
    rep_df = load_step_df[load_step_df['seed'] == representative_seed].copy()
    save_representative_timeseries(
        rep_df,
        fig_dir / 'representative_timeseries.pdf',
        PRIMARY_CONTROLLER_ORDER,
        n_points=240,
    )

    cycle_loss_controllers = _cycle_loss_controllers(metrics_df)
    save_metric_boxplot(
        metrics_df[metrics_df['controller'].isin(cycle_loss_controllers)].copy(),
        fig_dir / 'modeled_cycle_loss_boxplot.pdf',
        'lfp_cycle_loss_pct',
        cycle_loss_controllers,
        ylabel='Modeled LFP cycle-life loss (%)',
        title='Primary 24-hour benchmark: chemistry-calibrated cycling indicator',
    )

    _draw_runtime_path_diagram(
        fig_dir / 'runtime_path_diagram.pdf',
        figures_dir / 'runtime_path_diagram.png',
    )

    controller_summary_df = _build_cross_benchmark_input(repo_root)
    primary_summary_df = _build_runtime_speedup_input(repo_root)
    _plot_cross_benchmark_tradeoff(controller_summary_df, fig_dir / 'cross_benchmark_tradeoff.pdf')
    _plot_cycle_life_loss(controller_summary_df, fig_dir / 'cross_benchmark_cycle_loss.pdf')
    _plot_runtime_speedup(primary_summary_df, fig_dir / 'runtime_speedup.pdf')
    _plot_claim_heatmap(repo_root, fig_dir / 'scenario_nonworse_heatmap.pdf')
    _plot_parameter_plateau(repo_root, fig_dir / 'parameter_plateau.pdf')

    scan_df, forecast_df, robustness_df, ultralight_df = _load_extension_tables(repo_root)
    _plot_scan_time_runtime(scan_df, fig_dir / 'scan_time_runtime.pdf')
    _plot_forecast_compute(forecast_df, fig_dir / 'forecast_compute_runtime.pdf')
    _plot_robustness(robustness_df, fig_dir / 'measurement_wrapper_robustness.pdf')
    _plot_ultralight(ultralight_df, fig_dir / 'ultralight_runtime_tradeoff.pdf')

    return {
        'ramp_cdf': str(fig_dir / 'ramp_cdf.pdf'),
        'representative_timeseries': str(fig_dir / 'representative_timeseries.pdf'),
        'modeled_cycle_loss_boxplot': str(fig_dir / 'modeled_cycle_loss_boxplot.pdf'),
        'runtime_path_diagram': str(fig_dir / 'runtime_path_diagram.pdf'),
        'runtime_path_preview': str(figures_dir / 'runtime_path_diagram.png'),
        'cross_benchmark_tradeoff': str(fig_dir / 'cross_benchmark_tradeoff.pdf'),
        'cross_benchmark_cycle_loss': str(fig_dir / 'cross_benchmark_cycle_loss.pdf'),
        'runtime_speedup': str(fig_dir / 'runtime_speedup.pdf'),
        'scenario_nonworse_heatmap': str(fig_dir / 'scenario_nonworse_heatmap.pdf'),
        'parameter_plateau': str(fig_dir / 'parameter_plateau.pdf'),
        'scan_time_runtime': str(fig_dir / 'scan_time_runtime.pdf'),
        'forecast_compute_runtime': str(fig_dir / 'forecast_compute_runtime.pdf'),
        'measurement_wrapper_robustness': str(fig_dir / 'measurement_wrapper_robustness.pdf'),
        'ultralight_runtime_tradeoff': str(fig_dir / 'ultralight_runtime_tradeoff.pdf'),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Regenerate cleaned manuscript figures for the SUSCOM package.')
    parser.add_argument('--repo-root', type=str, default='.')
    args = parser.parse_args()
    regenerate_manuscript_figures(Path(args.repo_root).resolve())


if __name__ == '__main__':
    main()
