# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: ``
- snapshot: ``
- model_json: ``
- model: `factor-score`
- model_target: ``
- feature_snapshot: `data/snapshots/iem_cologne_major_2026_stage1_factor_weights_trained_2026-05-23.csv`
- score_column: `factor_score`
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
- catboost_metadata: ``
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: M80, BetBoom
- 0-3: FlyQuest, Liquid
- 晋级: B8, BIG, GamerLegion, HEROIC, MIBR, SINNERS
- 预计通过概率: 60.5%
- 期望猜中数: 4.81

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| B8 | 2 | 1570.0 | 20.6% | 27.1% | 23.1% | 70.9% | 13.4% | 10.8% | 4.9% | 3-1 |
| BIG | 5 | 1535.9 | 21.1% | 26.2% | 23.3% | 70.7% | 13.2% | 11.2% | 4.9% | 3-1 |
| GamerLegion | 1 | 1548.3 | 20.8% | 26.4% | 23.3% | 70.5% | 12.9% | 11.2% | 5.4% | 3-1 |
| M80 | 6 | 1543.4 | 19.4% | 26.0% | 22.9% | 68.4% | 14.4% | 11.8% | 5.5% | 3-1 |
| BetBoom | 4 | 1539.7 | 19.2% | 25.0% | 23.0% | 67.2% | 14.3% | 12.7% | 5.8% | 3-1 |
| HEROIC | 3 | 1545.7 | 18.2% | 24.6% | 23.2% | 65.9% | 15.3% | 12.7% | 6.1% | 3-1 |
| MIBR | 7 | 1496.1 | 14.4% | 21.5% | 22.5% | 58.5% | 17.7% | 16.0% | 7.7% | 3-2 |
| SINNERS | 8 | 1495.8 | 14.5% | 21.3% | 20.7% | 56.5% | 18.6% | 16.8% | 8.1% | 3-1 |
| NRG | 9 | 1521.7 | 11.4% | 20.2% | 20.9% | 52.6% | 18.6% | 18.9% | 9.9% | 3-2 |
| TYLOO | 10 | 1480.2 | 9.2% | 17.2% | 19.2% | 45.7% | 21.0% | 20.6% | 12.8% | 2-3 |
| Sharks | 11 | 1470.7 | 7.8% | 14.1% | 17.1% | 39.0% | 22.7% | 22.4% | 15.9% | 2-3 |
| THUNDER dOWNUNDER | 15 | 1443.8 | 5.6% | 12.2% | 14.2% | 32.0% | 22.8% | 25.2% | 20.0% | 1-3 |
| Liquid | 13 | 1429.4 | 5.0% | 10.8% | 12.6% | 28.4% | 23.4% | 25.9% | 22.3% | 1-3 |
| Gaimin Gladiators | 12 | 1422.2 | 5.3% | 10.3% | 12.8% | 28.4% | 24.1% | 27.4% | 20.1% | 1-3 |
| Lynn Vision | 14 | 1432.3 | 4.1% | 9.4% | 11.8% | 25.4% | 23.5% | 27.6% | 23.6% | 1-3 |
| FlyQuest | 16 | 1382.3 | 3.3% | 7.5% | 9.2% | 20.1% | 24.3% | 28.7% | 26.9% | 1-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
