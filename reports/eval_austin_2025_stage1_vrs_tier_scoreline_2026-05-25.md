# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/snapshots/blast_austin_major_2025_stage1_2025-06-02.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_vrs_tier_scoreline_weighted_finetune_2026-05-25.json`
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
- catboost_metadata: `{'model_path': 'reports/models/bo3_stage1_catboost_vrs_tier_scoreline_weighted_finetune_2026-05-25.cbm', 'stage1_training_mode': 'last_4_month_bo3_pretrain', 'stage2_training_mode': 'austin_budapest_major_calibration_weighted_pairwise_with_vrs_tier_scoreline_features', 'example_count': 1924}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: HEROIC, TYLOO
- 0-3: Fluxo, Metizport
- 晋级: B8, BetBoom, OG, Nemiga, Legacy, FlyQuest
- 预计通过概率: 96.5%
- 期望猜中数: 6.46

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| HEROIC | 1 | 385.5 | 43.9% | 36.8% | 16.4% | 97.0% | 1.6% | 1.1% | 0.3% | 3-0 |
| B8 | 4 | 341.5 | 37.6% | 37.9% | 20.2% | 95.7% | 2.4% | 1.6% | 0.4% | 3-1 |
| BetBoom | 8 | 298.4 | 35.3% | 37.4% | 21.1% | 93.8% | 3.8% | 2.0% | 0.4% | 3-1 |
| OG | 9 | 249.0 | 14.4% | 36.9% | 35.8% | 87.1% | 7.2% | 4.5% | 1.2% | 3-1 |
| Nemiga | 12 | 245.7 | 16.2% | 38.0% | 32.8% | 86.9% | 7.4% | 4.3% | 1.4% | 3-1 |
| TYLOO | 3 | 145.0 | 21.2% | 31.5% | 28.0% | 80.7% | 13.5% | 5.0% | 0.7% | 3-1 |
| Legacy | 14 | 104.6 | 10.2% | 22.8% | 35.6% | 68.6% | 20.4% | 8.7% | 2.2% | 3-2 |
| FlyQuest | 5 | 34.2 | 8.5% | 18.8% | 28.6% | 55.8% | 29.8% | 12.5% | 1.9% | 2-3 |
| Lynn Vision | 6 | 13.3 | 4.6% | 16.0% | 31.5% | 52.1% | 28.5% | 15.3% | 4.1% | 3-2 |
| NRG | 7 | -87.3 | 4.4% | 10.4% | 20.4% | 35.2% | 37.6% | 23.4% | 3.8% | 2-3 |
| Wildcard | 13 | -138.1 | 1.2% | 5.1% | 14.8% | 21.1% | 34.1% | 30.6% | 14.2% | 2-3 |
| Complexity | 2 | -287.9 | 1.1% | 3.0% | 4.8% | 8.8% | 36.0% | 42.2% | 12.9% | 1-3 |
| Chinggis Warriors | 10 | -322.2 | 0.6% | 2.0% | 3.0% | 5.5% | 26.1% | 45.3% | 23.0% | 1-3 |
| Imperial | 11 | -329.6 | 0.4% | 1.5% | 3.0% | 4.9% | 18.9% | 36.1% | 40.1% | 0-3 |
| Metizport | 16 | -351.6 | 0.2% | 1.3% | 2.3% | 3.9% | 17.0% | 35.4% | 43.8% | 0-3 |
| Fluxo | 15 | -396.8 | 0.3% | 0.9% | 1.6% | 2.7% | 15.7% | 32.1% | 49.5% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行没有启用地图 veto 模拟。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
