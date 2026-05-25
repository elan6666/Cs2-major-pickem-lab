# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/snapshots/starladder_budapest_major_2025_stage1_2025-10-06.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_vrs_reasonable_scoreline_weighted_finetune_2026-05-26.json`
- model: `catboost`
- model_target: `advanced`
- feature_snapshot: `data/snapshots/starladder_budapest_major_2025_stage1_2025-10-06.csv`
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
- map_stats: ``
- map_pool: ``
- veto_policy: ``
- bandit_policy_json: ``
- catboost_metadata: `{'model_path': 'reports/models/bo3_stage1_catboost_vrs_reasonable_scoreline_weighted_finetune_2026-05-26.cbm', 'stage1_training_mode': 'last_4_month_bo3_pretrain', 'stage2_training_mode': 'austin_budapest_major_calibration_weighted_pairwise_with_vrs_reasonable_scoreline_features', 'example_count': 1924}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: B8, Ninjas in Pyjamas
- 0-3: Rare Atom, The Huns
- 晋级(3-1/3-2): FlyQuest, PARIVISION, FaZe, M80, fnatic, Imperial
- 预计通过概率: 72.6%
- 期望猜中数: 5.45

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级(3-1/3-2) | 总晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| B8 | 4 | 270.8 | 36.9% | 36.4% | 20.5% | 56.9% | 93.8% | 4.2% | 1.8% | 0.2% | 3-0 |
| M80 | 10 | 271.8 | 33.6% | 36.7% | 23.1% | 59.9% | 93.4% | 4.6% | 1.7% | 0.2% | 3-1 |
| Ninjas in Pyjamas | 3 | 264.0 | 34.9% | 36.3% | 21.8% | 58.1% | 93.0% | 4.7% | 1.9% | 0.3% | 3-1 |
| fnatic | 6 | 242.5 | 32.0% | 36.5% | 23.1% | 59.6% | 91.6% | 5.9% | 2.2% | 0.4% | 3-1 |
| FlyQuest | 13 | 238.3 | 18.1% | 38.2% | 32.9% | 71.1% | 89.2% | 7.1% | 3.0% | 0.6% | 3-1 |
| FaZe | 1 | 192.3 | 24.6% | 33.2% | 28.4% | 61.6% | 86.3% | 9.6% | 3.4% | 0.7% | 3-1 |
| PARIVISION | 5 | 166.5 | 9.0% | 32.6% | 38.4% | 71.0% | 80.0% | 13.6% | 5.4% | 1.0% | 3-2 |
| Imperial | 9 | 48.0 | 3.2% | 17.0% | 35.0% | 52.0% | 55.2% | 28.1% | 13.7% | 3.0% | 3-2 |
| Legacy | 8 | -7.3 | 4.2% | 15.5% | 26.7% | 42.3% | 46.5% | 38.3% | 13.4% | 1.8% | 2-3 |
| NRG | 11 | -89.9 | 0.7% | 5.2% | 18.2% | 23.3% | 24.0% | 37.1% | 29.5% | 9.3% | 2-3 |
| GamerLegion | 2 | -150.7 | 0.9% | 5.1% | 12.7% | 17.8% | 18.6% | 40.6% | 32.0% | 8.8% | 2-3 |
| Fluxo | 14 | -138.7 | 0.4% | 3.1% | 11.4% | 14.5% | 14.9% | 32.5% | 35.7% | 16.8% | 1-3 |
| Lynn Vision | 7 | -315.2 | 0.6% | 1.6% | 2.8% | 4.4% | 5.0% | 26.1% | 45.2% | 23.7% | 1-3 |
| RED Canids | 15 | -337.9 | 0.4% | 1.3% | 2.0% | 3.4% | 3.8% | 20.6% | 41.0% | 34.7% | 1-3 |
| The Huns | 12 | -335.2 | 0.2% | 0.8% | 1.7% | 2.6% | 2.7% | 15.8% | 38.4% | 43.1% | 0-3 |
| Rare Atom | 16 | -397.9 | 0.2% | 0.6% | 1.1% | 1.7% | 1.9% | 11.3% | 31.6% | 55.2% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行没有启用地图 veto 模拟。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
- Pick'Em 计分严格按槽位判断：3-0 槽只认 3-0，晋级槽只认 3-1/3-2，0-3 槽只认 0-3。
