# Evidence Upgrade Summary

- Extended synthetic audit profiles: `80`
- External trace-driven audit profiles: `48`

## Baseline-Wise Directional Counts

| baseline | synthetic_profiles | synthetic_cap_wins | synthetic_throughput_wins | synthetic_cycle_loss_wins | trace_profiles | trace_cap_wins | trace_throughput_wins | trace_cycle_loss_wins |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NC | 80 | 80 | 0 | 0 | 48 | 48 | 0 | 0 |
| GR | 80 | 0 | 1 | 18 | 48 | 6 | 4 | 5 |
| RS | 80 | 75 | 80 | 80 | 48 | 48 | 0 | 0 |
| FBRL | 80 | 1 | 80 | 80 | 48 | 7 | 26 | 27 |

## Interpretation

- The extended synthetic audit broadens the internal stress-test evidence beyond the original small primary set.
- The external trace-driven audit adds non-synthetic daily structure derived from official OPSD load/solar/wind time series.
- The optimizer-based reference remains confined to the primary benchmark because its online solve path is substantially heavier than the lightweight controllers.