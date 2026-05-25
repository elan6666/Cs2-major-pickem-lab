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
- catboost_metadata: ``
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: GamerLegion, B8
- 0-3: FlyQuest, THUNDER dOWNUNDER
- 晋级(3-1/3-2): BetBoom, BIG, HEROIC, MIBR, M80, SINNERS
- 预计通过概率: 49.4%
- 期望猜中数: 4.53

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级(3-1/3-2) | 总晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| GamerLegion | 1 | 1566.0 | 38.1% | 31.1% | 21.4% | 52.5% | 90.6% | 4.5% | 3.7% | 1.3% | 3-0 |
| B8 | 2 | 1547.0 | 31.9% | 31.2% | 23.4% | 54.6% | 86.5% | 7.4% | 4.4% | 1.6% | 3-0 |
| HEROIC | 3 | 1482.0 | 22.2% | 29.2% | 25.7% | 54.8% | 77.0% | 11.9% | 8.4% | 2.7% | 3-1 |
| BetBoom | 4 | 1471.0 | 20.7% | 29.7% | 26.5% | 56.2% | 76.9% | 12.2% | 8.3% | 2.6% | 3-1 |
| BIG | 5 | 1445.0 | 20.3% | 29.9% | 25.2% | 55.0% | 75.3% | 12.8% | 8.8% | 3.1% | 3-1 |
| MIBR | 7 | 1402.0 | 14.7% | 25.1% | 25.3% | 50.3% | 65.0% | 17.4% | 13.0% | 4.6% | 3-2 |
| M80 | 6 | 1417.0 | 14.4% | 25.4% | 24.6% | 50.1% | 64.5% | 18.6% | 12.3% | 4.6% | 3-1 |
| SINNERS | 8 | 1379.0 | 11.1% | 23.1% | 23.1% | 46.2% | 57.4% | 20.8% | 15.7% | 6.1% | 3-2 |
| NRG | 9 | 1375.0 | 6.1% | 16.3% | 21.2% | 37.5% | 43.6% | 22.6% | 23.5% | 10.3% | 1-3 |
| TYLOO | 10 | 1348.0 | 5.6% | 15.4% | 20.8% | 36.2% | 41.8% | 24.0% | 23.3% | 10.9% | 2-3 |
| Sharks | 11 | 1334.0 | 4.2% | 12.1% | 17.4% | 29.5% | 33.7% | 26.1% | 26.1% | 14.1% | 2-3 |
| Gaimin Gladiators | 12 | 1319.0 | 3.9% | 11.6% | 16.5% | 28.1% | 32.0% | 26.4% | 26.4% | 15.1% | 2-3 |
| Liquid | 13 | 1267.0 | 2.4% | 7.0% | 10.3% | 17.2% | 19.6% | 25.6% | 30.9% | 23.9% | 1-3 |
| Lynn Vision | 14 | 1249.0 | 1.5% | 5.5% | 7.6% | 13.1% | 14.6% | 24.2% | 32.3% | 28.9% | 1-3 |
| THUNDER dOWNUNDER | 15 | 1224.0 | 1.7% | 4.7% | 6.9% | 11.6% | 13.3% | 23.5% | 31.3% | 31.9% | 0-3 |
| FlyQuest | 16 | 1164.0 | 1.1% | 3.1% | 4.0% | 7.1% | 8.2% | 21.9% | 31.6% | 38.3% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 本次运行没有使用 HLTV 特征输入。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
- Pick'Em 计分严格按槽位判断：3-0 槽只认 3-0，晋级槽只认 3-1/3-2，0-3 槽只认 0-3。
