# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/snapshots/blast_austin_major_2025_stage1_2025-06-02.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_vrs_interaction_scoreline_weighted_finetune_2026-05-25.json`
- model: `catboost`
- model_target: `advanced`
- feature_snapshot: `data/snapshots/blast_austin_major_2025_stage1_2025-06-02.csv`
- score_column: `feature_score`
- stage_name: `Stage 1`
- advance_label: `晋级`
- simulations: `10000`
- seed: `42`
- scale: `120.0`
- effective_scale: `120.0`
- bo1_shrink: `0.7`
- effective_bo1_shrink: `0.7`
- bo3_shrink: `1.0`
- effective_bo3_shrink: `1.0`
- veto_weight: `1.0`
- calibration_json: ``
- all_bo3: `False`
- map_stats: ``
- map_pool: ``
- veto_policy: ``
- bandit_policy_json: ``
- catboost_metadata: `{'model_path': 'reports/models/bo3_stage1_catboost_vrs_interaction_scoreline_weighted_finetune_2026-05-25.cbm', 'stage1_training_mode': 'last_4_month_bo3_pretrain', 'stage2_training_mode': 'austin_budapest_major_calibration_weighted_pairwise_with_vrs_interaction_scoreline_features', 'example_count': 1924}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: HEROIC, TYLOO
- 0-3: Fluxo, Metizport
- 晋级: B8, BetBoom, OG, Nemiga, Legacy, Lynn Vision
- 预计通过概率: 96.0%
- 期望猜中数: 6.43

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| HEROIC | 1 | 380.1 | 46.0% | 35.1% | 16.0% | 97.1% | 1.6% | 1.0% | 0.3% | 3-0 |
| B8 | 4 | 347.9 | 42.2% | 36.4% | 17.7% | 96.4% | 2.1% | 1.2% | 0.3% | 3-0 |
| BetBoom | 8 | 269.4 | 32.5% | 38.9% | 22.0% | 93.3% | 4.1% | 2.1% | 0.5% | 3-1 |
| OG | 9 | 225.8 | 13.2% | 36.5% | 36.6% | 86.3% | 7.5% | 5.0% | 1.2% | 3-2 |
| Nemiga | 12 | 219.6 | 14.2% | 37.0% | 34.2% | 85.5% | 8.4% | 4.6% | 1.6% | 3-1 |
| TYLOO | 3 | 133.3 | 21.3% | 31.5% | 28.1% | 80.9% | 13.0% | 5.3% | 0.7% | 3-1 |
| Legacy | 14 | 97.6 | 10.2% | 23.8% | 35.4% | 69.4% | 19.6% | 8.7% | 2.4% | 3-2 |
| Lynn Vision | 6 | 11.1 | 5.1% | 17.1% | 31.8% | 54.0% | 27.3% | 14.5% | 4.2% | 3-2 |
| FlyQuest | 5 | -1.0 | 6.6% | 17.4% | 27.0% | 51.1% | 31.4% | 15.0% | 2.6% | 2-3 |
| NRG | 7 | -86.1 | 4.6% | 11.0% | 20.6% | 36.2% | 36.1% | 23.5% | 4.1% | 2-3 |
| Wildcard | 13 | -137.9 | 1.2% | 5.6% | 14.7% | 21.6% | 33.7% | 30.2% | 14.6% | 2-3 |
| Complexity | 2 | -267.2 | 1.3% | 3.5% | 5.5% | 10.4% | 37.2% | 40.4% | 12.0% | 1-3 |
| Chinggis Warriors | 10 | -321.3 | 0.6% | 1.9% | 2.9% | 5.5% | 24.7% | 44.1% | 25.7% | 1-3 |
| Imperial | 11 | -306.5 | 0.4% | 1.7% | 3.2% | 5.3% | 19.8% | 36.4% | 38.4% | 0-3 |
| Metizport | 16 | -336.5 | 0.3% | 1.5% | 2.2% | 4.0% | 17.1% | 34.7% | 44.2% | 0-3 |
| Fluxo | 15 | -369.0 | 0.3% | 1.0% | 1.8% | 3.2% | 16.5% | 33.3% | 47.1% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行没有启用地图 veto 模拟。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
