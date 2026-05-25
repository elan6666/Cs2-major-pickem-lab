# Stage 1 BO3 Data Self-Audit

Date: 2026-05-25

## Coverage

| Dataset | Matches | Maps | Matches with veto sequence | Missing veto sequence | Veto action rows |
|---|---:|---:|---:|---:|---:|
| 16 Stage 1 teams vs VRS Top 100, 2026-01-24 to 2026-05-24 | 375 | 861 | 375 | 0 | 2622 |
| Austin 2025 + Budapest 2025 Major coverage | 212 | 351 | 212 | 0 | 1484 |

## Training Inputs

| Artifact | Rows | Coverage |
|---|---:|---|
| `data/bo3/bo3_stage1_last4months_catboost_pretrain_complete_2026-05-25.csv` | 1500 | 91 directed teams, 1500 rows with veto sequence |
| `data/bo3/bo3_stage1_last4months_map_stats_complete_2026-05-25.csv` | 112 | 16 teams x 7 active maps |
| `data/bo3/bo3_stage1_last4months_veto_actions_complete_2026-05-25.csv` | 2622 | pick/ban/leftover action rows from BO3 match detail plus verified HLTV supplements |
| `data/bo3/bo3_major_veto_actions_complete_2026-05-25.csv` | 1484 | Austin 2025 Stage 1 + Budapest 2025 Stage 1 ordered veto actions |

## Source Completion

- BO3.gg match detail supplied most ordered `match_maps` sequences.
- 16 recent BO3 matches and 2 Major matches had no ordered veto sequence in the local BO3 detail payload.
- Those 18 gaps are now filled by `data/bo3/bo3_hltv_veto_sequence_supplement_2026-05-25.csv`, where every row points to the matching HLTV page and the exact numbered veto order.
- After applying the supplement, both match-level and map-level complete CSVs have zero blank `veto_sequence` values.

## Model Status

- First stage: BO3.gg near-4-month match/map pretrain, 1500 pairwise rows.
- Second stage: Austin 2025 Stage 1 + Budapest 2025 Stage 1 calibration/weighted pairwise training.
- Rating features: Glicko-style mean, uncertainty, and expected score features are included in CatBoost.
- Veto policy: contextual-bandit action policy trained from ordered BO3 veto actions.
- TrueSkill: not implemented in the runnable pipeline; current runnable rating layer is Glicko-style.

## Current Comparison

| Model | Pass probability | Expected correct | Recommended card |
|---|---:|---:|---|
| strict-real-catboost-complete-veto | 75.0% | 5.33 | 3-0 HEROIC/M80; 0-3 Lynn Vision/Sharks; advance BetBoom/B8/FlyQuest/TYLOO/Liquid/GamerLegion |
| vrs-complete-veto | 73.8% | 5.25 | 3-0 B8/HEROIC; 0-3 FlyQuest/THUNDER dOWNUNDER; advance BIG/GamerLegion/BetBoom/SINNERS/M80/TYLOO |
| factor-complete-veto | 63.7% | 4.91 | 3-0 M80/B8; 0-3 FlyQuest/Liquid; advance BIG/BetBoom/GamerLegion/HEROIC/SINNERS/TYLOO |
| bo3-catboost-complete-veto | 59.3% | 4.79 | 3-0 SINNERS/HEROIC; 0-3 Lynn Vision/Liquid; advance BIG/BetBoom/GamerLegion/B8/M80/MIBR |

## Remaining Boundaries

- BO3 public data still does not provide deeper feature families: T/CT split, economy rounds, player role metrics, resilience states, and same-roster head-to-head context.
- Current comparison is a prediction-output comparison, not a historical validation leaderboard.
- The data is now sufficient to train the requested runnable experimental chain: contextual bandit + Glicko-style features + CatBoost. It is not correct to describe the runnable chain as TrueSkill, because that component has not been implemented.
