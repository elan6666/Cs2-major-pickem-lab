# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_pairwise_complete_2026-05-25.json`
- model: `catboost`
- model_target: `advanced`
- feature_snapshot: `data/snapshots/iem_cologne_major_2026_stage1_factor_weights_trained_2026-05-25.csv`
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
- map_stats: `data/bo3/bo3_stage1_last4months_map_stats_complete_2026-05-25.csv`
- map_pool: `Ancient, Anubis, Dust2, Inferno, Mirage, Nuke, Overpass`
- veto_policy: `contextual-bandit`
- bandit_policy_json: `reports/models/bo3_two_layer_veto_bandit_policy_2026-05-25.json`
- catboost_metadata: `{'model_path': 'reports/models/bo3_stage1_catboost_pairwise_complete_2026-05-25.cbm', 'stage1_training_mode': 'last_4_month_bo3_pretrain', 'stage2_training_mode': 'austin_budapest_major_calibration_weighted_pairwise', 'example_count': 1924}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: GamerLegion, BIG
- 0-3: Lynn Vision, Liquid
- 晋级(3-1/3-2): BetBoom, B8, HEROIC, SINNERS, MIBR, M80
- 预计通过概率: 28.6%
- 期望猜中数: 3.73

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级(3-1/3-2) | 总晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| BIG | 5 | 49.2 | 21.7% | 26.5% | 23.9% | 50.5% | 72.2% | 12.4% | 10.7% | 4.7% | 3-1 |
| GamerLegion | 1 | 55.0 | 22.0% | 26.2% | 23.1% | 49.2% | 71.2% | 12.9% | 10.8% | 5.1% | 3-1 |
| BetBoom | 4 | 50.9 | 19.3% | 25.8% | 23.4% | 49.2% | 68.5% | 13.6% | 12.2% | 5.7% | 3-1 |
| B8 | 2 | 69.0 | 19.8% | 25.9% | 22.6% | 48.5% | 68.2% | 14.5% | 11.3% | 5.9% | 3-1 |
| HEROIC | 3 | 56.6 | 18.7% | 25.1% | 22.9% | 48.0% | 66.7% | 14.6% | 12.5% | 6.2% | 3-1 |
| SINNERS | 8 | 30.3 | 16.7% | 24.0% | 22.8% | 46.8% | 63.5% | 16.0% | 13.8% | 6.8% | 3-1 |
| M80 | 6 | 20.3 | 16.0% | 23.2% | 20.6% | 43.9% | 59.9% | 17.2% | 15.5% | 7.4% | 3-1 |
| MIBR | 7 | 0.9 | 14.2% | 21.8% | 22.4% | 44.1% | 58.4% | 17.5% | 16.0% | 8.2% | 3-2 |
| TYLOO | 10 | -11.5 | 9.5% | 18.1% | 19.4% | 37.5% | 46.9% | 20.5% | 19.6% | 12.9% | 2-3 |
| Sharks | 11 | -18.8 | 8.2% | 14.7% | 17.5% | 32.2% | 40.3% | 21.8% | 22.4% | 15.4% | 1-3 |
| THUNDER dOWNUNDER | 15 | -33.3 | 6.7% | 13.2% | 15.4% | 28.6% | 35.4% | 22.2% | 24.7% | 17.8% | 1-3 |
| FlyQuest | 16 | -47.6 | 6.2% | 12.5% | 15.5% | 28.0% | 34.2% | 22.2% | 24.3% | 19.2% | 1-3 |
| Gaimin Gladiators | 12 | -49.3 | 6.4% | 12.1% | 14.8% | 26.9% | 33.3% | 24.0% | 25.3% | 17.3% | 1-3 |
| NRG | 9 | -43.2 | 6.4% | 12.2% | 14.1% | 26.3% | 32.8% | 23.2% | 25.7% | 18.4% | 1-3 |
| Liquid | 13 | -62.3 | 5.1% | 10.7% | 12.6% | 23.3% | 28.3% | 23.5% | 25.7% | 22.5% | 1-3 |
| Lynn Vision | 14 | -84.4 | 3.1% | 8.0% | 9.0% | 17.0% | 20.1% | 23.9% | 29.7% | 26.3% | 1-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
- Pick'Em 计分严格按槽位判断：3-0 槽只认 3-0，晋级槽只认 3-1/3-2，0-3 槽只认 0-3。
