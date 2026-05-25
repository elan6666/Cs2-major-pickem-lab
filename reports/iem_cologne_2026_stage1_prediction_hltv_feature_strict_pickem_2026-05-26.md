# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: ``
- snapshot: ``
- model_json: ``
- model: `feature-score`
- model_target: ``
- feature_snapshot: `data/snapshots/iem_cologne_major_2026_stage1_hltv_features_2026-05-23.csv`
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
- catboost_metadata: ``
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: GamerLegion, B8
- 0-3: FlyQuest, THUNDER dOWNUNDER
- 晋级(3-1/3-2): BetBoom, BIG, HEROIC, M80, MIBR, SINNERS
- 预计通过概率: 47.1%
- 期望猜中数: 4.44

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级(3-1/3-2) | 总晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| GamerLegion | 1 | 1595.0 | 35.3% | 31.3% | 22.3% | 53.6% | 88.9% | 5.3% | 4.2% | 1.6% | 3-0 |
| B8 | 2 | 1589.5 | 31.3% | 31.3% | 23.3% | 54.7% | 86.0% | 7.5% | 4.9% | 1.7% | 3-1 |
| HEROIC | 3 | 1526.0 | 22.0% | 28.9% | 25.6% | 54.5% | 76.6% | 12.0% | 8.5% | 2.9% | 3-1 |
| BetBoom | 4 | 1513.5 | 21.1% | 29.1% | 25.7% | 54.9% | 75.9% | 12.5% | 8.7% | 2.8% | 3-1 |
| BIG | 5 | 1492.0 | 20.6% | 29.5% | 25.2% | 54.7% | 75.3% | 12.8% | 8.8% | 3.0% | 3-1 |
| M80 | 6 | 1482.0 | 16.8% | 26.6% | 25.3% | 52.0% | 68.7% | 16.4% | 10.9% | 3.9% | 3-1 |
| MIBR | 7 | 1447.5 | 14.5% | 24.5% | 25.3% | 49.8% | 64.3% | 17.6% | 13.3% | 4.8% | 3-2 |
| SINNERS | 8 | 1417.0 | 10.5% | 21.8% | 22.0% | 43.8% | 54.3% | 22.6% | 16.6% | 6.4% | 2-3 |
| NRG | 9 | 1440.0 | 7.2% | 18.3% | 22.8% | 41.1% | 48.3% | 21.7% | 21.0% | 9.0% | 3-2 |
| TYLOO | 10 | 1402.5 | 6.1% | 15.6% | 21.5% | 37.1% | 43.3% | 23.5% | 22.9% | 10.3% | 2-3 |
| Sharks | 11 | 1379.5 | 4.2% | 12.1% | 17.0% | 29.1% | 33.3% | 26.0% | 26.2% | 14.6% | 1-3 |
| Gaimin Gladiators | 12 | 1348.0 | 3.3% | 10.3% | 14.4% | 24.6% | 27.9% | 26.4% | 28.3% | 17.3% | 1-3 |
| Liquid | 13 | 1309.5 | 2.4% | 6.6% | 9.9% | 16.4% | 18.8% | 25.3% | 31.3% | 24.6% | 1-3 |
| THUNDER dOWNUNDER | 15 | 1289.0 | 2.0% | 5.5% | 8.1% | 13.7% | 15.7% | 24.1% | 30.8% | 29.5% | 1-3 |
| Lynn Vision | 14 | 1300.5 | 1.6% | 5.5% | 7.7% | 13.2% | 14.8% | 24.4% | 31.6% | 29.2% | 1-3 |
| FlyQuest | 16 | 1211.0 | 1.1% | 2.9% | 4.0% | 6.9% | 8.0% | 21.8% | 31.9% | 38.3% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
- Pick'Em 计分严格按槽位判断：3-0 槽只认 3-0，晋级槽只认 3-1/3-2，0-3 槽只认 0-3。
