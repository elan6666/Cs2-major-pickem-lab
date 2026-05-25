# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: ``
- snapshot: `data/snapshots/iem_cologne_major_2026_stage1_hltv_features_2026-05-23.csv`
- model_json: `reports/stage1_model_training.json`
- model: `logistic`
- model_target: `advanced`
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
- 0-3: FlyQuest, Lynn Vision
- 晋级(3-1/3-2): BIG, BetBoom, HEROIC, SINNERS, MIBR, M80
- 预计通过概率: 37.6%
- 期望猜中数: 4.09

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级(3-1/3-2) | 总晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| GamerLegion | 1 | 135.1 | 31.6% | 30.9% | 22.6% | 53.5% | 85.1% | 7.2% | 5.5% | 2.2% | 3-0 |
| B8 | 2 | 124.1 | 26.2% | 29.9% | 24.1% | 54.0% | 80.2% | 10.0% | 7.1% | 2.7% | 3-1 |
| BIG | 5 | 81.6 | 23.6% | 30.1% | 25.2% | 55.3% | 78.9% | 10.5% | 7.6% | 3.0% | 3-1 |
| HEROIC | 3 | 103.4 | 23.9% | 29.0% | 25.1% | 54.1% | 78.0% | 10.1% | 8.6% | 3.3% | 3-1 |
| BetBoom | 4 | 94.1 | 22.7% | 29.4% | 25.3% | 54.7% | 77.4% | 10.9% | 8.6% | 3.1% | 3-1 |
| SINNERS | 8 | 46.7 | 16.6% | 26.5% | 24.5% | 51.0% | 67.6% | 15.4% | 11.9% | 5.0% | 3-1 |
| MIBR | 7 | -15.0 | 11.4% | 20.5% | 22.3% | 42.8% | 54.3% | 20.8% | 16.7% | 8.2% | 3-2 |
| M80 | 6 | -4.9 | 10.8% | 20.5% | 21.6% | 42.2% | 52.9% | 22.2% | 17.2% | 7.7% | 2-3 |
| TYLOO | 10 | -29.1 | 6.7% | 16.0% | 19.7% | 35.6% | 42.3% | 22.3% | 22.3% | 13.1% | 2-3 |
| NRG | 9 | -34.7 | 5.4% | 13.3% | 16.6% | 29.8% | 35.2% | 23.8% | 25.7% | 15.3% | 1-3 |
| Sharks | 11 | -57.3 | 4.1% | 11.2% | 14.5% | 25.7% | 29.8% | 24.9% | 26.0% | 19.3% | 1-3 |
| Gaimin Gladiators | 12 | -67.4 | 4.4% | 10.6% | 14.7% | 25.3% | 29.8% | 24.1% | 27.5% | 18.6% | 1-3 |
| Liquid | 13 | -85.5 | 3.2% | 8.9% | 12.0% | 20.9% | 24.1% | 23.9% | 27.6% | 24.5% | 1-3 |
| THUNDER dOWNUNDER | 15 | -90.3 | 3.6% | 8.0% | 10.8% | 18.8% | 22.4% | 24.6% | 29.5% | 23.5% | 1-3 |
| Lynn Vision | 14 | -78.0 | 3.0% | 8.3% | 11.0% | 19.3% | 22.4% | 25.4% | 29.1% | 23.2% | 1-3 |
| FlyQuest | 16 | -110.0 | 2.7% | 6.9% | 10.0% | 16.9% | 19.6% | 23.9% | 29.0% | 27.5% | 1-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 本次运行没有使用 HLTV 特征输入。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
- Pick'Em 计分严格按槽位判断：3-0 槽只认 3-0，晋级槽只认 3-1/3-2，0-3 槽只认 0-3。
