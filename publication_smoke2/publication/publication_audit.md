# Publication Audit

## Scope

Bu rapor, varsayılan Proposed controller için train/hold-out ayrımıyla küçük ölçekli bir yayın-auditi üretir.
Amaç dergi kabulünü garanti etmek değil; iddiaların ne kadar savunulabilir olduğunu tekrarlanabilir biçimde belgelemektir.

## Split

- Train seeds: `[0]`
- Hold-out seeds: `[0]`

## Selected Candidate

- Candidate label: `Candidate_01`
- Train score vs GR: `0.0004`
- Selected parameters:
  - `base_soft_low` = `0.32`
  - `prep_power_cap_kw` = `3.0`
  - `lookahead_gain` = `0.01`
  - `min_useful_cmd_kw` = `0.25`

## Default Proposed Parameters

- `base_soft_low` = `0.34`
- `min_useful_cmd_kw` = `0.5`
- `prep_power_cap_kw` = `4.0`
- `lookahead_gain` = `0.02`

## Hold-out Main Means

| Controller | Ramp95 | CapViolPct | Throughput | EFC | HighSOCDwell | HighCExposure | IDOD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FBRL | 2.41 (0.00) | 0.00 (0.00) | 17.84 (0.00) | 0.09 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) |
| GR | 9.46 (0.00) | 0.00 (0.00) | 0.02 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) |
| NC | 9.53 (0.00) | 0.28 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) |
| Proposed | 9.46 (0.00) | 0.00 (0.00) | 0.02 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) |
| RS | 2.97 (0.00) | 0.00 (0.00) | 18.79 (0.00) | 0.09 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) |

## Hold-out Claim Audit

| Reference | Baseline | Pairs | ramp95_kw_per_min_delta_mean | ramp95_kw_per_min_wins | ramp95_kw_per_min_ties | ramp95_kw_per_min_losses | cap_violation_pct_total_delta_mean | cap_violation_pct_total_wins | cap_violation_pct_total_ties | cap_violation_pct_total_losses | throughput_kwh_delta_mean | throughput_kwh_wins | throughput_kwh_ties | throughput_kwh_losses | idod_delta_mean | idod_wins | idod_ties | idod_losses | flip_per_day_delta_mean | flip_per_day_wins | flip_per_day_ties | flip_per_day_losses | all4_nonworse_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Proposed | NC | 1 | -0.07050969739122692 | 1 | 0 | 0 | -0.2777777777777778 | 1 | 0 | 0 | 0.01707339425699625 | 0 | 0 | 1 | 1.6149628335451827e-08 | 0 | 0 | 1 | 8.0 | 0 | 0 | 1 | 0 |
| Proposed | GR | 1 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 0.0014594337050549931 | 0 | 0 | 1 | 2.64293780262262e-09 | 0 | 0 | 1 | 0.0 | 0 | 1 | 0 | 0 |
| Proposed | RS | 1 | 6.488026944634669 | 0 | 0 | 1 | 0.0 | 0 | 1 | 0 | -18.77611394155281 | 1 | 0 | 0 | -0.00028339390162686524 | 1 | 0 | 0 | -536.0 | 1 | 0 | 0 | 0 |
| Proposed | FBRL | 1 | 7.0421170130252415 | 0 | 0 | 1 | 0.0 | 0 | 1 | 0 | -17.824686905389193 | 1 | 0 | 0 | -0.00030017853686245283 | 1 | 0 | 0 | -528.0 | 1 | 0 | 0 | 0 |

## Hold-out Pairwise Stats

| metric | comparison | n_pairs | mean_paired_diff | ci95_lo | ci95_hi | p_value | effect_size | effect_name | direction | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ramp95_kw_per_min | Proposed vs NC | 1 | -0.07050969739122692 | -0.07050969739122692 | -0.07050969739122692 | 1.0 | -1.0 | Cliff_delta | left_better | 1.0 |
| cap_violation_pct_total | Proposed vs NC | 1 | -0.2777777777777778 | -0.2777777777777778 | -0.2777777777777778 | 1.0 | -1.0 | Cliff_delta | left_better | 1.0 |
| throughput_kwh | Proposed vs NC | 1 | 0.01707339425699625 | 0.01707339425699625 | 0.01707339425699625 | 1.0 | 1.0 | Cliff_delta | right_better | 1.0 |
| idod | Proposed vs NC | 1 | 1.6149628335451827e-08 | 1.6149628335451827e-08 | 1.6149628335451827e-08 | 1.0 | 1.0 | Cliff_delta | right_better | 1.0 |
| flip_per_day | Proposed vs NC | 1 | 8.0 | 8.0 | 8.0 | 1.0 | 1.0 | Cliff_delta | right_better | 1.0 |
| ramp95_kw_per_min | Proposed vs GR | 1 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | Cliff_delta | right_better | 1.0 |
| cap_violation_pct_total | Proposed vs GR | 1 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | Cliff_delta | right_better | 1.0 |
| throughput_kwh | Proposed vs GR | 1 | 0.0014594337050549931 | 0.0014594337050549931 | 0.0014594337050549931 | 1.0 | 1.0 | Cliff_delta | right_better | 1.0 |
| idod | Proposed vs GR | 1 | 2.64293780262262e-09 | 2.64293780262262e-09 | 2.64293780262262e-09 | 1.0 | 1.0 | Cliff_delta | right_better | 1.0 |
| flip_per_day | Proposed vs GR | 1 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | Cliff_delta | right_better | 1.0 |
| ramp95_kw_per_min | Proposed vs RS | 1 | 6.488026944634669 | 6.488026944634669 | 6.488026944634669 | 1.0 | 1.0 | Cliff_delta | right_better | 1.0 |
| cap_violation_pct_total | Proposed vs RS | 1 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | Cliff_delta | right_better | 1.0 |
| throughput_kwh | Proposed vs RS | 1 | -18.77611394155281 | -18.77611394155281 | -18.77611394155281 | 1.0 | -1.0 | Cliff_delta | left_better | 1.0 |
| idod | Proposed vs RS | 1 | -0.00028339390162686524 | -0.00028339390162686524 | -0.00028339390162686524 | 1.0 | -1.0 | Cliff_delta | left_better | 1.0 |
| flip_per_day | Proposed vs RS | 1 | -536.0 | -536.0 | -536.0 | 1.0 | -1.0 | Cliff_delta | left_better | 1.0 |
| ramp95_kw_per_min | Proposed vs FBRL | 1 | 7.0421170130252415 | 7.0421170130252415 | 7.0421170130252415 | 1.0 | 1.0 | Cliff_delta | right_better | 1.0 |
| cap_violation_pct_total | Proposed vs FBRL | 1 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | Cliff_delta | right_better | 1.0 |
| throughput_kwh | Proposed vs FBRL | 1 | -17.824686905389193 | -17.824686905389193 | -17.824686905389193 | 1.0 | -1.0 | Cliff_delta | left_better | 1.0 |
| idod | Proposed vs FBRL | 1 | -0.00030017853686245283 | -0.00030017853686245283 | -0.00030017853686245283 | 1.0 | -1.0 | Cliff_delta | left_better | 1.0 |
| flip_per_day | Proposed vs FBRL | 1 | -528.0 | -528.0 | -528.0 | 1.0 | -1.0 | Cliff_delta | left_better | 1.0 |

## Interpretation

- `score_vs_gr < 0` means the selected candidate beats GR under the weighted publication score used by this audit.
- The claim audit is stricter: it reports per-metric delta means and win/tie/loss counts rather than a single score.
- A publishable manuscript still needs human-authored novelty positioning, related-work review, venue selection, and careful claim wording.