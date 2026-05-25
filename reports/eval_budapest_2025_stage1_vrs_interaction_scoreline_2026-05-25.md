# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/snapshots/starladder_budapest_major_2025_stage1_2025-10-06.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_vrs_interaction_scoreline_weighted_finetune_2026-05-25.json`
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
- catboost_metadata: `{'model_path': 'reports/models/bo3_stage1_catboost_vrs_interaction_scoreline_weighted_finetune_2026-05-25.cbm', 'stage1_training_mode': 'last_4_month_bo3_pretrain', 'stage2_training_mode': 'austin_budapest_major_calibration_weighted_pairwise_with_vrs_interaction_scoreline_features', 'example_count': 1924}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: fnatic, FaZe
- 0-3: Rare Atom, The Huns
- 晋级: B8, Ninjas in Pyjamas, M80, FlyQuest, PARIVISION, Legacy
- 预计通过概率: 97.3%
- 期望猜中数: 6.54

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| B8 | 4 | 276.3 | 37.9% | 35.3% | 20.1% | 93.3% | 4.5% | 1.9% | 0.3% | 3-0 |
| Ninjas in Pyjamas | 3 | 262.6 | 34.2% | 35.9% | 22.1% | 92.2% | 5.3% | 2.2% | 0.4% | 3-1 |
| M80 | 10 | 258.4 | 29.8% | 36.5% | 25.1% | 91.3% | 6.1% | 2.3% | 0.3% | 3-1 |
| fnatic | 6 | 250.5 | 32.2% | 36.2% | 22.8% | 91.2% | 5.7% | 2.6% | 0.5% | 3-1 |
| FlyQuest | 13 | 221.3 | 15.5% | 36.1% | 34.9% | 86.5% | 8.8% | 3.7% | 0.9% | 3-1 |
| FaZe | 1 | 196.6 | 26.5% | 32.8% | 27.0% | 86.2% | 9.7% | 3.4% | 0.6% | 3-1 |
| PARIVISION | 5 | 178.6 | 11.8% | 33.7% | 36.2% | 81.7% | 12.3% | 5.1% | 0.9% | 3-2 |
| Legacy | 8 | 16.4 | 6.0% | 19.4% | 28.9% | 54.2% | 32.3% | 11.7% | 1.8% | 2-3 |
| Imperial | 9 | 8.0 | 2.5% | 14.2% | 30.7% | 47.4% | 31.1% | 17.3% | 4.2% | 2-3 |
| NRG | 11 | -89.2 | 0.8% | 5.8% | 19.1% | 25.8% | 35.1% | 29.4% | 9.8% | 2-3 |
| GamerLegion | 2 | -142.3 | 1.0% | 5.8% | 13.6% | 20.4% | 40.3% | 30.1% | 9.2% | 2-3 |
| Fluxo | 14 | -162.7 | 0.4% | 3.2% | 9.9% | 13.4% | 30.0% | 36.3% | 20.3% | 1-3 |
| Lynn Vision | 7 | -303.3 | 0.6% | 2.1% | 3.5% | 6.2% | 27.3% | 43.6% | 22.9% | 1-3 |
| RED Canids | 15 | -324.4 | 0.6% | 1.5% | 2.6% | 4.7% | 22.5% | 40.9% | 32.0% | 1-3 |
| The Huns | 12 | -333.8 | 0.2% | 1.0% | 2.1% | 3.3% | 16.5% | 37.6% | 42.6% | 0-3 |
| Rare Atom | 16 | -399.7 | 0.2% | 0.6% | 1.3% | 2.1% | 12.5% | 32.0% | 53.4% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行没有启用地图 veto 模拟。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
