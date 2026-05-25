# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_pairwise_weighted_finetune_2026-05-25.json`
- model: `catboost`
- model_target: `advanced`
- feature_snapshot: `data/snapshots/iem_cologne_major_2026_stage1_factor_weights_trained_2026-05-25.csv`
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
- catboost_metadata: `{'model_path': 'reports/models/bo3_stage1_catboost_pairwise_weighted_finetune_2026-05-25.cbm', 'stage1_training_mode': 'last_4_month_bo3_pretrain', 'stage2_training_mode': 'combined_weighted_bo3_pretrain_major_finetune', 'example_count': 1924}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: BetBoom, SINNERS
- 0-3: Lynn Vision, Liquid
- 晋级: GamerLegion, BIG, HEROIC, B8, MIBR, M80
- 预计通过概率: 62.6%
- 期望猜中数: 4.88

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| GamerLegion | 1 | 82.6 | 25.0% | 28.0% | 23.1% | 76.1% | 11.0% | 9.2% | 3.7% | 3-1 |
| BIG | 5 | 52.1 | 21.4% | 27.0% | 23.4% | 71.7% | 13.0% | 10.7% | 4.6% | 3-1 |
| BetBoom | 4 | 62.9 | 20.2% | 26.2% | 24.1% | 70.6% | 12.8% | 11.4% | 5.2% | 3-1 |
| HEROIC | 3 | 68.5 | 19.6% | 25.2% | 23.9% | 68.7% | 13.8% | 12.1% | 5.5% | 3-1 |
| SINNERS | 8 | 40.2 | 16.9% | 24.6% | 23.1% | 64.5% | 15.9% | 13.3% | 6.3% | 3-1 |
| B8 | 2 | 57.1 | 16.7% | 25.2% | 22.6% | 64.4% | 16.6% | 12.5% | 6.5% | 3-1 |
| MIBR | 7 | 19.3 | 16.3% | 23.4% | 23.1% | 62.8% | 16.3% | 14.1% | 6.8% | 3-1 |
| M80 | 6 | 6.6 | 13.9% | 21.5% | 20.5% | 55.8% | 18.9% | 16.9% | 8.3% | 3-1 |
| TYLOO | 10 | 9.2 | 11.1% | 19.6% | 21.6% | 52.3% | 19.7% | 17.6% | 10.4% | 3-2 |
| Sharks | 11 | -2.9 | 8.7% | 16.0% | 18.8% | 43.5% | 21.0% | 21.7% | 13.9% | 1-3 |
| FlyQuest | 16 | -38.7 | 6.3% | 12.7% | 16.4% | 35.4% | 22.2% | 23.9% | 18.4% | 1-3 |
| NRG | 9 | -35.0 | 6.3% | 12.4% | 14.6% | 33.3% | 23.2% | 25.6% | 17.8% | 1-3 |
| Gaimin Gladiators | 12 | -53.4 | 5.8% | 11.2% | 14.1% | 31.1% | 24.1% | 26.5% | 18.4% | 1-3 |
| THUNDER dOWNUNDER | 15 | -66.7 | 4.8% | 10.0% | 11.6% | 26.4% | 23.4% | 27.0% | 23.2% | 1-3 |
| Liquid | 13 | -72.8 | 4.3% | 9.9% | 10.8% | 24.9% | 24.0% | 27.2% | 23.9% | 1-3 |
| Lynn Vision | 14 | -91.2 | 2.8% | 7.1% | 8.6% | 18.5% | 24.1% | 30.2% | 27.1% | 1-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
