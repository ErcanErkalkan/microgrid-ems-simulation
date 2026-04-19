from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .utils import ensure_dir


plt.rcParams.update({
    'figure.dpi': 140,
    'savefig.dpi': 300,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'svg.fonttype': 'none',
})


def save_ramp_cdf(series_df: pd.DataFrame, output_path: str | Path, controller_order: list[str]) -> None:
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    for name in controller_order:
        g = series_df[series_df['controller'] == name]
        if g.empty:
            continue
        ramp = np.abs(np.diff(g['grid_kw'].to_numpy(dtype=float), prepend=g['grid_kw'].iloc[0]))
        xs = np.sort(ramp)
        ys = np.arange(1, len(xs) + 1) / len(xs)
        ax.plot(xs, ys, label=name)
    ax.set_xlabel('Absolute PCC step (kW)')
    ax.set_ylabel('CDF')
    ax.set_title('Ramp-rate magnitude distribution')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def save_representative_timeseries(series_df: pd.DataFrame, output_path: str | Path, controllers: list[str], n_points: int = 360) -> None:
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    base_plotted = False
    for name in controllers:
        g = series_df[series_df['controller'] == name].head(n_points)
        if g.empty:
            continue
        if not base_plotted:
            ax.plot(g['timestamp'], g['base_kw'], label='Base net demand')
            base_plotted = True
        ax.plot(g['timestamp'], g['grid_kw'], label=f'Grid ({name})')
    ax.set_xlabel('Time')
    ax.set_ylabel('Power (kW)')
    ax.set_title('Representative base and grid power trajectories')
    ax.legend(fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def save_rainflow_hist(hist_df: pd.DataFrame, output_path: str | Path, controllers: list[str]) -> None:
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    width = 0.12
    bins = sorted(hist_df['depth_bin'].unique())
    xs = np.arange(len(bins))
    for i, name in enumerate(controllers):
        g = hist_df[hist_df['controller'] == name]
        if g.empty:
            continue
        vals = [float(g[g['depth_bin'] == b]['count_weighted'].sum()) for b in bins]
        ax.bar(xs + i * width, vals, width=width, label=name)
    ax.set_xticks(xs + width * (len(controllers) - 1) / 2)
    ax.set_xticklabels(bins, rotation=20)
    ax.set_ylabel('Count-weighted cycles')
    ax.set_title('Rainflow cycle-depth histogram')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def save_stress_boxplots(metrics_df: pd.DataFrame, output_path: str | Path, metrics: list[str], controller_order: list[str]) -> None:
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    fig, axes = plt.subplots(len(metrics), 1, figsize=(8.0, 2.8 * len(metrics)), sharex=True)
    if len(metrics) == 1:
        axes = [axes]
    for ax, metric in zip(axes, metrics):
        data = [metrics_df[metrics_df['controller'] == c][metric].to_numpy(dtype=float) for c in controller_order if c in metrics_df['controller'].unique()]
        labels = [c for c in controller_order if c in metrics_df['controller'].unique()]
        ax.boxplot(data, labels=labels, showfliers=False)
        ax.set_ylabel(metric)
        ax.set_title(metric)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def save_pareto_frontier(frontier_df: pd.DataFrame, output_path: str | Path, x: str = 'ramp95_kw_per_min', y: str = 'throughput_kwh') -> None:
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    if not frontier_df.empty:
        ax.scatter(frontier_df[x], frontier_df[y], s=20)
        for _, row in frontier_df.iterrows():
            ax.annotate(row.get('label', ''), (row[x], row[y]), fontsize=7)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title('Optimization Pareto frontier')
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def save_sensitivity_heatmap(pivot_df: pd.DataFrame, output_path: str | Path, title: str) -> None:
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    fig, ax = plt.subplots(figsize=(6.0, 4.5))
    mat = pivot_df.to_numpy(dtype=float)
    im = ax.imshow(mat, aspect='auto')
    ax.set_xticks(range(pivot_df.shape[1]))
    ax.set_xticklabels([str(c) for c in pivot_df.columns])
    ax.set_yticks(range(pivot_df.shape[0]))
    ax.set_yticklabels([str(i) for i in pivot_df.index])
    ax.set_title(title)
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
