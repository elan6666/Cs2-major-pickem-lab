# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/snapshots/starladder_budapest_major_2025_stage1_2025-10-06.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_vrs_tier_scoreline_weighted_finetune_2026-05-25.json`
- model: `catboost`
- model_target: `advanced`
- feature_snapshot: `data/snapshots/starladder_budapest_major_2025_stage1_2025-10-06.csv`
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

- 3-0: Ninjas in Pyjamas, FaZe
- 0-3: Rare Atom, The Huns
- 晋级: B8, fnatic, M80, FlyQuest, PARIVISION, Legacy
- 预计通过概率: 97.5%
- 期望猜中数: 6.58

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| B8 | 4 | 293.6 | 38.9% | 35.4% | 19.6% | 93.8% | 4.2% | 1.8% | 0.2% | 3-0 |
| Ninjas in Pyjamas | 3 | 276.6 | 34.6% | 36.1% | 21.9% | 92.6% | 4.9% | 2.1% | 0.4% | 3-1 |
| fnatic | 6 | 269.0 | 33.9% | 36.6% | 22.0% | 92.5% | 5.0% | 2.1% | 0.4% | 3-1 |
| M80 | 10 | 267.1 | 29.3% | 36.4% | 25.7% | 91.5% | 6.0% | 2.2% | 0.3% | 3-1 |
| FlyQuest | 13 | 226.4 | 15.1% | 36.0% | 35.3% | 86.4% | 8.9% | 3.8% | 0.9% | 3-1 |
| FaZe | 1 | 194.9 | 25.1% | 32.7% | 27.6% | 85.3% | 10.6% | 3.4% | 0.7% | 3-1 |
| PARIVISION | 5 | 181.7 | 11.0% | 33.3% | 36.7% | 81.0% | 12.8% | 5.2% | 1.0% | 3-2 |
| Legacy | 8 | 29.0 | 6.3% | 19.9% | 29.5% | 55.8% | 31.8% | 10.9% | 1.5% | 2-3 |
| Imperial | 9 | 6.3 | 2.2% | 13.6% | 29.8% | 45.6% | 32.3% | 17.9% | 4.2% | 2-3 |
| NRG | 11 | -90.9 | 0.7% | 5.8% | 18.6% | 25.0% | 35.9% | 29.3% | 9.7% | 2-3 |
| GamerLegion | 2 | -138.4 | 1.1% | 6.1% | 13.9% | 21.1% | 40.5% | 29.9% | 8.5% | 2-3 |
| Fluxo | 14 | -150.1 | 0.4% | 3.3% | 11.2% | 14.9% | 31.2% | 35.7% | 18.1% | 1-3 |
| RED Canids | 15 | -332.4 | 0.6% | 1.5% | 2.7% | 4.7% | 23.3% | 41.9% | 30.0% | 1-3 |
| Lynn Vision | 7 | -338.2 | 0.5% | 1.6% | 2.6% | 4.7% | 24.7% | 44.1% | 26.5% | 1-3 |
| The Huns | 12 | -350.0 | 0.2% | 1.0% | 1.9% | 3.0% | 16.0% | 38.4% | 42.6% | 0-3 |
| Rare Atom | 16 | -423.1 | 0.2% | 0.6% | 1.3% | 2.0% | 11.8% | 31.2% | 55.0% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行没有启用地图 veto 模拟。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
