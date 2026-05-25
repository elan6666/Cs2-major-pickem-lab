# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/stage1_catboost_pairwise.json`
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
- bandit_policy_json: `reports/models/bo3_two_layer_veto_bandit_policy_2026-05-25.json`
- catboost_metadata: `{'model_path': 'reports/models/stage1_catboost_pairwise.cbm', 'stage1_training_mode': 'fallback_major_pairwise', 'stage2_training_mode': 'austin_budapest_major_calibration_weighted_pairwise', 'example_count': 424}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: B8, BIG
- 0-3: Lynn Vision, THUNDER dOWNUNDER
- 晋级: HEROIC, BetBoom, M80, FlyQuest, TYLOO, SINNERS
- 预计通过概率: 85.4%
- 期望猜中数: 5.67

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| HEROIC | 3 | 247.1 | 38.3% | 34.0% | 21.3% | 93.6% | 3.3% | 2.5% | 0.7% | 3-0 |
| B8 | 2 | 245.1 | 34.5% | 34.3% | 23.7% | 92.6% | 3.7% | 3.0% | 0.7% | 3-0 |
| BetBoom | 4 | 213.0 | 35.6% | 34.1% | 21.9% | 91.7% | 4.3% | 3.2% | 0.8% | 3-0 |
| M80 | 6 | 192.9 | 31.7% | 36.6% | 22.8% | 91.1% | 4.2% | 3.6% | 1.1% | 3-1 |
| FlyQuest | 16 | 49.1 | 10.9% | 24.8% | 31.9% | 67.6% | 15.9% | 11.6% | 4.9% | 3-2 |
| TYLOO | 10 | 18.2 | 7.5% | 23.2% | 31.2% | 61.8% | 16.8% | 14.4% | 7.1% | 3-2 |
| BIG | 5 | -16.9 | 11.1% | 24.1% | 25.6% | 60.8% | 20.4% | 13.9% | 4.9% | 3-2 |
| SINNERS | 8 | -40.4 | 6.8% | 19.0% | 26.9% | 52.7% | 20.8% | 17.7% | 8.9% | 3-2 |
| MIBR | 7 | -92.9 | 6.6% | 16.6% | 19.8% | 43.0% | 26.8% | 21.4% | 8.8% | 2-3 |
| NRG | 9 | -119.3 | 3.7% | 10.4% | 13.4% | 27.5% | 30.5% | 28.3% | 13.7% | 2-3 |
| Sharks | 11 | -118.8 | 2.4% | 9.3% | 13.2% | 25.0% | 23.9% | 28.8% | 22.4% | 1-3 |
| Gaimin Gladiators | 12 | -140.8 | 1.9% | 8.2% | 11.8% | 21.8% | 24.7% | 30.7% | 22.8% | 1-3 |
| Liquid | 13 | -144.5 | 2.5% | 7.7% | 11.4% | 21.6% | 25.8% | 29.6% | 23.0% | 1-3 |
| GamerLegion | 1 | -179.9 | 3.3% | 7.7% | 10.3% | 21.3% | 31.6% | 29.3% | 17.8% | 2-3 |
| THUNDER dOWNUNDER | 15 | -156.7 | 2.5% | 7.1% | 10.7% | 20.3% | 26.9% | 30.3% | 22.4% | 1-3 |
| Lynn Vision | 14 | -239.1 | 0.8% | 3.0% | 4.0% | 7.8% | 20.6% | 31.5% | 40.1% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
