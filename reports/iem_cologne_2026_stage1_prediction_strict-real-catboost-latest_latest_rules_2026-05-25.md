# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/strict_real_stage1_catboost_pairwise.json`
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
- catboost_metadata: `{'model_path': 'reports/models/strict_real_stage1_catboost_pairwise.cbm', 'stage1_training_mode': 'last_4_month_hltv_pretrain', 'stage2_training_mode': 'austin_budapest_major_calibration_weighted_pairwise', 'example_count': 458}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: M80, FlyQuest
- 0-3: Lynn Vision, Sharks
- 晋级: HEROIC, BetBoom, B8, TYLOO, GamerLegion, MIBR
- 预计通过概率: 75.8%
- 期望猜中数: 5.32

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| HEROIC | 3 | 209.1 | 36.5% | 32.6% | 21.5% | 90.6% | 4.4% | 3.9% | 1.0% | 3-0 |
| BetBoom | 4 | 163.9 | 29.6% | 32.5% | 24.6% | 86.7% | 6.5% | 5.2% | 1.6% | 3-1 |
| B8 | 2 | 172.7 | 26.1% | 32.5% | 27.3% | 85.9% | 7.1% | 5.2% | 1.8% | 3-1 |
| M80 | 6 | 101.7 | 25.0% | 30.8% | 24.4% | 80.2% | 9.6% | 7.4% | 2.8% | 3-1 |
| FlyQuest | 16 | 107.2 | 18.9% | 27.7% | 28.7% | 75.3% | 12.0% | 9.3% | 3.4% | 3-2 |
| TYLOO | 10 | 62.1 | 12.1% | 26.6% | 28.9% | 67.5% | 14.2% | 12.2% | 6.1% | 3-2 |
| GamerLegion | 1 | -35.0 | 10.2% | 17.7% | 19.5% | 47.4% | 24.1% | 20.2% | 8.5% | 2-3 |
| MIBR | 7 | -50.9 | 8.1% | 17.5% | 19.8% | 45.4% | 24.1% | 20.7% | 9.8% | 2-3 |
| Liquid | 13 | -13.2 | 8.1% | 16.9% | 19.7% | 44.7% | 23.9% | 20.2% | 11.2% | 2-3 |
| Gaimin Gladiators | 12 | -24.2 | 5.7% | 14.9% | 20.1% | 40.7% | 23.0% | 22.7% | 13.6% | 2-3 |
| BIG | 5 | -97.0 | 5.0% | 11.9% | 15.0% | 32.0% | 27.7% | 26.0% | 14.3% | 2-3 |
| THUNDER dOWNUNDER | 15 | -82.6 | 4.1% | 9.8% | 13.0% | 26.9% | 25.6% | 28.7% | 18.9% | 1-3 |
| SINNERS | 8 | -116.8 | 3.4% | 10.0% | 12.3% | 25.8% | 25.1% | 28.2% | 21.0% | 1-3 |
| Sharks | 11 | -103.0 | 3.0% | 7.6% | 11.4% | 22.0% | 23.5% | 29.2% | 25.3% | 1-3 |
| NRG | 9 | -116.5 | 3.1% | 7.9% | 10.0% | 21.0% | 28.0% | 29.6% | 21.4% | 1-3 |
| Lynn Vision | 14 | -196.8 | 1.1% | 3.0% | 3.9% | 8.0% | 21.2% | 31.5% | 39.3% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
