# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/snapshots/blast_austin_major_2025_stage1_2025-06-02.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_pairwise_weighted_finetune_2026-05-25.json`
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
- catboost_metadata: `{'model_path': 'reports/models/bo3_stage1_catboost_pairwise_weighted_finetune_2026-05-25.cbm', 'stage1_training_mode': 'last_4_month_bo3_pretrain', 'stage2_training_mode': 'combined_weighted_bo3_pretrain_major_finetune', 'example_count': 1924}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: HEROIC, TYLOO
- 0-3: Metizport, Fluxo
- 晋级: B8, BetBoom, OG, Nemiga, Legacy, Lynn Vision
- 预计通过概率: 96.4%
- 期望猜中数: 6.50

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| HEROIC | 1 | 383.4 | 46.9% | 35.1% | 15.3% | 97.2% | 1.5% | 0.9% | 0.3% | 3-0 |
| B8 | 4 | 330.3 | 39.6% | 37.5% | 18.9% | 96.0% | 2.3% | 1.4% | 0.4% | 3-0 |
| BetBoom | 8 | 260.9 | 31.9% | 38.6% | 22.7% | 93.2% | 4.2% | 2.0% | 0.5% | 3-1 |
| OG | 9 | 230.6 | 13.9% | 37.1% | 36.1% | 87.1% | 7.1% | 4.5% | 1.2% | 3-1 |
| Nemiga | 12 | 223.2 | 15.4% | 37.8% | 33.0% | 86.2% | 7.8% | 4.4% | 1.5% | 3-1 |
| TYLOO | 3 | 127.4 | 22.0% | 31.3% | 27.5% | 80.8% | 13.0% | 5.5% | 0.8% | 3-1 |
| Legacy | 14 | 74.8 | 8.6% | 21.6% | 36.0% | 66.1% | 21.3% | 10.0% | 2.6% | 3-2 |
| Lynn Vision | 6 | 13.7 | 5.6% | 17.8% | 32.2% | 55.6% | 26.3% | 14.1% | 4.0% | 3-2 |
| FlyQuest | 5 | 1.3 | 7.2% | 17.8% | 26.9% | 51.9% | 31.3% | 14.2% | 2.7% | 2-3 |
| NRG | 7 | -89.4 | 4.7% | 10.3% | 21.3% | 36.3% | 35.9% | 23.6% | 4.2% | 2-3 |
| Wildcard | 13 | -149.4 | 1.2% | 5.3% | 13.5% | 20.0% | 33.0% | 31.1% | 16.0% | 2-3 |
| Complexity | 2 | -256.8 | 1.3% | 3.7% | 5.9% | 10.9% | 38.1% | 40.0% | 10.9% | 1-3 |
| Imperial | 11 | -282.0 | 0.5% | 2.0% | 4.2% | 6.7% | 21.1% | 37.6% | 34.7% | 1-3 |
| Chinggis Warriors | 10 | -303.1 | 0.5% | 2.0% | 3.5% | 6.1% | 26.1% | 44.8% | 23.1% | 1-3 |
| Metizport | 16 | -370.6 | 0.3% | 1.1% | 1.6% | 3.0% | 14.4% | 33.0% | 49.6% | 0-3 |
| Fluxo | 15 | -370.9 | 0.3% | 1.0% | 1.6% | 2.8% | 16.7% | 32.9% | 47.6% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行没有启用地图 veto 模拟。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
