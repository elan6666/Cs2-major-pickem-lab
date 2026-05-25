# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_vrs_tier_scoreline_weighted_finetune_2026-05-25.json`
- model: `catboost`
- model_target: `advanced`
- feature_snapshot: `data/snapshots/iem_cologne_major_2026_stage1_vrs_tier_scoreline_features_2026-05-25.csv`
- score_column: `feature_score`
- stage_name: `Stage 1`
- advance_label: `晋级(3-1/3-2)`
- simulations: `10000`
- seed: `42`
- scale: `120.0`
- effective_scale: `150.0`
- bo1_shrink: `0.7`
- effective_bo1_shrink: `0.55`
- bo3_shrink: `1.0`
- effective_bo3_shrink: `0.9`
- veto_weight: `1.0`
- calibration_json: `reports/stage1_factor_veto_calibration.json`
- all_bo3: `False`
- map_stats: `data/bo3/bo3_stage1_last4months_vrs_tier_scoreline_map_stats_2026-05-25.csv`
- map_pool: `Ancient, Anubis, Dust2, Inferno, Mirage, Nuke, Overpass`
- veto_policy: `contextual-bandit`
- bandit_policy_json: `reports/models/bo3_two_layer_veto_bandit_policy_2026-05-25.json`
- catboost_metadata: `{'model_path': 'reports/models/bo3_stage1_catboost_vrs_tier_scoreline_weighted_finetune_2026-05-25.cbm', 'stage1_training_mode': 'last_4_month_bo3_pretrain', 'stage2_training_mode': 'austin_budapest_major_calibration_weighted_pairwise_with_vrs_tier_scoreline_features', 'example_count': 1924}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: BIG, BetBoom
- 0-3: Lynn Vision, NRG
- 晋级(3-1/3-2): MIBR, THUNDER dOWNUNDER, SINNERS, FlyQuest, HEROIC, GamerLegion
- 预计通过概率: 45.0%
- 期望猜中数: 4.33

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级(3-1/3-2) | 总晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| BIG | 5 | 162.1 | 34.9% | 30.5% | 22.5% | 53.0% | 87.9% | 5.6% | 4.9% | 1.7% | 3-0 |
| MIBR | 7 | 120.6 | 22.0% | 30.6% | 28.1% | 58.6% | 80.7% | 9.0% | 7.4% | 2.9% | 3-1 |
| BetBoom | 4 | 97.7 | 23.7% | 27.7% | 23.4% | 51.0% | 74.8% | 11.9% | 10.0% | 3.3% | 3-1 |
| THUNDER dOWNUNDER | 15 | 104.3 | 16.0% | 26.8% | 28.8% | 55.6% | 71.6% | 12.9% | 10.8% | 4.7% | 3-2 |
| SINNERS | 8 | 66.3 | 14.8% | 25.1% | 25.5% | 50.7% | 65.5% | 15.8% | 12.9% | 5.8% | 3-2 |
| FlyQuest | 16 | 71.2 | 14.0% | 23.6% | 26.9% | 50.5% | 64.5% | 15.7% | 13.6% | 6.3% | 3-2 |
| GamerLegion | 1 | 37.7 | 16.4% | 23.5% | 21.5% | 45.0% | 61.4% | 19.9% | 13.5% | 5.3% | 3-1 |
| HEROIC | 3 | 49.7 | 13.2% | 23.2% | 23.7% | 46.9% | 60.1% | 17.4% | 15.5% | 7.0% | 3-2 |
| TYLOO | 10 | 13.8 | 11.4% | 20.4% | 21.6% | 42.0% | 53.4% | 21.8% | 17.2% | 7.6% | 2-3 |
| Sharks | 11 | 23.1 | 10.0% | 19.1% | 22.1% | 41.2% | 51.2% | 20.5% | 18.8% | 9.5% | 3-2 |
| M80 | 6 | 3.6 | 11.6% | 18.9% | 19.2% | 38.1% | 49.6% | 24.0% | 19.2% | 7.1% | 2-3 |
| B8 | 2 | -53.9 | 4.9% | 11.7% | 12.5% | 24.2% | 29.1% | 28.2% | 26.9% | 15.8% | 2-3 |
| Liquid | 13 | -98.8 | 2.6% | 7.3% | 9.7% | 17.0% | 19.7% | 25.2% | 29.7% | 25.5% | 1-3 |
| Gaimin Gladiators | 12 | -153.8 | 1.7% | 4.7% | 5.7% | 10.4% | 12.2% | 23.8% | 33.5% | 30.6% | 1-3 |
| NRG | 9 | -174.2 | 1.5% | 3.8% | 4.5% | 8.4% | 9.8% | 24.5% | 32.7% | 32.9% | 0-3 |
| Lynn Vision | 14 | -193.4 | 1.2% | 3.0% | 4.3% | 7.4% | 8.6% | 23.9% | 33.3% | 34.2% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
- Pick'Em 计分严格按槽位判断：3-0 槽只认 3-0，晋级槽只认 3-1/3-2，0-3 槽只认 0-3。
