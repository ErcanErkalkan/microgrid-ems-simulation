from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .config import SiteConfig
from .utils import quantile_safe


def _reversals(series: np.ndarray) -> list[float]:
    x = np.asarray(series, dtype=float)
    if x.size < 2:
        return x.tolist()
    rev = [x[0]]
    for i in range(1, len(x) - 1):
        prev_, cur_, next_ = x[i - 1], x[i], x[i + 1]
        if (cur_ >= prev_ and cur_ > next_) or (cur_ > prev_ and cur_ >= next_) or (cur_ <= prev_ and cur_ < next_) or (cur_ < prev_ and cur_ <= next_):
            rev.append(cur_)
    rev.append(x[-1])
    out = [rev[0]]
    for v in rev[1:]:
        if v != out[-1]:
            out.append(v)
    return out


def rainflow_cycles(series: np.ndarray) -> list[tuple[float, float]]:
    pts = _reversals(series)
    stack: list[float] = []
    cycles: list[tuple[float, float]] = []
    for x in pts:
        stack.append(x)
        while len(stack) >= 3:
            s0, s1, s2 = stack[-3], stack[-2], stack[-1]
            r1 = abs(s1 - s0)
            r2 = abs(s2 - s1)
            if r2 < r1:
                break
            if len(stack) == 3:
                cycles.append((r1, 0.5))
                stack.pop(-2)
            else:
                cycles.append((r1, 1.0))
                last = stack[-1]
                stack = stack[:-3] + [last]
    for i in range(len(stack) - 1):
        cycles.append((abs(stack[i + 1] - stack[i]), 0.5))
    return cycles


def compute_metrics(sim: pd.DataFrame, site: SiteConfig) -> dict[str, Any]:
    grid = sim['grid_kw'].to_numpy(dtype=float)
    cmd = sim['cmd_kw'].to_numpy(dtype=float)
    soc = sim['soc'].to_numpy(dtype=float)
    p_imp_cap = sim['p_imp_cap'].to_numpy(dtype=float)
    p_exp_cap = sim['p_exp_cap'].to_numpy(dtype=float)
    dt_min = site.ts_hours * 60.0

    ramp = np.abs(np.diff(grid, prepend=grid[0])) / dt_min
    imp_v = grid > p_imp_cap
    exp_v = -grid > p_exp_cap
    throughput = np.sum(np.abs(cmd)) * site.ts_hours
    efc = throughput / (2.0 * site.e_nom_kwh)
    soc_band_residency = np.mean((soc >= site.soc_min) & (soc <= site.soc_max))
    t_high = np.sum(soc > site.soc_high_thresh) * site.ts_hours
    t_low = np.sum(soc < site.soc_low_thresh) * site.ts_hours
    ceq = np.abs(cmd) / site.e_nom_kwh
    t_high_c = np.sum(ceq > site.c_high) * site.ts_hours
    q95_ceq = quantile_safe(ceq, 0.95)

    cycles = rainflow_cycles(soc)
    if cycles:
        depths = np.asarray([d for d, _ in cycles], dtype=float)
        weights = np.asarray([w for _, w in cycles], dtype=float)
        efcrf = float(np.sum(weights * depths))
        idod = float(np.sum(weights * depths ** site.beta_dod))
        n_micro = float(np.sum(weights * (depths <= site.dmc)))
        bins = np.array([0.0, 0.1, 0.2, 0.4, 0.6, 1.0 + 1e-9])
        hist, edges = np.histogram(depths, bins=bins, weights=weights)
        hist_payload = {f"[{edges[i]:.1f},{edges[i+1]:.1f})": float(hist[i]) for i in range(len(hist))}
    else:
        efcrf = 0.0
        idod = 0.0
        n_micro = 0.0
        hist_payload = {}

    modes = sim['mode'].astype(str).to_numpy()
    flips = int(np.sum(modes[1:] != modes[:-1])) if len(modes) > 1 else 0
    horizon_hours = len(sim) * site.ts_hours
    flip_per_hour = flips / horizon_hours if horizon_hours > 0 else 0.0
    flip_per_day = flips / (horizon_hours / 24.0) if horizon_hours > 0 else 0.0

    metrics = {
        'ramp95_kw_per_min': quantile_safe(ramp, 0.95),
        'cap_violation_pct_import': 100.0 * np.mean(imp_v),
        'cap_violation_pct_export': 100.0 * np.mean(exp_v),
        'cap_violation_pct_total': 100.0 * np.mean(imp_v | exp_v),
        'soc_band_residency': float(soc_band_residency),
        'throughput_kwh': float(throughput),
        'efc': float(efc),
        't_high_soc_h': float(t_high),
        't_low_soc_h': float(t_low),
        'ceq_q95': float(q95_ceq),
        't_high_c_h': float(t_high_c),
        'efcrf': float(efcrf),
        'idod': float(idod),
        'n_micro': float(n_micro),
        'flip_per_hour': float(flip_per_hour),
        'flip_per_day': float(flip_per_day),
        'mean_cpu_ms': float(sim['cpu_ms'].mean()),
        'max_cpu_ms': float(sim['cpu_ms'].max()),
        'rainflow_hist': hist_payload,
    }
    return metrics


def compute_group_metrics(sim: pd.DataFrame, site: SiteConfig, group_cols: list[str]) -> pd.DataFrame:
    rows = []
    for keys, g in sim.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys))
        row.update(compute_metrics(g, site))
        rows.append(row)
    return pd.DataFrame(rows)
