# BO3 CatBoost Pretrain Dataset

- Matches input: `data/bo3/bo3_stage1_last4months_matches_complete_2026-05-25.csv`
- Maps input: `data/bo3/bo3_stage1_last4months_maps_complete_2026-05-25.csv`
- Output: `data/bo3/bo3_stage1_last4months_catboost_vrs_tier_scoreline_pretrain_2026-05-25.csv`
- Featureized rows: `1500`
- Rows with veto sequence: `1500`
- Teams with directed rows: `91`

## Notes

Rows are directed pairwise map examples built from BO3.gg match/map results. Current Cologne Stage 1 teams use the factor snapshot; VRS Top 100 opponents outside the snapshot use conservative VRS/BO3 rank defaults so the 16 teams can still learn from broader recent opposition.
