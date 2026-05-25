# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: ``
- snapshot: ``
- model_json: ``
- model: `factor-score`
- model_target: ``
- feature_snapshot: `data/snapshots/iem_cologne_major_2026_stage1_factor_scores_2026-05-23.csv`
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
- 晋级: GamerLegion, B8, BIG, HEROIC, MIBR, SINNERS
- 预计通过概率: 61.1%
- 期望猜中数: 4.83

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| GamerLegion | 1 | 1548.3 | 21.1% | 26.7% | 23.7% | 71.4% | 12.5% | 10.9% | 5.2% | 3-1 |
| B8 | 2 | 1569.6 | 20.8% | 27.2% | 23.3% | 71.3% | 13.1% | 10.8% | 4.8% | 3-1 |
| BIG | 5 | 1533.4 | 21.1% | 26.1% | 23.2% | 70.5% | 13.4% | 11.3% | 4.9% | 3-1 |
| M80 | 6 | 1542.4 | 19.5% | 26.2% | 22.8% | 68.5% | 14.4% | 11.7% | 5.3% | 3-1 |
| BetBoom | 4 | 1537.7 | 19.2% | 25.3% | 22.7% | 67.2% | 14.4% | 12.7% | 5.7% | 3-1 |
| HEROIC | 3 | 1543.9 | 18.3% | 24.7% | 23.2% | 66.2% | 15.1% | 12.6% | 6.1% | 3-1 |
| MIBR | 7 | 1494.8 | 14.6% | 21.5% | 22.5% | 58.6% | 17.8% | 15.9% | 7.7% | 3-2 |
| SINNERS | 8 | 1492.0 | 14.3% | 21.2% | 20.6% | 56.1% | 18.8% | 16.9% | 8.1% | 3-1 |
| NRG | 9 | 1519.8 | 11.3% | 20.2% | 21.1% | 52.6% | 18.6% | 18.9% | 9.8% | 3-2 |
| TYLOO | 10 | 1478.6 | 9.2% | 17.3% | 19.6% | 46.1% | 20.9% | 20.4% | 12.6% | 2-3 |
| Sharks | 11 | 1468.0 | 7.7% | 14.0% | 17.3% | 39.0% | 22.7% | 22.5% | 15.8% | 2-3 |
| THUNDER dOWNUNDER | 15 | 1439.6 | 5.5% | 12.0% | 14.1% | 31.6% | 22.7% | 25.4% | 20.3% | 1-3 |
| Gaimin Gladiators | 12 | 1419.1 | 5.3% | 10.2% | 12.7% | 28.2% | 24.3% | 27.3% | 20.1% | 1-3 |
| Liquid | 13 | 1425.3 | 4.8% | 10.7% | 12.2% | 27.8% | 23.7% | 26.0% | 22.5% | 1-3 |
| Lynn Vision | 14 | 1428.7 | 4.0% | 9.3% | 11.7% | 25.0% | 23.4% | 27.7% | 23.8% | 1-3 |
| FlyQuest | 16 | 1376.8 | 3.2% | 7.4% | 9.1% | 19.7% | 24.0% | 28.9% | 27.3% | 1-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
