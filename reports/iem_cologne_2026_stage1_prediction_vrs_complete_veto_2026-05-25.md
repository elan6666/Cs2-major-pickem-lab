# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: ``
- snapshot: ``
- model_json: ``
- model: `vrs`
- model_target: ``
- feature_snapshot: ``
- score_column: ``
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
- catboost_metadata: ``
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: B8, HEROIC
- 0-3: FlyQuest, THUNDER dOWNUNDER
- 晋级: BIG, GamerLegion, BetBoom, SINNERS, M80, TYLOO
- 预计通过概率: 73.8%
- 期望猜中数: 5.25

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| BIG | 5 | 1526.0 | 26.1% | 30.7% | 24.6% | 81.4% | 9.2% | 6.7% | 2.7% | 3-1 |
| GamerLegion | 1 | 1529.0 | 27.1% | 29.3% | 23.8% | 80.2% | 9.8% | 7.3% | 2.7% | 3-1 |
| BetBoom | 4 | 1525.0 | 24.2% | 29.2% | 24.4% | 77.8% | 10.6% | 8.4% | 3.2% | 3-1 |
| B8 | 2 | 1518.0 | 20.6% | 28.3% | 24.9% | 73.7% | 12.8% | 9.5% | 4.0% | 3-1 |
| HEROIC | 3 | 1502.0 | 19.7% | 27.2% | 24.5% | 71.4% | 13.5% | 11.0% | 4.1% | 3-1 |
| SINNERS | 8 | 1480.0 | 18.7% | 26.4% | 23.9% | 69.1% | 14.8% | 11.5% | 4.6% | 3-1 |
| M80 | 6 | 1456.0 | 15.3% | 23.6% | 23.1% | 62.1% | 17.7% | 14.2% | 6.0% | 3-1 |
| TYLOO | 10 | 1441.0 | 10.1% | 19.5% | 23.9% | 53.5% | 19.9% | 17.7% | 9.0% | 3-2 |
| MIBR | 7 | 1369.0 | 8.7% | 15.2% | 17.5% | 41.4% | 25.3% | 22.0% | 11.4% | 2-3 |
| Sharks | 11 | 1408.0 | 6.3% | 14.8% | 18.6% | 39.7% | 23.2% | 23.2% | 14.0% | 1-3 |
| NRG | 9 | 1412.0 | 6.6% | 15.2% | 17.8% | 39.5% | 23.3% | 23.9% | 13.3% | 1-3 |
| Gaimin Gladiators | 12 | 1376.0 | 5.3% | 12.1% | 15.6% | 33.0% | 24.2% | 26.3% | 16.5% | 1-3 |
| Liquid | 13 | 1361.0 | 4.1% | 10.0% | 12.9% | 27.0% | 23.8% | 27.2% | 22.0% | 1-3 |
| Lynn Vision | 14 | 1334.0 | 2.6% | 6.8% | 9.5% | 19.0% | 24.9% | 29.9% | 26.2% | 1-3 |
| THUNDER dOWNUNDER | 15 | 1301.0 | 2.4% | 6.2% | 8.2% | 16.8% | 24.6% | 30.7% | 27.8% | 1-3 |
| FlyQuest | 16 | 1282.0 | 2.1% | 5.5% | 6.9% | 14.4% | 22.6% | 30.6% | 32.4% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 本次运行没有使用 HLTV 特征输入。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
