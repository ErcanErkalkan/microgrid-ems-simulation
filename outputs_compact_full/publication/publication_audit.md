# Publication Audit

## Scope

Bu rapor, Proposed controller için kanonik train/hold-out ayrımı ile repeated-split stabilite kontrolünü birlikte üretir.
Amaç dergi kabulünü garanti etmek değil; iddiaların ne kadar savunulabilir olduğunu tekrarlanabilir biçimde belgelemektir.

## Canonical Split

- Train seeds: `[0]`
- Hold-out seeds: `[1]`

## Selected Candidate

- Candidate label: `Candidate_01`
- Canonical train score vs GR: `0.0004`
- Repeated-split mean hold score vs GR: `0.0002`
- Repeated-split std hold score vs GR: `0.0003`
- Repeated-split mean hold cap delta vs GR: `0.0000`
- Repeated-split mean hold rank: `1.00`
- Selected parameters:
  - `base_soft_low` = `0.32`
  - `prep_power_cap_kw` = `3.0`
  - `lookahead_gain` = `0.01`
  - `min_useful_cmd_kw` = `0.25`

## Default Proposed Parameters

- `base_soft_low` = `0.32`
- `min_useful_cmd_kw` = `0.25`
- `prep_power_cap_kw` = `4.0`
- `lookahead_gain` = `0.01`

## Candidate Stability Top-5

| candidate | base_soft_low | prep_power_cap_kw | lookahead_gain | min_useful_cmd_kw | mean_train_score_vs_gr | mean_hold_score_vs_gr | std_hold_score_vs_gr | max_hold_score_vs_gr | mean_hold_rank | best_hold_rank_count | mean_hold_ramp_delta_vs_gr | mean_hold_cap_delta_vs_gr | mean_hold_throughput_delta_vs_gr | mean_hold_idod_delta_vs_gr | mean_hold_flip_delta_vs_gr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Candidate_01 | 0.32 | 3.0 | 0.01 | 0.25 | 0.00018252832329947248 | 0.00018252832329947248 | 0.00025813403032733497 | 0.00036505664659894496 | 1.0 | 2 | 0.0 | 0.0 | 0.0007297168525274966 | 1.32146890131131e-09 | 0.0 |
| Candidate_02 | 0.32 | 4.0 | 0.01 | 0.25 | 0.00018252832329947248 | 0.00018252832329947248 | 0.00025813403032733497 | 0.00036505664659894496 | 1.0 | 2 | 0.0 | 0.0 | 0.0007297168525274966 | 1.32146890131131e-09 | 0.0 |
| Candidate_03 | 0.32 | 5.0 | 0.01 | 0.25 | 0.00018252832329947248 | 0.00018252832329947248 | 0.00025813403032733497 | 0.00036505664659894496 | 1.0 | 2 | 0.0 | 0.0 | 0.0007297168525274966 | 1.32146890131131e-09 | 0.0 |
| Candidate_05 | 0.32 | 4.0 | 0.01 | 0.5 | 0.00018252832329947248 | 0.00018252832329947248 | 0.00025813403032733497 | 0.00036505664659894496 | 1.0 | 2 | 0.0 | 0.0 | 0.0007297168525274966 | 1.32146890131131e-09 | 0.0 |
| Candidate_06 | 0.34 | 3.0 | 0.01 | 0.25 | 0.00018252832329947248 | 0.00018252832329947248 | 0.00025813403032733497 | 0.00036505664659894496 | 1.0 | 2 | 0.0 | 0.0 | 0.0007297168525274966 | 1.32146890131131e-09 | 0.0 |

## Hold-out Main Means

| Controller | Ramp95 | CapViolPct | Throughput | EFC | HighSOCDwell | HighCExposure | IDOD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FBRL | 2.41 (0.00) | 0.00 (0.00) | 17.11 (0.00) | 0.09 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) |
| GR | 9.75 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) |
| NC | 9.75 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) |
| Proposed | 9.75 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) |
| RS | 2.88 (0.00) | 0.00 (0.00) | 18.61 (0.00) | 0.09 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) |

## Hold-out Claim Audit

| Reference | Baseline | Pairs | ramp95_kw_per_min_delta_mean | ramp95_kw_per_min_wins | ramp95_kw_per_min_ties | ramp95_kw_per_min_losses | cap_violation_pct_total_delta_mean | cap_violation_pct_total_wins | cap_violation_pct_total_ties | cap_violation_pct_total_losses | throughput_kwh_delta_mean | throughput_kwh_wins | throughput_kwh_ties | throughput_kwh_losses | idod_delta_mean | idod_wins | idod_ties | idod_losses | flip_per_day_delta_mean | flip_per_day_wins | flip_per_day_ties | flip_per_day_losses | all4_nonworse_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Proposed | NC | 2 | 0.0 | 0 | 2 | 0 | 0.0 | 0 | 2 | 0 | 0.0 | 0 | 2 | 0 | 0.0 | 0 | 2 | 0 | 0.0 | 0 | 2 | 0 | 2 |
| Proposed | GR | 2 | 0.0 | 0 | 2 | 0 | 0.0 | 0 | 2 | 0 | 0.0 | 0 | 2 | 0 | 0.0 | 0 | 2 | 0 | 0.0 | 0 | 2 | 0 | 2 |
| Proposed | RS | 2 | 6.870821834035517 | 0 | 0 | 2 | 0.0 | 0 | 2 | 0 | -18.61360024441178 | 2 | 0 | 0 | -0.0002640273825203316 | 2 | 0 | 0 | -552.0 | 2 | 0 | 0 | 0 |
| Proposed | FBRL | 2 | 7.342484602961488 | 0 | 0 | 2 | 0.0 | 0 | 2 | 0 | -17.106922336831893 | 2 | 0 | 0 | -0.00027234406824740425 | 2 | 0 | 0 | -536.0 | 2 | 0 | 0 | 0 |

## Hold-out Claim Audit By Scenario

| Scenario | Reference | Baseline | Pairs | ramp95_kw_per_min_delta_mean | ramp95_kw_per_min_wins | ramp95_kw_per_min_ties | ramp95_kw_per_min_losses | cap_violation_pct_total_delta_mean | cap_violation_pct_total_wins | cap_violation_pct_total_ties | cap_violation_pct_total_losses | throughput_kwh_delta_mean | throughput_kwh_wins | throughput_kwh_ties | throughput_kwh_losses | idod_delta_mean | idod_wins | idod_ties | idod_losses | flip_per_day_delta_mean | flip_per_day_wins | flip_per_day_ties | flip_per_day_losses | all4_nonworse_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cloud_edge | Proposed | NC | 1 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 1 |
| cloud_edge | Proposed | GR | 1 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 1 |
| cloud_edge | Proposed | RS | 1 | 6.870821834035517 | 0 | 0 | 1 | 0.0 | 0 | 1 | 0 | -18.61360024441178 | 1 | 0 | 0 | -0.0002640273825203316 | 1 | 0 | 0 | -552.0 | 1 | 0 | 0 | 0 |
| cloud_edge | Proposed | FBRL | 1 | 7.342484602961488 | 0 | 0 | 1 | 0.0 | 0 | 1 | 0 | -17.106922336831893 | 1 | 0 | 0 | -0.00027234406824740425 | 1 | 0 | 0 | -536.0 | 1 | 0 | 0 | 0 |
| mixed | Proposed | NC | 1 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 1 |
| mixed | Proposed | GR | 1 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 0.0 | 0 | 1 | 0 | 1 |
| mixed | Proposed | RS | 1 | 6.870821834035517 | 0 | 0 | 1 | 0.0 | 0 | 1 | 0 | -18.61360024441178 | 1 | 0 | 0 | -0.0002640273825203316 | 1 | 0 | 0 | -552.0 | 1 | 0 | 0 | 0 |
| mixed | Proposed | FBRL | 1 | 7.342484602961488 | 0 | 0 | 1 | 0.0 | 0 | 1 | 0 | -17.106922336831893 | 1 | 0 | 0 | -0.00027234406824740425 | 1 | 0 | 0 | -536.0 | 1 | 0 | 0 | 0 |

## Hold-out Pairwise Stats

| metric | comparison | n_pairs | mean_paired_diff | ci95_lo | ci95_hi | p_value | effect_size | effect_name | direction | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ramp95_kw_per_min | Proposed vs NC | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| cap_violation_pct_total | Proposed vs NC | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| throughput_kwh | Proposed vs NC | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| idod | Proposed vs NC | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| flip_per_day | Proposed vs NC | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| ramp95_kw_per_min | Proposed vs GR | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| cap_violation_pct_total | Proposed vs GR | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| throughput_kwh | Proposed vs GR | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| idod | Proposed vs GR | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| flip_per_day | Proposed vs GR | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| ramp95_kw_per_min | Proposed vs RS | 2 | 6.870821834035517 | 6.870821834035517 | 6.870821834035517 | 0.5 | 1.0 | Cliff_delta | right_better | 1.0 |
| cap_violation_pct_total | Proposed vs RS | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| throughput_kwh | Proposed vs RS | 2 | -18.61360024441178 | -18.61360024441178 | -18.61360024441178 | 0.5 | -1.0 | Cliff_delta | left_better | 1.0 |
| idod | Proposed vs RS | 2 | -0.0002640273825203316 | -0.0002640273825203316 | -0.0002640273825203316 | 0.5 | -1.0 | Cliff_delta | left_better | 1.0 |
| flip_per_day | Proposed vs RS | 2 | -552.0 | -552.0 | -552.0 | 0.5 | -1.0 | Cliff_delta | left_better | 1.0 |
| ramp95_kw_per_min | Proposed vs FBRL | 2 | 7.342484602961488 | 7.342484602961488 | 7.342484602961488 | 0.5 | 1.0 | Cliff_delta | right_better | 1.0 |
| cap_violation_pct_total | Proposed vs FBRL | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| throughput_kwh | Proposed vs FBRL | 2 | -17.106922336831893 | -17.106922336831893 | -17.106922336831893 | 0.5 | -1.0 | Cliff_delta | left_better | 1.0 |
| idod | Proposed vs FBRL | 2 | -0.00027234406824740425 | -0.00027234406824740425 | -0.00027234406824740425 | 0.5 | -1.0 | Cliff_delta | left_better | 1.0 |
| flip_per_day | Proposed vs FBRL | 2 | -536.0 | -536.0 | -536.0 | 0.5 | -1.0 | Cliff_delta | left_better | 1.0 |

## Interpretation

- `score_vs_gr < 0` means the selected candidate beats GR under the weighted publication score used by this audit.
- Repeated-split stability is stricter than a single split: lower mean hold score and lower variance imply a more robust candidate choice.
- The claim audit is stricter than the score: it reports per-metric delta means and win/tie/loss counts rather than a single scalar.
- A publishable manuscript still needs human-authored novelty positioning, related-work review, venue selection, and careful claim wording.