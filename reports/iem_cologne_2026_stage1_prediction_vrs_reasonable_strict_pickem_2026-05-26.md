# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_vrs_reasonable_scoreline_weighted_finetune_2026-05-26.json`
- model: `catboost`
- model_target: `advanced`
- feature_snapshot: `data/snapshots/iem_cologne_major_2026_stage1_vrs_reasonable_scoreline_features_2026-05-26.csv`
- score_column: `feature_score`
- stage_name: `Stage 1`
- advance_label: `晋级(3-1/3-2)`
- simulations: `10000`
- seed: `42`
- scale: `120.0`
- effective_scale: `105.0`
- bo1_shrink: `0.7`
- effective_bo1_shrink: `0.7`
- bo3_shrink: `1.0`
- effective_bo3_shrink: `1.0`
- veto_weight: `1.0`
- calibration_json: `reports/vrs_reasonable_scoreline_bo1_bo3_calibration_2026-05-26.json`
- all_bo3: `False`
- map_stats: `data/bo3/bo3_stage1_last4months_vrs_reasonable_scoreline_map_stats_2026-05-26.csv`
- map_pool: `Ancient, Anubis, Dust2, Inferno, Mirage, Nuke, Overpass`
- veto_policy: `contextual-bandit`
- bandit_policy_json: `reports/models/bo3_two_layer_veto_bandit_policy_2026-05-25.json`
- catboost_metadata: `{'model_path': 'reports/models/bo3_stage1_catboost_vrs_reasonable_scoreline_weighted_finetune_2026-05-26.cbm', 'stage1_training_mode': 'last_4_month_bo3_pretrain', 'stage2_training_mode': 'austin_budapest_major_calibration_weighted_pairwise_with_vrs_reasonable_scoreline_features', 'example_count': 1924}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: BIG, BetBoom
- 0-3: Lynn Vision, NRG
- 晋级(3-1/3-2): MIBR, THUNDER dOWNUNDER, SINNERS, HEROIC, GamerLegion, Sharks
- 预计通过概率: 61.6%
- 期望猜中数: 4.89

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级(3-1/3-2) | 总晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| BIG | 5 | 155.7 | 46.8% | 31.8% | 16.8% | 48.5% | 95.3% | 2.7% | 1.7% | 0.4% | 3-0 |
| MIBR | 7 | 90.8 | 23.1% | 35.9% | 26.9% | 62.9% | 85.9% | 7.7% | 5.1% | 1.3% | 3-1 |
| BetBoom | 4 | 90.0 | 29.2% | 32.4% | 23.4% | 55.9% | 85.1% | 8.4% | 5.4% | 1.1% | 3-1 |
| SINNERS | 8 | 57.4 | 16.7% | 29.4% | 28.2% | 57.6% | 74.3% | 14.1% | 9.2% | 2.4% | 3-1 |
| GamerLegion | 1 | 44.3 | 21.4% | 28.6% | 24.2% | 52.8% | 74.2% | 16.3% | 7.6% | 1.8% | 3-1 |
| HEROIC | 3 | 56.3 | 16.6% | 28.5% | 27.8% | 56.4% | 73.0% | 15.3% | 8.7% | 2.9% | 3-1 |
| THUNDER dOWNUNDER | 15 | 54.6 | 10.9% | 25.5% | 33.1% | 58.6% | 69.5% | 15.7% | 11.0% | 3.7% | 3-2 |
| M80 | 6 | -3.8 | 10.2% | 20.2% | 21.8% | 42.0% | 52.2% | 27.2% | 17.0% | 3.5% | 2-3 |
| TYLOO | 10 | -2.9 | 8.3% | 20.0% | 23.5% | 43.5% | 51.7% | 26.9% | 16.8% | 4.6% | 2-3 |
| Sharks | 11 | 10.1 | 6.9% | 18.6% | 25.4% | 43.9% | 50.9% | 24.0% | 18.6% | 6.6% | 3-2 |
| FlyQuest | 16 | -10.7 | 4.9% | 13.0% | 23.5% | 36.4% | 41.3% | 27.3% | 22.8% | 8.6% | 2-3 |
| B8 | 2 | -57.2 | 3.1% | 8.8% | 14.2% | 23.0% | 26.1% | 32.3% | 28.5% | 13.2% | 2-3 |
| Liquid | 13 | -124.9 | 0.7% | 2.4% | 4.0% | 6.5% | 7.2% | 23.7% | 36.5% | 32.6% | 1-3 |
| Gaimin Gladiators | 12 | -149.0 | 0.5% | 2.2% | 3.0% | 5.2% | 5.7% | 20.6% | 37.7% | 35.9% | 1-3 |
| NRG | 9 | -167.6 | 0.5% | 1.5% | 2.7% | 4.2% | 4.6% | 20.8% | 38.1% | 36.5% | 1-3 |
| Lynn Vision | 14 | -192.3 | 0.3% | 1.2% | 1.5% | 2.7% | 3.0% | 17.1% | 35.2% | 44.7% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行启用了地图 veto 模拟：BO1/BO3 会按地图池、地图胜率、pick/ban 倾向调整单场胜率。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
- Pick'Em 计分严格按槽位判断：3-0 槽只认 3-0，晋级槽只认 3-1/3-2，0-3 槽只认 0-3。
