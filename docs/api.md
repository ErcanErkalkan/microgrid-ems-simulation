# API Overview

This document describes the core public API used by examples, tests, and the
benchmark pipeline. Internal helper functions whose names begin with `_` are
implementation details.

## Configuration

`jer_microgrid.config.SiteConfig`

Defines physical and operational settings for the synthetic microgrid,
including battery capacity, SOC limits, charge/discharge power limits,
efficiency, grid import/export caps, time step, and controller parameters.

`jer_microgrid.config.SyntheticConfig`

Defines synthetic profile generation settings such as scenario names, duration,
PV/wind/load amplitudes, stochastic event rates, and noise levels.

`jer_microgrid.config.OptimConfig`

Defines MPC reference settings, including horizon length and objective-weight
sweep values.

`jer_microgrid.config.ExperimentConfig`

Defines experiment-level settings such as seeds, output path, controller lists,
and publication-package options.

## Synthetic Profiles

`jer_microgrid.synth.generate_profile(seed, scenario, site, synth)`

Returns a deterministic `pandas.DataFrame` for one scenario/seed pair. The
frame includes timestamped PV, wind, load, base net-demand, peak-period flags,
and scenario identifiers. Calling the function twice with the same arguments
returns identical profile values.

`jer_microgrid.synth.generate_dataset(seeds, site, synth)`

Returns the concatenated profile dataset for all requested seeds and scenarios.
This is the normal input to the benchmark pipeline.

Example:

```python
from jer_microgrid.config import SiteConfig, SyntheticConfig
from jer_microgrid.synth import generate_profile

site = SiteConfig()
synth = SyntheticConfig(hours=2, scenario_names=["mixed"])
profile = generate_profile(7, "mixed", site, synth)
```

## Controllers and Simulation

`jer_microgrid.controllers.build_controller(name, site)`

Creates a controller instance by registry name. Main names include `Proposed`,
`NC`, `GR`, `RS`, and `FBRL`.

`jer_microgrid.simulation.simulate_controller(profile, controller, site)`

Runs a controller on a generated profile and returns a `SimResult`. The
`series` field contains per-tick commands, SOC, grid import/export behavior,
and CPU timing measurements.

`jer_microgrid.simulation.soc_update(soc, cmd_kw, site)`

Applies one time-step battery SOC update for a charge/discharge command while
respecting configured SOC bounds and asymmetric efficiency.

Example:

```python
from jer_microgrid.config import SiteConfig, SyntheticConfig
from jer_microgrid.controllers import build_controller
from jer_microgrid.simulation import simulate_controller
from jer_microgrid.synth import generate_profile

site = SiteConfig()
synth = SyntheticConfig(hours=1, scenario_names=["load_step"])
profile = generate_profile(3, "load_step", site, synth)
controller = build_controller("Proposed", site)
result = simulate_controller(profile, controller, site)
```

## Metrics

`jer_microgrid.metrics.compute_metrics(sim, site)`

Computes scalar metrics from a simulation result frame. The returned dictionary
includes grid-ramp statistics, cap-violation percentages, battery throughput,
equivalent full cycles, modeled LiFePO4 cycling loss, switching activity, and
mean/max CPU time.

`jer_microgrid.metrics.compute_group_metrics(sim, site, group_cols)`

Computes the same metrics independently for each group in a per-tick simulation
frame, for example by controller, scenario, and seed.

Example:

```python
from jer_microgrid.metrics import compute_metrics

metrics = compute_metrics(result.series, site)
print(metrics["cap_violation_pct_total"])
```

## Full Benchmark

`jer_microgrid.pipeline.build_default_configs(smoke=False)`

Returns default site, synthetic-profile, optimization, and experiment
configuration objects. Set `smoke=True` for a reduced reviewer-verification
run.

`jer_microgrid.pipeline.run_full_pipeline(site, synth, optim, exp, output_dir)`

Runs the complete benchmark, writes CSV/LaTeX/PDF outputs and
`run_manifest.json`, and returns the generated in-memory tables.

For command-line use:

```powershell
python main.py --smoke --output-dir outputs_smoke
python main.py --output-dir outputs_reference --publication-package
```
