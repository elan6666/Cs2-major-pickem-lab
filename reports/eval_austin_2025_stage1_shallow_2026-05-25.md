# CS2 Major Stage 1 预测报告

## 运行设置

- teams: `data/snapshots/blast_austin_major_2025_stage1_2025-06-02.csv`
- locked_results: ``
- snapshot: ``
- model_json: `reports/models/bo3_stage1_catboost_pairwise_complete_2026-05-25.json`
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
- catboost_metadata: `{'model_path': 'reports/models/bo3_stage1_catboost_pairwise_complete_2026-05-25.cbm', 'stage1_training_mode': 'last_4_month_bo3_pretrain', 'stage2_training_mode': 'austin_budapest_major_calibration_weighted_pairwise', 'example_count': 1924}`
- pass_threshold: `5`
- three_zero_picks: `2`
- zero_three_picks: `2`
- advance_picks: `6`

## 推荐 Pick'Em 卡

- 3-0: TYLOO, FlyQuest
- 0-3: Metizport, Fluxo
- 晋级: HEROIC, B8, BetBoom, OG, Nemiga, Legacy
- 预计通过概率: 93.0%
- 期望猜中数: 6.14

## 队伍概率

| 队伍 | 种子 | 分数 | 3-0 | 3-1 | 3-2 | 晋级 | 2-3 | 1-3 | 0-3 | 最常见战绩 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| HEROIC | 1 | 211.7 | 35.1% | 36.7% | 20.6% | 92.3% | 4.4% | 2.5% | 0.7% | 3-1 |
| B8 | 4 | 160.9 | 25.9% | 34.9% | 26.6% | 87.3% | 7.2% | 4.3% | 1.1% | 3-1 |
| BetBoom | 8 | 135.5 | 28.5% | 32.5% | 23.4% | 84.4% | 9.0% | 5.2% | 1.5% | 3-1 |
| OG | 9 | 137.9 | 16.4% | 33.1% | 31.4% | 80.9% | 9.9% | 6.9% | 2.3% | 3-1 |
| TYLOO | 3 | 99.2 | 24.6% | 30.6% | 24.4% | 79.7% | 11.9% | 6.9% | 1.5% | 3-1 |
| Nemiga | 12 | 116.3 | 16.1% | 30.0% | 31.5% | 77.6% | 11.8% | 8.0% | 2.7% | 3-2 |
| FlyQuest | 5 | 86.5 | 21.5% | 27.2% | 27.0% | 75.8% | 14.2% | 8.2% | 1.8% | 3-1 |
| Legacy | 14 | 39.5 | 10.6% | 21.8% | 27.6% | 60.1% | 21.1% | 13.9% | 4.9% | 3-2 |
| NRG | 7 | -68.6 | 5.8% | 12.1% | 16.1% | 34.0% | 31.3% | 25.5% | 9.2% | 2-3 |
| Lynn Vision | 6 | -59.9 | 3.7% | 10.3% | 18.1% | 32.1% | 28.4% | 26.8% | 12.6% | 2-3 |
| Complexity | 2 | -93.3 | 4.7% | 9.6% | 13.7% | 28.0% | 34.5% | 28.1% | 9.4% | 2-3 |
| Imperial | 11 | -99.7 | 2.1% | 6.2% | 12.5% | 20.9% | 25.4% | 31.2% | 22.5% | 1-3 |
| Chinggis Warriors | 10 | -130.1 | 2.1% | 5.9% | 10.2% | 18.1% | 28.5% | 34.4% | 19.0% | 1-3 |
| Wildcard | 13 | -117.8 | 1.6% | 5.0% | 10.0% | 16.5% | 25.3% | 32.8% | 25.4% | 1-3 |
| Metizport | 16 | -205.5 | 0.7% | 2.4% | 3.7% | 6.8% | 17.1% | 30.9% | 45.2% | 0-3 |
| Fluxo | 15 | -218.2 | 0.7% | 1.8% | 3.1% | 5.6% | 19.9% | 34.3% | 40.2% | 0-3 |

## 注意事项

- 队伍分数默认来自输入 CSV；如果设置了 `model_json` 或 `feature_snapshot`，模型模式会用训练模型或特征快照分数替换。
- 赔率不作为模型输入。
- 特征快照质量取决于缓存来源数据与截止窗口；发布前需要复核来源覆盖。
- 本次运行没有启用地图 veto 模拟。
- 瑞士轮配对按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表，并尽量避免重复交手。
