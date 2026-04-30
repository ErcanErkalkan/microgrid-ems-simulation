---
title: "Microgrid EMS Simulation: A reproducible Python package for benchmarking bounded-time edge energy-management controllers"
tags:
  - Python
  - microgrid
  - energy management system
  - edge computing
  - battery storage
  - reproducible benchmark
authors:
  - name: Ercan Erkalkan
    affiliation: 1
affiliations:
  - name: Department of Computer Technologies, Vocational School of Technical Sciences, Marmara University, Turkey
    index: 1
date: 30 April 2026
bibliography: paper.bib
---

# Summary

Microgrid EMS Simulation is a Python package for reproducible benchmarking of
energy-management controllers for grid-connected PV--wind--battery microgrids.
The software generates deterministic synthetic stress profiles, runs multiple
controller families, simulates battery state-of-charge dynamics at minute-level
cadence, and exports compliance, battery-stress, and runtime metrics. The
package is intended for researchers who need an auditable benchmark for
bounded-time edge supervisory logic rather than a single notebook-based
analysis.

The current release includes a forecast-guided cap-correction and
reserve-preparation controller, no-control and greedy rule baselines, reactive
and filter-based smoothing baselines, constrained MPC references, parameter
sensitivity sweeps, ablations, paired statistical summaries, and publication
tables and figures. The canonical reproducibility artifact is stored in
`outputs_reference` and is described by a machine-readable `run_manifest.json`.

# Statement of Need

Microgrid energy-management studies often report controller objective values
without making the implementation path, runtime cost, and battery-stress
accounting easy to inspect or reproduce. Researchers who want to study
edge-executable supervisory control need a benchmark that exposes the full path
from profile generation to controller execution, metric aggregation, and figure
export.

Microgrid EMS Simulation addresses this need by providing:

- deterministic PV, wind, load, and battery-excluded net-demand generation,
- reusable controller implementations with a common simulation interface,
- grid cap-compliance and ramping metrics,
- battery throughput, equivalent-full-cycle, rainflow, micro-cycle, and modeled
  LiFePO4 cycling indicators,
- measured per-tick software runtime summaries,
- CSV, LaTeX, and PDF exports suitable for reproducible manuscript workflows.

The software is not a field-certified microgrid controller and does not replace
hardware-in-the-loop or site validation. Its contribution is a reusable
research-software benchmark for comparing supervisory control logic under
controlled synthetic scenarios.

# State of the Field

Open-source power-system tools such as OpenDSS [@dugan2011opendss],
GridLAB-D [@chassin2008gridlabd], pandapower [@thurner2018pandapower], and
PyPSA [@brown2018pypsa] provide broad modeling and simulation capabilities for
distribution systems, power flow, and energy-system analysis. These tools are
valuable for network modeling, but they are not focused on a compact,
controller-centric benchmark that exports paired per-scenario-day metrics for
edge-executable microgrid EMS logic and battery-stress accounting.

The present package is complementary to those platforms. It keeps the physical
plant model deliberately compact so that controller behavior, runtime path,
and reproducibility are easy to audit. It is therefore useful for developing
and comparing supervisory EMS policies before moving selected candidates into
larger power-system simulators or hardware-in-the-loop testbeds.

The package was built as a benchmark harness rather than as a new network
solver because the research question concerns controller execution, grid-cap
compliance, battery use, and reproducible metric generation under identical
profiles. Reusing a full power-flow platform for this purpose would make the
controller path harder to inspect and would not by itself provide paired
per-scenario-day stress and runtime outputs. The intended workflow is therefore
to use this package for fast, auditable controller comparison and then transfer
selected policies to more detailed electrical simulators when network effects
or site-specific validation are the focus.

# Software Design

The package is organized as a reusable Python library plus a command-line
entry point. Synthetic profile generation is implemented in `synth.py`.
Controller implementations are in `controllers.py`, including rule-based
controllers, filter-based smoothing, ablations of the proposed controller, and
shared command-bound utilities. The simulation loop in `simulation.py` applies
controller commands, updates battery SOC with asymmetric charge/discharge
efficiencies, and records per-tick CPU timing. Metric computation in
`metrics.py` covers grid-ramp behavior, cap violations, throughput, EFC,
rainflow cycle counts, IDOD, modeled LiFePO4 cycle-life loss, switching
activity, and runtime. `pipeline.py` orchestrates full benchmark execution,
table generation, figure generation, and manifest export.

These design choices trade physical detail for auditability. The simulator
uses a compact grid-connected PV--wind--battery abstraction so that each
controller receives the same deterministic net-demand path and every command
can be traced to subsequent SOC, cap-compliance, stress, and runtime outputs.
The MPC controllers are included as reproducible references rather than as the
primary deployment target; this keeps the proposed bounded-time supervisory
logic comparable against optimization-based behavior while preserving a simple
edge-execution path.

The design emphasizes reproducibility and inspection:

- all random synthetic profiles are seed-controlled,
- controller outputs are logged at every tick,
- aggregated tables are derived from exported per-tick and per-scenario-day
  CSV files,
- the full benchmark configuration is captured in `run_manifest.json`,
- the reduced smoke run provides a fast verification path for reviewers.

# Research Impact

The software enables researchers to reproduce a complete microgrid EMS
benchmark and to extend it with new controllers, metrics, or synthetic
scenario families. It is particularly useful for studies where bounded-time
execution, controller auditability, and battery-stress reporting are part of
the research question. The current reference artifact shows how a local
rule-based controller can be compared against no-control, greedy, smoothing,
and MPC references under the same profiles and metric pipeline. In the current
synthetic benchmark artifact, the proposed controller achieves zero mean
cap-violation rate, while the no-control baseline has a mean cap-violation
rate of 4.92%. The same artifact records a mean proposed-controller runtime of
0.141 ms per tick and an approximately 92% throughput reduction relative to
the reactive-smoothing and filter-based shaping baselines.

The package is also designed as a starting point for future work. Researchers
can add field traces, hardware-in-the-loop interfaces, alternative battery
aging models, or additional optimization and learning-based baselines while
reusing the existing reporting and verification pipeline.

The current repository also includes a complete reference run, reduced smoke
verification, and tests for the core simulation path. These materials make the
software suitable for method-comparison papers, teaching demonstrations on
microgrid control trade-offs, and artifact-review workflows where reviewers
need to verify that published tables can be traced back to deterministic code
and exported intermediate data.

# Availability and Reproducibility

The source code is available from the public repository:
<https://github.com/ErcanErkalkan/microgrid-ems-simulation>. The software is
released under the MIT License. The repository includes installation
instructions, tests, a smoke benchmark command, the current reproducibility
artifact, and citation metadata.

The archived `v0.1.0` software release is available from Zenodo with DOI
<https://doi.org/10.5281/zenodo.19924269> [@microgridems2026]. The included
`CITATION.cff` and `.zenodo.json` files provide software-citation and
release-archive metadata for the tagged version submitted for review.

The smoke benchmark can be run with:

```bash
python main.py --smoke --output-dir outputs_smoke
```

The full reference benchmark can be reproduced with:

```bash
python main.py --output-dir outputs_reference --publication-package
```

# AI Usage Disclosure

OpenAI generative-AI assistance was used for documentation drafting,
manuscript-artifact consistency checking, test scaffolding, and local review of
submission-readiness material. The author reviewed, edited, and validated the
AI-assisted outputs, ran the verification checks, and made the core software
design, scientific, and submission decisions.

# Acknowledgements

No external funding was received for this work.

# References
