# Publication Audit

## Scope

This audit reports the canonical train/hold-out split together with repeated-split stability checks for the Proposed controller.
Its goal is not to guarantee publication; it documents how defensible the controller claims are under repeatable selection and hold-out checks.

## Canonical Split

- Train seeds: `[0, 2, 4]`
- Hold-out seeds: `[1, 3]`
- Hold-out validity: `valid`

## Selected Candidate

- Candidate label: `Candidate_01`
- Canonical train score vs GR: `-0.1204`
- Repeated-split mean hold score vs GR: `-0.0225`
- Repeated-split std hold score vs GR: `0.1545`
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

| candidate | base_soft_low | prep_power_cap_kw | lookahead_gain | min_useful_cmd_kw | mean_train_score_vs_gr | mean_hold_score_vs_gr | std_hold_score_vs_gr | max_hold_score_vs_gr | mean_hold_rank | best_hold_rank_count | mean_hold_ramp_delta_vs_gr | mean_hold_cap_delta_vs_gr | mean_hold_throughput_delta_vs_gr | mean_hold_lfp_cycle_loss_delta_vs_gr | mean_hold_idod_delta_vs_gr | mean_hold_flip_delta_vs_gr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Candidate_01 | 0.32 | 3.0 | 0.01 | 0.25 | -0.0180283939779391 | -0.02248715318417712 | 0.15447991641098704 | 0.18927889552794772 | 1.0 | 5 | 0.000741982372589689 | 0.0 | 0.3821072448348174 | 4.309181106052272e-05 | -0.00011674595687294867 | -2.2 |
| Candidate_02 | 0.32 | 4.0 | 0.01 | 0.25 | -0.014989740296736956 | -0.019661526375989342 | 0.15568615873526903 | 0.19322070587345883 | 2.0 | 0 | 0.0024626042663051352 | 0.0 | 0.3959250137226412 | 4.515500083321509e-05 | -0.00011473845430606373 | -2.25 |
| Candidate_03 | 0.32 | 5.0 | 0.01 | 0.25 | -0.011503690049008258 | -0.016697559830013115 | 0.15821948045987244 | 0.199021730155995 | 3.0 | 0 | 0.0024626042663051352 | 0.0 | 0.4082185920990259 | 4.488275161577198e-05 | -0.00011619749494766297 | -2.25 |
| Candidate_05 | 0.32 | 4.0 | 0.01 | 0.5 | 0.003620958502218072 | -0.0040091180744730006 | 0.1546045974577984 | 0.20493747545901095 | 4.0 | 0 | 0.0024626042663051352 | 0.0 | 0.39124812063235515 | 3.622579059664524e-05 | -0.0001793389222071151 | -1.8166666666666658 |
| Candidate_04 | 0.32 | 4.0 | 0.02 | 0.25 | 0.04709806073244183 | 0.043883378309051244 | 0.1462303552732 | 0.24950963920131736 | 5.0 | 0 | 0.00041552916898872637 | 0.0 | 0.526863754937887 | 7.84629242539183e-05 | 0.00015669213874121036 | -2.0 |

## Hold-out Main Means

| Controller | Ramp95 | CapViolPct | Throughput | EFC | LFP_CycleLossPct | HighSOCDwell | HighCExposure | IDOD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FBRL | 2.48 (0.13) | 0.00 (0.00) | 74.13 (2.91) | 0.37 (0.01) | 0.0054 (0.0008) | 0.00 (0.00) | 0.00 (0.00) | 0.0056 (0.0045) |
| GR | 9.29 (0.43) | 0.00 (0.00) | 5.55 (5.45) | 0.03 (0.03) | 0.0006 (0.0006) | 0.00 (0.00) | 0.00 (0.00) | 0.0019 (0.0023) |
| NC | 9.46 (0.37) | 4.92 (4.51) | 0.00 (0.00) | 0.00 (0.00) | 0.0000 (0.0000) | 0.00 (0.00) | 0.00 (0.00) | 0.0000 (0.0000) |
| Proposed | 9.29 (0.42) | 0.00 (0.00) | 5.93 (5.85) | 0.03 (0.03) | 0.0006 (0.0006) | 0.00 (0.00) | 0.00 (0.00) | 0.0018 (0.0018) |
| RS | 3.07 (0.12) | 3.72 (3.97) | 76.19 (2.29) | 0.38 (0.01) | 0.0053 (0.0001) | 0.00 (0.00) | 0.00 (0.00) | 0.0024 (0.0001) |

## Hold-out Claim Audit

| Reference | Baseline | Pairs | ramp95_kw_per_min_delta_mean | ramp95_kw_per_min_wins | ramp95_kw_per_min_ties | ramp95_kw_per_min_losses | cap_violation_pct_total_delta_mean | cap_violation_pct_total_wins | cap_violation_pct_total_ties | cap_violation_pct_total_losses | throughput_kwh_delta_mean | throughput_kwh_wins | throughput_kwh_ties | throughput_kwh_losses | lfp_cycle_loss_pct_delta_mean | lfp_cycle_loss_pct_wins | lfp_cycle_loss_pct_ties | lfp_cycle_loss_pct_losses | idod_delta_mean | idod_wins | idod_ties | idod_losses | flip_per_day_delta_mean | flip_per_day_wins | flip_per_day_ties | flip_per_day_losses | all4_nonworse_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Proposed | NC | 8 | -0.17347495336253216 | 7 | 1 | 0 | -4.921875 | 8 | 0 | 0 | 5.93188650662878 | 0 | 0 | 8 | 0.0006442783342725405 | 0 | 0 | 8 | 0.0017923877352520458 | 0 | 0 | 8 | 49.5 | 0 | 0 | 8 | 0 |
| Proposed | GR | 8 | -0.0016490188870463829 | 2 | 4 | 2 | 0.0 | 0 | 8 | 0 | 0.38086128272118946 | 0 | 0 | 8 | 4.532290056017372e-05 | 1 | 0 | 7 | -0.00010809836892924218 | 1 | 0 | 7 | -0.25 | 4 | 3 | 1 | 0 |
| Proposed | RS | 8 | 6.216988119266754 | 0 | 0 | 8 | -3.7152777777777777 | 6 | 2 | 0 | -70.26274307709255 | 8 | 0 | 0 | -0.004682863050795772 | 8 | 0 | 0 | -0.000588243332464662 | 5 | 0 | 3 | -501.0 | 8 | 0 | 0 | 0 |
| Proposed | FBRL | 8 | 6.802900127152792 | 0 | 0 | 8 | 0.0 | 0 | 8 | 0 | -68.19370799998393 | 8 | 0 | 0 | -0.004787906434933984 | 8 | 0 | 0 | -0.003761631299085519 | 8 | 0 | 0 | -469.375 | 8 | 0 | 0 | 0 |

## Hold-out Claim Audit By Scenario

| Scenario | Reference | Baseline | Pairs | ramp95_kw_per_min_delta_mean | ramp95_kw_per_min_wins | ramp95_kw_per_min_ties | ramp95_kw_per_min_losses | cap_violation_pct_total_delta_mean | cap_violation_pct_total_wins | cap_violation_pct_total_ties | cap_violation_pct_total_losses | throughput_kwh_delta_mean | throughput_kwh_wins | throughput_kwh_ties | throughput_kwh_losses | lfp_cycle_loss_pct_delta_mean | lfp_cycle_loss_pct_wins | lfp_cycle_loss_pct_ties | lfp_cycle_loss_pct_losses | idod_delta_mean | idod_wins | idod_ties | idod_losses | flip_per_day_delta_mean | flip_per_day_wins | flip_per_day_ties | flip_per_day_losses | all4_nonworse_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cloud_edge | Proposed | NC | 2 | -0.25216660435555127 | 2 | 0 | 0 | -5.173611111111112 | 2 | 0 | 0 | 6.111940554821561 | 0 | 0 | 2 | 0.0006797734884112901 | 0 | 0 | 2 | 0.0014668499727997053 | 0 | 0 | 2 | 52.0 | 0 | 0 | 2 | 0 |
| cloud_edge | Proposed | GR | 2 | 0.0040207672431158414 | 1 | 0 | 1 | 0.0 | 0 | 2 | 0 | 0.31294905330374573 | 0 | 0 | 2 | 8.54267845240291e-05 | 0 | 0 | 2 | -0.0014984973306274671 | 1 | 0 | 1 | -3.0 | 1 | 1 | 0 | 0 |
| cloud_edge | Proposed | RS | 2 | 6.15312362971277 | 0 | 0 | 2 | -4.027777777777778 | 1 | 1 | 0 | -70.01624749483881 | 2 | 0 | 0 | -0.004635227853513918 | 2 | 0 | 0 | -0.0008750855089405523 | 1 | 0 | 1 | -491.0 | 2 | 0 | 0 | 0 |
| cloud_edge | Proposed | FBRL | 2 | 6.73598708058754 | 0 | 0 | 2 | 0.0 | 0 | 2 | 0 | -67.90451065992573 | 2 | 0 | 0 | -0.004678489398877856 | 2 | 0 | 0 | -0.004044024888699432 | 2 | 0 | 0 | -457.0 | 2 | 0 | 0 | 0 |
| load_step | Proposed | NC | 2 | -0.31043286743228116 | 2 | 0 | 0 | -8.159722222222221 | 2 | 0 | 0 | 10.999771603253038 | 0 | 0 | 2 | 0.0011292726147877935 | 0 | 0 | 2 | 0.0034916219152699465 | 0 | 0 | 2 | 81.0 | 0 | 0 | 2 | 0 |
| load_step | Proposed | GR | 2 | -0.010616842791301373 | 1 | 0 | 1 | 0.0 | 0 | 2 | 0 | 0.8496765409044373 | 0 | 0 | 2 | 2.098553953012712e-06 | 1 | 0 | 1 | 0.0004006816318539257 | 0 | 0 | 2 | 6.0 | 1 | 0 | 1 | 0 |
| load_step | Proposed | RS | 2 | 6.177802600631989 | 0 | 0 | 2 | -6.527777777777778 | 2 | 0 | 0 | -64.14561761245821 | 2 | 0 | 0 | -0.004168394280793575 | 2 | 0 | 0 | 0.0010411459427818424 | 1 | 0 | 1 | -467.5 | 2 | 0 | 0 | 0 |
| load_step | Proposed | FBRL | 2 | 6.828944881819063 | 0 | 0 | 2 | 0.0 | 0 | 2 | 0 | -65.62525810728657 | 2 | 0 | 0 | -0.005058827803423949 | 2 | 0 | 0 | -0.006364162876773903 | 2 | 0 | 0 | -445.5 | 2 | 0 | 0 | 0 |
| mixed | Proposed | NC | 2 | -0.06338670108718869 | 2 | 0 | 0 | -3.8194444444444446 | 2 | 0 | 0 | 3.87776744587724 | 0 | 0 | 2 | 0.0004564963165103989 | 0 | 0 | 2 | 0.001409981992378797 | 0 | 0 | 2 | 40.0 | 0 | 0 | 2 | 0 |
| mixed | Proposed | GR | 2 | 0.0 | 0 | 2 | 0 | 0.0 | 0 | 2 | 0 | 0.21208569683960216 | 0 | 0 | 2 | 5.9327240730081725e-05 | 0 | 0 | 2 | 0.0005315720533761544 | 0 | 0 | 2 | -2.0 | 1 | 1 | 0 | 0 |
| mixed | Proposed | RS | 2 | 6.035772921174892 | 0 | 0 | 2 | -2.5694444444444446 | 2 | 0 | 0 | -71.43129713503012 | 2 | 0 | 0 | -0.0048568891809740375 | 2 | 0 | 0 | -0.0009305944590109185 | 1 | 0 | 1 | -505.0 | 2 | 0 | 0 | 0 |
| mixed | Proposed | FBRL | 2 | 6.566804636426936 | 0 | 0 | 2 | 0.0 | 0 | 2 | 0 | -67.87547693341483 | 2 | 0 | 0 | -0.004680028540783065 | 2 | 0 | 0 | -0.00232653293105502 | 2 | 0 | 0 | -473.5 | 2 | 0 | 0 | 0 |
| wind_gust | Proposed | NC | 2 | -0.06791364057510751 | 1 | 1 | 0 | -2.5347222222222223 | 2 | 0 | 0 | 2.738066422563282 | 0 | 0 | 2 | 0.0003115709173806791 | 0 | 0 | 2 | 0.0008010970605597348 | 0 | 0 | 2 | 25.0 | 0 | 0 | 2 | 0 |
| wind_gust | Proposed | GR | 2 | 0.0 | 0 | 2 | 0 | 0.0 | 0 | 2 | 0 | 0.14873383983697264 | 0 | 0 | 2 | 3.4439023033571334e-05 | 0 | 0 | 2 | 0.0001338501696804183 | 0 | 0 | 2 | -2.0 | 1 | 1 | 0 | 0 |
| wind_gust | Proposed | RS | 2 | 6.501253325547369 | 0 | 0 | 2 | -1.7361111111111112 | 1 | 1 | 0 | -75.45781006604307 | 2 | 0 | 0 | -0.005070940887901557 | 2 | 0 | 0 | -0.0015884393046890198 | 2 | 0 | 0 | -540.5 | 2 | 0 | 0 | 0 |
| wind_gust | Proposed | FBRL | 2 | 7.079863909777625 | 0 | 0 | 2 | 0.0 | 0 | 2 | 0 | -71.3695862993086 | 2 | 0 | 0 | -0.004734279996651065 | 2 | 0 | 0 | -0.0023118044998137206 | 2 | 0 | 0 | -501.5 | 2 | 0 | 0 | 0 |

## Hold-out Pairwise Stats

| metric | comparison | n_pairs | mean_paired_diff | ci95_lo | ci95_hi | p_value | effect_size | effect_name | direction | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ramp95_kw_per_min | Proposed vs NC | 8 | -0.17347495336253216 | -0.29791234525569965 | -0.060787638647011644 | 0.015625 | -1.0 | Rank_biserial | left_better | 0.078125 |
| cap_violation_pct_total | Proposed vs NC | 8 | -4.921875 | -7.899739583333333 | -2.204210069444448 | 0.01765656400230381 | -1.0911989370376067 | Cohen_dz | left_better | 0.078125 |
| throughput_kwh | Proposed vs NC | 8 | 5.93188650662878 | 2.4061636261279893 | 9.763529643820254 | 0.024013495016522512 | 1.014476847503215 | Cohen_dz | right_better | 0.078125 |
| lfp_cycle_loss_pct | Proposed vs NC | 8 | 0.0006442783342725405 | 0.00026507930453761224 | 0.0010461268366880356 | 0.020841887698757413 | 1.049644852728362 | Cohen_dz | right_better | 0.078125 |
| idod | Proposed vs NC | 8 | 0.0017923877352520458 | 0.0007155236129687392 | 0.002992705573845382 | 0.026172319564610018 | 0.9932366402350922 | Cohen_dz | right_better | 0.078125 |
| flip_per_day | Proposed vs NC | 8 | 49.5 | 25.0 | 75.50624999999997 | 0.009586329709683667 | 1.248358908189543 | Cohen_dz | right_better | 0.057517978258102 |
| ramp95_kw_per_min | Proposed vs GR | 8 | -0.0016490188870463829 | -0.01138097491128831 | 0.007497547064407757 | 0.7662977505357391 | -0.10925662412943378 | Cohen_dz | left_better | 1.0 |
| cap_violation_pct_total | Proposed vs GR | 8 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| throughput_kwh | Proposed vs GR | 8 | 0.38086128272118946 | 0.15108785910692174 | 0.6892372662481099 | 0.0078125 | 1.0 | Rank_biserial | right_better | 0.046875 |
| lfp_cycle_loss_pct | Proposed vs GR | 8 | 4.532290056017372e-05 | -6.845132929722692e-06 | 9.414208356582355e-05 | 0.14361342867282095 | 0.582196402083825 | Cohen_dz | right_better | 0.7180671433641048 |
| idod | Proposed vs GR | 8 | -0.00010809836892924218 | -0.0010070649845852905 | 0.0005003248252999242 | 0.1953125 | 0.5555555555555556 | Rank_biserial | left_better | 0.78125 |
| flip_per_day | Proposed vs GR | 8 | -0.25 | -4.0 | 5.5 | 0.6875 | -0.3333333333333333 | Rank_biserial | left_better | 1.0 |
| ramp95_kw_per_min | Proposed vs RS | 8 | 6.216988119266754 | 5.953475602748402 | 6.447925039073845 | 6.63932415870054e-10 | 16.028458344374354 | Cohen_dz | right_better | 3.983594495220324e-09 |
| cap_violation_pct_total | Proposed vs RS | 8 | -3.7152777777777777 | -6.319878472222222 | -1.3802083333333335 | 0.033095465752326955 | -0.9357822258014276 | Cohen_dz | left_better | 0.06619093150465391 |
| throughput_kwh | Proposed vs RS | 8 | -70.26274307709255 | -74.76718323713969 | -65.60975544780821 | 2.024536144719864e-08 | -9.81234632554079 | Cohen_dz | left_better | 8.098144578879456e-08 |
| lfp_cycle_loss_pct | Proposed vs RS | 8 | -0.004682863050795772 | -0.005070586846001601 | -0.004272765924718194 | 1.429009752329547e-07 | -7.399705394673339 | Cohen_dz | left_better | 4.2870292569886416e-07 |
| idod | Proposed vs RS | 8 | -0.000588243332464662 | -0.0016327713356118411 | 0.0005691827959263814 | 0.36915403288850873 | -0.33932000610938734 | Cohen_dz | left_better | 0.36915403288850873 |
| flip_per_day | Proposed vs RS | 8 | -501.0 | -530.878125 | -471.125 | 1.0945400271962228e-08 | -10.720410337398368 | Cohen_dz | left_better | 5.472700135981114e-08 |
| ramp95_kw_per_min | Proposed vs FBRL | 8 | 6.802900127152792 | 6.577705148408641 | 7.001090760472167 | 1.137520496501009e-10 | 20.63497271040754 | Cohen_dz | right_better | 6.825122979006053e-10 |
| cap_violation_pct_total | Proposed vs FBRL | 8 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | NoDifference | tie | 1.0 |
| throughput_kwh | Proposed vs FBRL | 8 | -68.19370799998393 | -70.76450934998589 | -65.43557705307518 | 5.542255812816672e-10 | -16.448645186948056 | Cohen_dz | left_better | 2.2169023251266686e-09 |
| lfp_cycle_loss_pct | Proposed vs FBRL | 8 | -0.004787906434933984 | -0.004976288713548949 | -0.004618995874322464 | 3.378206018088128e-10 | -17.657400893828555 | Cohen_dz | left_better | 1.689103009044064e-09 |
| idod | Proposed vs FBRL | 8 | -0.003761631299085519 | -0.0057166295225019705 | -0.0022981790849472524 | 0.0078125 | -1.0 | Rank_biserial | left_better | 0.015625 |
| flip_per_day | Proposed vs FBRL | 8 | -469.375 | -505.75625 | -433.0 | 6.710546398312978e-08 | -8.254840884488535 | Cohen_dz | left_better | 2.0131639194938935e-07 |

## Interpretation

- `score_vs_gr < 0` means the selected candidate beats GR under the weighted publication score used by this audit.
- Repeated-split stability is stricter than a single split: lower mean hold score and lower variance imply a more robust candidate choice.
- The claim audit is stricter than the score: it reports per-metric delta means and win/tie/loss counts rather than a single scalar.
- A publishable manuscript still needs human-authored novelty positioning, related-work review, venue selection, and careful claim wording.