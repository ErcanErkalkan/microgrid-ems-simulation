# Full Results Audit

## Directory Roles

| Category | Directories | Examples | Role |
| --- | --- | --- | --- |
| primary_postfix | 3 | outputs_24h_core_eval, outputs_compact_full, outputs_medium_full | Independent benchmark evidence |
| incomplete | 1 | outputs_24h_eval | Discarded incomplete early run |
| redundant_retry | 1 | outputs_24h_eval_retry | Redundant 24 h retry / regression evidence |
| derived_audit | 2 | outputs_cross_benchmark_evidence, outputs_parameter_audit | Derived audit / secondary evidence |
| smoke_regression | 10 | publication_smoke, publication_smoke2, publication_smoke3 | Smoke / regression verification |

## Primary Benchmark Summary

| result_dir | hours | profiles | proposed_ramp95 | proposed_cap_violation_pct | proposed_throughput_kwh | proposed_lfp_cycle_loss_pct | gr_throughput_kwh | gr_lfp_cycle_loss_pct | throughput_vs_gr_delta_kwh | lfp_cycle_loss_vs_gr_delta_pctpt | throughput_reduction_vs_rs_pct | throughput_reduction_vs_fbrl_pct | lfp_cycle_loss_reduction_vs_rs_pct | lfp_cycle_loss_reduction_vs_fbrl_pct | cap_gain_vs_nc_pctpt | cpu_speedup_vs_mpc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| outputs_compact_full | 6.0 | 4 | 9.602083810067544 | 0.0 | 0.0085366971284981 | 6.199837535863728e-07 | 0.0078069802759706 | 5.669778923320188e-07 | 0.0007297168525275 | 5.300586125435398e-08 | 99.95435749669662 | 99.95114724513485 | 99.94035133817317 | 99.93529031026043 | 0.1388888888888889 | 3261.802913042707 |
| outputs_medium_full | 12.0 | 8 | 9.032893028441366 | 0.0 | 0.8052375703616899 | 7.583560335042573e-05 | 0.7278377926904847 | 7.64706012845945e-05 | 0.0773997776712052 | -6.349979341687664e-07 | 97.79535358582928 | 97.6734515747083 | 96.94324405151447 | 96.63425851943464 | 1.8749999999999998 | 3394.5611822605574 |
| outputs_24h_core_eval | 24.0 | 8 | 9.323152269934997 | 0.0 | 4.731062186988869 | 0.0004953038001694035 | 4.321279401968584 | 0.0004820402572361656 | 0.4097827850202851 | 1.3263542933237876e-05 | 93.83863826815441 | 93.6202496256576 | 90.69932444197187 | 90.52793488821585 | 3.7673611111111107 | 2504.3229361753233 |

## Smoke / Regression Summary

| result_dir | category | signature_group | hours | seed_count | has_runtime | has_publication | publication_holdout_valid | proposed_ramp95 | proposed_cap_violation_pct | proposed_throughput_kwh |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| outputs_24h_eval_retry | redundant_retry | 3 | 24.0 | 2 | True | False | None | 9.323152269934997 | 0.0 | 4.731062186988869 |
| publication_smoke | smoke_regression | 6 | 6.0 | 1 | False | True | False | 9.456311658167252 | 0.0 | 0.0185328279620512 |
| publication_smoke2 | smoke_regression | 6 | 6.0 | 1 | False | True | False | 9.456311658167252 | 0.0 | 0.0185328279620512 |
| publication_smoke3 | smoke_regression | 7 | 6.0 | 1 | True | True | False | 9.456311658167252 | 0.0 | 0.0170733942569962 |
| publication_smoke4 | smoke_regression | 7 | 6.0 | 1 | True | True | False | 9.456311658167252 | 0.0 | 0.0170733942569962 |
| review_codex_smoke | smoke_regression | 7 | 6.0 | 1 | True | False | False | 9.456311658167252 | 0.0 | 0.0170733942569962 |
| review_codex_smoke_pub | smoke_regression | 7 | 6.0 | 1 | True | True | False | 9.456311658167252 | 0.0 | 0.0170733942569962 |
| review_codex_smoke_v2 | smoke_regression | 7 | 6.0 | 1 | True | True | False | 9.456311658167252 | 0.0 | 0.0170733942569962 |
| review_smoke | smoke_regression | 8 | 6.0 | 1 | False | False | False | 9.456311658167252 | 0.0 | 0.0272894301923812 |
| review_smoke_after_fix | smoke_regression | 8 | 6.0 | 1 | False | False | False | 9.456311658167252 | 0.0 | 0.0272894301923812 |
| review_smoke_after_fix2 | smoke_regression | 8 | 6.0 | 1 | False | False | False | 9.456311658167252 | 0.0 | 0.0272894301923812 |

## Parameter Stability Top-8

| candidate | base_soft_low | prep_power_cap_kw | lookahead_gain | min_useful_cmd_kw | mean_hold_score_vs_gr | std_hold_score_vs_gr | mean_hold_rank | mean_hold_cap_delta_vs_gr | mean_hold_throughput_delta_vs_gr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Candidate_01 | 0.32 | 3.0 | 0.01 | 0.25 | 0.0576330794736153 | 0.110862573665371 | 1.0 | 0.0 | 0.2053426080930576 |
| Candidate_02 | 0.32 | 4.0 | 0.01 | 0.25 | 0.0594725909681869 | 0.1127294712401628 | 1.6666666666666667 | 0.0 | 0.2164836255418785 |
| Candidate_03 | 0.32 | 5.0 | 0.01 | 0.25 | 0.0621797356333706 | 0.1155975277068599 | 2.333333333333333 | 0.0 | 0.2275753625858516 |
| Candidate_05 | 0.32 | 4.0 | 0.01 | 0.5 | 0.0789642447870821 | 0.1042545915296673 | 6.666666666666667 | 0.0 | 0.2153625693898875 |
| Candidate_04 | 0.32 | 4.0 | 0.02 | 0.25 | 0.0888298615495524 | 0.1294127320317235 | 6.0 | 0.0 | 0.2784906664529045 |
| Candidate_07 | 0.34 | 4.0 | 0.01 | 0.25 | 0.1705576520154115 | 0.2096421192786106 | 4.333333333333333 | 0.0 | 0.3175859393440901 |
| Candidate_06 | 0.34 | 3.0 | 0.01 | 0.25 | 0.2009672404781761 | 0.2381639049636356 | 5.0 | 0.0 | 0.302407435310919 |
| Candidate_08 | 0.34 | 4.0 | 0.02 | 0.25 | 0.2240867918566236 | 0.253956135826395 | 8.166666666666666 | 0.0 | 0.3967063298607867 |

## Full Catalog

| result_dir | category | evidence_role | hours | scenario_count | seed_count | profiles | file_count | has_manifest | has_main_metrics | has_runtime | has_publication | has_figures | has_claims_by_scenario | publication_holdout_valid | proposed_ramp95 | proposed_cap_violation_pct | proposed_throughput_kwh | proposed_lfp_cycle_loss_pct | gr_ramp95 | gr_cap_violation_pct | gr_throughput_kwh | gr_lfp_cycle_loss_pct | rs_throughput_kwh | rs_lfp_cycle_loss_pct | fbrl_throughput_kwh | fbrl_lfp_cycle_loss_pct | nc_cap_violation_pct | mpc_ramp95 | mpc_cap_violation_pct | mpc_lfp_cycle_loss_pct | proposed_mean_cpu_ms | mpc_mean_cpu_ms | signature_group |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| outputs_24h_core_eval | primary_postfix | Independent benchmark evidence | 24.0 | 4 | 2 | 8 | 16 | True | True | True | False | False | True | None | 9.323152269934997 | 0.0 | 4.731062186988869 | 0.0004953038001694035 | 9.317549684518905 | 0.0 | 4.321279401968584 | 0.0004820402572361656 | 76.78598324354049 | 0.005325460468749163 | 74.15748123964063 | 0.005229100458285476 | 3.7673611111111107 | 9.350477760608637 | 2.3784722222222223 | 0.00038064362590026495 | 0.3247233848317895 | 813.2122205467365 | 1 |
| outputs_24h_eval | incomplete | Discarded incomplete early run | nan | 0 | 0 | 0 | 1 | False | False | False | False | True | False | None | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 2 |
| outputs_24h_eval_retry | redundant_retry | Redundant 24 h retry / regression evidence | 24.0 | 4 | 2 | 8 | 36 | True | True | True | False | True | True | None | 9.323152269934997 | 0.0 | 4.731062186988869 | nan | 9.317549684518905 | 0.0 | 4.321279401968584 | nan | 76.7859832435405 | nan | 74.15748123964062 | nan | 3.7673611111111107 | 9.350477760608637 | 2.3784722222222223 | nan | 0.302541727857412 | 816.154472916757 | 3 |
| outputs_compact_full | primary_postfix | Independent benchmark evidence | 6.0 | 2 | 2 | 4 | 50 | True | True | True | True | True | True | None | 9.602083810067544 | 0.0 | 0.0085366971284981 | 6.199837535863728e-07 | 9.602083810067544 | 0.0 | 0.0078069802759706 | 5.669778923320188e-07 | 18.703393790110795 | 0.00103939256070205 | 17.47434131823904 | 0.0009581003340946 | 0.1388888888888889 | 9.633404845418125 | 0.1388888888888889 | 1.0804041835119123e-06 | 0.2897149987499385 | 944.9932268747136 | 4 |
| outputs_cross_benchmark_evidence | derived_audit | Derived audit / secondary evidence | nan | 0 | 0 | 0 | 3 | False | False | False | False | False | False | None | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 2 |
| outputs_medium_full | primary_postfix | Independent benchmark evidence | 12.0 | 4 | 2 | 8 | 36 | True | True | True | False | True | True | None | 9.032893028441366 | 0.0 | 0.8052375703616899 | 7.583560335042573e-05 | 9.033668234671568 | 0.0 | 0.7278377926904847 | 7.64706012845945e-05 | 36.524567621632755 | 0.002480917830159075 | 34.61082355338148 | 0.0022531618601226372 | 1.8749999999999998 | 9.124440865848086 | 1.25 | 5.937332044665945e-05 | 0.3474491146941242 | 1179.4372775514703 | 5 |
| outputs_parameter_audit | derived_audit | Derived audit / secondary evidence | nan | 0 | 0 | 0 | 10 | False | False | False | False | False | False | None | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 2 |
| publication_smoke | smoke_regression | Smoke / regression verification | 6.0 | 1 | 1 | 1 | 32 | True | True | False | True | True | False | False | 9.456311658167252 | 0.0 | 0.0185328279620512 | nan | 9.456311658167252 | 0.0 | 0.0156139605519412 | nan | 18.793187335809808 | nan | 17.84176029964619 | nan | 0.2777777777777778 | 9.518953728868407 | 0.2777777777777778 | nan | nan | nan | 6 |
| publication_smoke2 | smoke_regression | Smoke / regression verification | 6.0 | 1 | 1 | 1 | 42 | True | True | False | True | True | False | False | 9.456311658167252 | 0.0 | 0.0185328279620512 | nan | 9.456311658167252 | 0.0 | 0.0156139605519412 | nan | 18.793187335809808 | nan | 17.84176029964619 | nan | 0.2777777777777778 | 9.518953728868407 | 0.2777777777777778 | nan | nan | nan | 6 |
| publication_smoke3 | smoke_regression | Smoke / regression verification | 6.0 | 1 | 1 | 1 | 50 | True | True | True | True | True | True | False | 9.456311658167252 | 0.0 | 0.0170733942569962 | nan | 9.456311658167252 | 0.0 | 0.0156139605519412 | nan | 18.793187335809808 | nan | 17.84176029964619 | nan | 0.2777777777777778 | 9.518953728868407 | 0.2777777777777778 | nan | 0.1592408387093908 | 514.8043999978755 | 7 |
| publication_smoke4 | smoke_regression | Smoke / regression verification | 6.0 | 1 | 1 | 1 | 50 | True | True | True | True | True | True | False | 9.456311658167252 | 0.0 | 0.0170733942569962 | nan | 9.456311658167252 | 0.0 | 0.0156139605519412 | nan | 18.793187335809808 | nan | 17.84176029964619 | nan | 0.2777777777777778 | 9.518953728868407 | 0.2777777777777778 | nan | 0.1802516674312452 | 506.7070347231089 | 7 |
| review_codex_smoke | smoke_regression | Smoke / regression verification | 6.0 | 1 | 1 | 1 | 36 | True | True | True | False | True | True | False | 9.456311658167252 | 0.0 | 0.0170733942569962 | nan | 9.456311658167252 | 0.0 | 0.0156139605519412 | nan | 18.793187335809808 | nan | 17.84176029964619 | nan | 0.2777777777777778 | 9.51906594523909 | 0.2777777777777778 | nan | 0.1285341669346154 | 480.1837599999999 | 7 |
| review_codex_smoke_pub | smoke_regression | Smoke / regression verification | 6.0 | 1 | 1 | 1 | 50 | True | True | True | True | True | True | False | 9.456311658167252 | 0.0 | 0.0170733942569962 | nan | 9.456311658167252 | 0.0 | 0.0156139605519412 | nan | 18.793187335809808 | nan | 17.84176029964619 | nan | 0.2777777777777778 | 9.51906594523909 | 0.2777777777777778 | nan | 0.1363363884593127 | 514.6159319442733 | 7 |
| review_codex_smoke_v2 | smoke_regression | Smoke / regression verification | 6.0 | 1 | 1 | 1 | 50 | True | True | True | True | True | True | False | 9.456311658167252 | 0.0 | 0.0170733942569962 | nan | 9.456311658167252 | 0.0 | 0.0156139605519412 | nan | 18.793187335809808 | nan | 17.84176029964619 | nan | 0.2777777777777778 | 9.51906594523909 | 0.2777777777777778 | nan | 0.1319086110419852 | 573.6918036112911 | 7 |
| review_smoke | smoke_regression | Smoke / regression verification | 6.0 | 1 | 1 | 1 | 27 | True | True | False | False | True | False | False | 9.456311658167252 | 0.0 | 0.0272894301923812 | nan | 9.456311658167252 | 0.0 | 0.0156139605519412 | nan | 18.793187335809808 | nan | 17.84176029964619 | nan | 0.2777777777777778 | 9.518615623734876 | 0.2777777777777778 | nan | nan | nan | 8 |
| review_smoke_after_fix | smoke_regression | Smoke / regression verification | 6.0 | 1 | 1 | 1 | 28 | True | True | False | False | True | False | False | 9.456311658167252 | 0.0 | 0.0272894301923812 | nan | 9.456311658167252 | 0.0 | 0.0156139605519412 | nan | 18.793187335809808 | nan | 17.84176029964619 | nan | 0.2777777777777778 | 9.525704620284923 | 0.2777777777777778 | nan | nan | nan | 8 |
| review_smoke_after_fix2 | smoke_regression | Smoke / regression verification | 6.0 | 1 | 1 | 1 | 28 | True | True | False | False | True | False | False | 9.456311658167252 | 0.0 | 0.0272894301923812 | nan | 9.456311658167252 | 0.0 | 0.0156139605519412 | nan | 18.793187335809808 | nan | 17.84176029964619 | nan | 0.2777777777777778 | 9.518953728868407 | 0.2777777777777778 | nan | nan | nan | 8 |