# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_pairwise_complete_2026-05-25.json`
- model: `catboost`
- model_target: `advanced`
- feature_snapshot: `data/snapshots/iem_cologne_major_2026_stage1_factor_weights_trained_2026-05-23.csv`
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
- map_stats: `data/bo3/bo3_stage1_last4months_map_stats_complete_2026-05-25.csv`
- map_pool: `Ancient, Anubis, Dust2, Inferno, Mirage, Nuke, Overpass`
- veto_policy: `contextual-bandit`
- bandit_policy_json: `reports/models/bo3_true_veto_bandit_policy_complete_2026-05-25.json`
- catboost_metadata: `{'model_path': 'reports/models/bo3_stage1_catboost_pairwise_complete_2026-05-25.cbm', 'stage1_training_mode': 'last_4_month_bo3_pretrain', 'stage2_training_mode': 'austin_budapest_major_calibration_weighted_pairwise', 'example_count': 1924}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: SINNERS, HEROIC
- 0-3: Lynn Vision, Liquid
- 晋级: BIG, BetBoom, GamerLegion, B8, M80, MIBR
- 预计通过概率: 59.3%
- 期望猜中数: 4.79

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| BIG | 5 | 63.0 | 23.3% | 27.7% | 24.2% | 75.2% | 11.2% | 9.4% | 4.2% | 3-1 |
| BetBoom | 4 | 60.2 | 20.5% | 26.6% | 23.7% | 70.8% | 12.4% | 11.4% | 5.4% | 3-1 |
| GamerLegion | 1 | 46.6 | 20.8% | 25.8% | 22.5% | 69.1% | 14.0% | 11.5% | 5.4% | 3-1 |
| SINNERS | 8 | 39.9 | 18.1% | 24.8% | 23.3% | 66.2% | 14.7% | 13.0% | 6.1% | 3-1 |
| HEROIC | 3 | 53.7 | 18.1% | 25.0% | 22.8% | 65.8% | 14.7% | 13.1% | 6.4% | 3-1 |
| B8 | 2 | 57.9 | 17.8% | 25.3% | 22.1% | 65.2% | 16.0% | 12.2% | 6.6% | 3-1 |
| M80 | 6 | 17.0 | 15.5% | 22.5% | 21.1% | 59.1% | 17.5% | 15.7% | 7.7% | 3-1 |
| MIBR | 7 | -10.3 | 13.4% | 20.0% | 21.3% | 54.7% | 18.9% | 17.3% | 9.2% | 3-2 |
| TYLOO | 10 | -3.9 | 10.3% | 18.9% | 20.4% | 49.6% | 19.7% | 18.8% | 11.9% | 3-2 |
| Sharks | 11 | -13.9 | 8.5% | 15.4% | 18.0% | 41.8% | 20.9% | 22.4% | 14.9% | 1-3 |
| FlyQuest | 16 | -48.3 | 6.1% | 12.3% | 15.7% | 34.1% | 22.7% | 23.7% | 19.5% | 1-3 |
| THUNDER dOWNUNDER | 15 | -38.9 | 6.7% | 12.6% | 14.6% | 33.9% | 22.9% | 25.2% | 18.0% | 1-3 |
| Gaimin Gladiators | 12 | -47.6 | 6.4% | 12.5% | 14.5% | 33.4% | 23.8% | 25.1% | 17.6% | 1-3 |
| NRG | 9 | -48.8 | 6.1% | 11.8% | 13.7% | 31.6% | 23.2% | 26.3% | 18.8% | 1-3 |
| Liquid | 13 | -57.4 | 5.2% | 11.1% | 12.9% | 29.2% | 23.0% | 25.7% | 22.1% | 1-3 |
| Lynn Vision | 14 | -83.7 | 3.2% | 7.8% | 9.3% | 20.3% | 24.2% | 29.3% | 26.2% | 1-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
