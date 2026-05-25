# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/snapshots/starladder_budapest_major_2025_stage1_2025-10-06.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_pairwise_weighted_finetune_2026-05-25.json`
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
- catboost_metadata: `{'model_path': 'reports/models/bo3_stage1_catboost_pairwise_weighted_finetune_2026-05-25.cbm', 'stage1_training_mode': 'last_4_month_bo3_pretrain', 'stage2_training_mode': 'combined_weighted_bo3_pretrain_major_finetune', 'example_count': 1924}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: Ninjas in Pyjamas, FaZe
- 0-3: Rare Atom, The Huns
- 晋级: M80, B8, fnatic, FlyQuest, PARIVISION, Imperial
- 预计通过概率: 97.5%
- 期望猜中数: 6.50

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| M80 | 10 | 271.4 | 32.7% | 36.1% | 23.6% | 92.3% | 5.2% | 2.1% | 0.3% | 3-1 |
| B8 | 4 | 261.9 | 35.1% | 35.5% | 21.5% | 92.2% | 5.3% | 2.2% | 0.3% | 3-1 |
| Ninjas in Pyjamas | 3 | 258.0 | 32.9% | 36.0% | 22.8% | 91.6% | 5.8% | 2.2% | 0.4% | 3-1 |
| fnatic | 6 | 246.5 | 31.9% | 35.9% | 23.3% | 91.1% | 5.8% | 2.5% | 0.5% | 3-1 |
| FlyQuest | 13 | 246.4 | 19.5% | 37.6% | 32.2% | 89.4% | 7.1% | 2.9% | 0.6% | 3-1 |
| FaZe | 1 | 200.6 | 26.2% | 33.5% | 27.0% | 86.7% | 9.3% | 3.4% | 0.7% | 3-1 |
| PARIVISION | 5 | 165.9 | 9.6% | 32.2% | 37.1% | 78.8% | 14.3% | 5.8% | 1.1% | 3-2 |
| Legacy | 8 | 2.6 | 5.4% | 17.6% | 27.7% | 50.7% | 34.4% | 13.0% | 2.0% | 2-3 |
| Imperial | 9 | 20.2 | 2.8% | 15.1% | 31.5% | 49.4% | 30.1% | 16.7% | 3.8% | 3-2 |
| NRG | 11 | -93.7 | 0.8% | 5.5% | 18.2% | 24.4% | 35.1% | 30.4% | 10.1% | 2-3 |
| GamerLegion | 2 | -117.7 | 1.3% | 6.7% | 15.8% | 23.8% | 40.2% | 28.6% | 7.5% | 2-3 |
| Fluxo | 14 | -160.5 | 0.4% | 3.2% | 9.8% | 13.4% | 29.5% | 36.7% | 20.3% | 1-3 |
| Lynn Vision | 7 | -295.2 | 0.7% | 2.2% | 3.7% | 6.6% | 27.8% | 43.6% | 22.1% | 1-3 |
| RED Canids | 15 | -322.0 | 0.5% | 1.5% | 2.5% | 4.4% | 22.1% | 40.8% | 32.6% | 1-3 |
| The Huns | 12 | -320.9 | 0.2% | 1.0% | 2.2% | 3.4% | 17.3% | 38.7% | 40.6% | 0-3 |
| Rare Atom | 16 | -427.8 | 0.2% | 0.5% | 1.2% | 1.8% | 10.6% | 30.5% | 57.1% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行没有启用地图 veto 模拟。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
