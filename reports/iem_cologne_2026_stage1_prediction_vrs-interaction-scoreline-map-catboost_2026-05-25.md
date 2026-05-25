# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_vrs_interaction_scoreline_weighted_finetune_2026-05-25.json`
- model: `catboost`
- model_target: `advanced`
- feature_snapshot: `data/snapshots/iem_cologne_major_2026_stage1_vrs_interaction_scoreline_features_2026-05-25.csv`
- score_column: `feature_score`
- stage_name: `Stage 1`
- advance_label: `晋级`
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
- map_stats: `data/bo3/bo3_stage1_last4months_vrs_interaction_scoreline_map_stats_2026-05-25.csv`
- map_pool: `Ancient, Anubis, Dust2, Inferno, Mirage, Nuke, Overpass`
- veto_policy: `contextual-bandit`
- bandit_policy_json: `reports/models/bo3_two_layer_veto_bandit_policy_2026-05-25.json`
- catboost_metadata: `{'model_path': 'reports/models/bo3_stage1_catboost_vrs_interaction_scoreline_weighted_finetune_2026-05-25.cbm', 'stage1_training_mode': 'last_4_month_bo3_pretrain', 'stage2_training_mode': 'austin_budapest_major_calibration_weighted_pairwise_with_vrs_interaction_scoreline_features', 'example_count': 1924}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: GamerLegion, HEROIC
- 0-3: Lynn Vision, NRG
- 晋级: BIG, MIBR, BetBoom, THUNDER dOWNUNDER, SINNERS, Sharks
- 预计通过概率: 77.6%
- 期望猜中数: 5.35

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| BIG | 5 | 167.4 | 33.6% | 30.2% | 23.0% | 86.9% | 6.1% | 5.3% | 1.8% | 3-0 |
| MIBR | 7 | 127.3 | 23.0% | 30.8% | 27.6% | 81.4% | 8.6% | 7.4% | 2.6% | 3-1 |
| BetBoom | 4 | 111.9 | 26.0% | 28.2% | 23.6% | 77.8% | 10.5% | 8.8% | 2.9% | 3-1 |
| THUNDER dOWNUNDER | 15 | 91.6 | 14.2% | 25.5% | 28.4% | 68.2% | 14.4% | 12.0% | 5.4% | 3-2 |
| SINNERS | 8 | 69.6 | 15.5% | 25.9% | 25.9% | 67.3% | 15.4% | 12.1% | 5.2% | 3-1 |
| HEROIC | 3 | 69.7 | 15.7% | 25.7% | 24.8% | 66.2% | 15.2% | 13.0% | 5.6% | 3-1 |
| GamerLegion | 1 | 30.3 | 16.1% | 22.9% | 21.2% | 60.2% | 20.3% | 13.9% | 5.6% | 3-1 |
| Sharks | 11 | 36.5 | 10.9% | 21.1% | 23.8% | 55.8% | 18.8% | 16.8% | 8.6% | 3-2 |
| FlyQuest | 16 | 38.1 | 10.4% | 20.4% | 24.4% | 55.2% | 19.6% | 17.0% | 8.2% | 3-2 |
| M80 | 6 | 17.8 | 13.1% | 20.8% | 20.3% | 54.2% | 21.9% | 17.8% | 6.1% | 2-3 |
| TYLOO | 10 | -15.0 | 8.5% | 17.3% | 19.5% | 45.3% | 24.9% | 20.1% | 9.7% | 2-3 |
| B8 | 2 | -50.6 | 6.0% | 13.1% | 14.5% | 33.7% | 27.7% | 25.0% | 13.7% | 2-3 |
| Liquid | 13 | -127.6 | 2.4% | 6.1% | 7.8% | 16.3% | 24.8% | 30.9% | 28.0% | 1-3 |
| Gaimin Gladiators | 12 | -167.0 | 1.6% | 4.6% | 5.7% | 11.9% | 23.3% | 33.8% | 31.0% | 1-3 |
| NRG | 9 | -181.1 | 1.6% | 4.1% | 5.0% | 10.7% | 25.0% | 33.1% | 31.2% | 1-3 |
| Lynn Vision | 14 | -195.1 | 1.2% | 3.2% | 4.4% | 8.9% | 23.3% | 33.3% | 34.5% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
