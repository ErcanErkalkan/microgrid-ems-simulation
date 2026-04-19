# Microgrid EMS Simulation

Public code and results repository for the microgrid EMS study.

Repository URL:
- https://github.com/ErcanErkalkan/microgrid-ems-simulation

## Scope

This repository contains:
- the simulation code in `jer_microgrid/`
- the CLI entry point in `main.py`
- reproducibility outputs for the benchmark, audit, and smoke runs
- the experiment notebook and supporting run scripts

This repository intentionally does **not** contain the manuscript package.
The manuscript directory is excluded from version control and is shared separately with the journal submission.

## Environment

Recommended Python version:
- Python 3.10 to 3.13

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Main Commands

Smoke run:

```powershell
python main.py --smoke --output-dir outputs_smoke
```

Full run:

```powershell
python main.py --output-dir outputs_full
```

Full run with publication audit:

```powershell
python main.py --output-dir outputs_full --publication-package
```

## Key Repository Contents

- `jer_microgrid/`: controllers, simulation, metrics, plotting, audits
- `main.py`: experiment entry point
- `run_experiments.ps1`: convenience script for Windows
- `outputs_24h_core_eval/`: primary 24-hour benchmark artifact
- `outputs_cross_benchmark_evidence/`: cross-benchmark summaries
- `outputs_parameter_audit/`: parameter search and sensitivity evidence
- `outputs_full_results_audit/`: full directory-level audit of all result folders

## Notes

- The public repository contains code and result artifacts only.
- The manuscript and journal-specific submission files are intentionally excluded.
- Experiments are deterministic under fixed seeds.
