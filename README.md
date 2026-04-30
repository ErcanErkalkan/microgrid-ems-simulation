# Microgrid EMS Simulation

Microgrid EMS Simulation is a Python research-software package for reproducible
benchmarking of edge-executable microgrid energy-management controllers. It
generates deterministic synthetic PV, wind, load, and battery profiles; runs
multiple controller families; computes grid-compliance, battery-stress, and
runtime metrics; and exports publication-ready tables and figures.

The package is designed for researchers who need a transparent benchmark for
bounded-time supervisory energy-management logic rather than a one-off notebook
analysis. The current reference artifact is `outputs_reference`.

## Statement of Need

Microgrid EMS studies often compare controller objective values while leaving
software execution path, reproducibility, and battery-stress accounting hard to
audit. This package provides a reusable benchmark harness for:

- deterministic synthetic microgrid stress profiles,
- bounded-time rule-based EMS controllers intended for edge or PLC-style logic,
- baseline controllers including no-control, greedy rules, reactive smoothing,
  filter-based reference shaping, and constrained MPC references,
- per-scenario-day metrics for ramping, cap violation, SOC residency,
  throughput, equivalent full cycles, rainflow cycle counting, modeled
  LiFePO4 cycling loss, switching activity, and measured per-tick runtime,
- reproducible CSV, LaTeX, and PDF figure exports.

The software does not claim field-certified deployment performance. The current
benchmark is a reproducible software artifact using synthetic profiles.

## Installation

Use Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

For tests:

```powershell
python -m pip install -e .[test]
python -m unittest discover -s tests
```

## Quick Start

Run a reduced smoke benchmark:

```powershell
python main.py --smoke --output-dir outputs_smoke
```

Run the full benchmark:

```powershell
python main.py --output-dir outputs_reference --publication-package
```

The pipeline writes CSV tables, LaTeX tables, PDF figures, and
`run_manifest.json` into the selected output directory.

## Archived Release

The `v0.1.0` release is archived on Zenodo:
<https://doi.org/10.5281/zenodo.19924269>.

## Repository Layout

- `jer_microgrid/`: reusable Python package.
- `main.py`: command-line entry point.
- `tests/`: regression and smoke tests.
- `paper/`: JOSS paper source.
- `outputs_reference/`: current reproducibility artifact.

## Main Software Components

- `synth.py`: deterministic PV, wind, load, and net-demand generation.
- `controllers.py`: rule-based controllers and the proposed bounded-time EMS.
- `optimization_refs.py`: constrained MPC reference controllers.
- `simulation.py`: minute-level simulation loop and SOC dynamics.
- `metrics.py`: compliance, stress, rainflow, cycling, and runtime metrics.
- `pipeline.py`: end-to-end benchmark execution and artifact export.
- `publication.py`: parameter-audit and hold-out reporting utilities.

## API Example

The library can be used directly without running the full benchmark:

```python
from jer_microgrid.config import SiteConfig, SyntheticConfig
from jer_microgrid.controllers import build_controller
from jer_microgrid.metrics import compute_metrics
from jer_microgrid.simulation import simulate_controller
from jer_microgrid.synth import generate_profile

site = SiteConfig()
synth = SyntheticConfig(hours=1, scenario_names=["mixed"])
profile = generate_profile(0, "mixed", site, synth)
controller = build_controller("Proposed", site)
result = simulate_controller(profile, controller, site)
metrics = compute_metrics(result.series, site)
print(metrics["cap_violation_pct_total"])
```

See `docs/api.md` for the core API surface and expected inputs/outputs.

## Reproducing the Current Artifact

The canonical reference run is stored in `outputs_reference`. Its
`run_manifest.json` records the site parameters, synthetic profile parameters,
controller set, MPC sweep, seeds, and selected benchmark settings.

Expected headline values from the current artifact:

- Proposed mean cap violation: `0.00%`.
- No-control mean cap violation: `4.92%`.
- Proposed mean runtime: `0.141 ms/tick`.
- Proposed mean throughput reduction versus RS/FBRL: about `92%`.

These are software-benchmark results on synthetic profiles, not field or HIL
validation results.

## Tests and Verification

The unit test suite checks deterministic profile generation, SOC update
behavior, command feasibility for the proposed controller, metric computation,
and controller registry consistency. Run:

```powershell
python -m unittest discover -s tests
```

The repository also contains a GitHub Actions workflow in
`.github/workflows/tests.yml` for automated test execution on push and pull
request events.

For a slower end-to-end verification, run:

```powershell
python main.py --smoke --output-dir outputs_smoke
```

## Citation

Use `CITATION.cff` for software citation metadata. A JOSS paper draft is
available at `paper/paper.md`. The archived release DOI is
`10.5281/zenodo.19924269`.

## JOSS Submission Notes

The repository includes `docs/joss_checklist.md`, which separates completed
local preparation from external submission actions. The most important
remaining external requirement is evidence of sustained public development:
JOSS may reject repositories whose public history is concentrated immediately
before submission. If older development occurred elsewhere, document that
history with releases, issues, pull requests, publications, or external use.

## License

This project is released under the MIT License. See `LICENSE`.

## AI Usage Disclosure

OpenAI generative-AI assistance was used for documentation drafting,
manuscript-artifact consistency checking, test scaffolding, and local
submission-readiness review. The author reviewed, edited, and validated the
resulting material and remains responsible for the software, documentation,
and submitted paper.
