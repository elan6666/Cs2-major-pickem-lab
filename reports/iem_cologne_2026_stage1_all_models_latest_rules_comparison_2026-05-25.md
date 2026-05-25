# Stage 1 模型对比

这份报告对比已生成的 Stage 1 预测输出。它是预测结果对比，不等同于已完成历史回测。

## 排名

| 排名 | 模型 | 配置模型 | 通过概率 | 期望猜中 | 3-0 | 0-3 | 晋级 |
|---:|---|---|---:|---:|---|---|---|
| 1 | catboost-major-only-latest | catboost | 85.4% | 5.67 | B8, BIG | Lynn Vision, THUNDER dOWNUNDER | HEROIC, BetBoom, M80, FlyQuest, TYLOO, SINNERS |
| 2 | vrs-latest | vrs | 81.0% | 5.54 | HEROIC, BIG | FlyQuest, THUNDER dOWNUNDER | GamerLegion, B8, BetBoom, MIBR, M80, SINNERS |
| 3 | hltv-feature-latest | feature-score | 80.3% | 5.48 | HEROIC, BetBoom | FlyQuest, Lynn Vision | GamerLegion, B8, BIG, M80, MIBR, SINNERS |
| 4 | strict-real-catboost-latest | catboost | 75.8% | 5.32 | M80, FlyQuest | Lynn Vision, Sharks | HEROIC, BetBoom, B8, TYLOO, GamerLegion, MIBR |
| 5 | logistic-latest | logistic | 72.3% | 5.18 | HEROIC, BetBoom | FlyQuest, Liquid | GamerLegion, B8, BIG, SINNERS, MIBR, M80 |
| 6 | weighted-finetune-latest | catboost | 62.6% | 4.88 | BetBoom, SINNERS | Lynn Vision, Liquid | GamerLegion, BIG, HEROIC, B8, MIBR, M80 |
| 7 | factor-score-latest | factor-score | 61.1% | 4.83 | M80, BetBoom | FlyQuest, Liquid | GamerLegion, B8, BIG, HEROIC, MIBR, SINNERS |
| 8 | factor-weight-latest | factor-score | 60.5% | 4.81 | M80, BetBoom | FlyQuest, Liquid | B8, BIG, GamerLegion, HEROIC, MIBR, SINNERS |
| 9 | bo3-catboost-shallow-latest | catboost | 60.1% | 4.80 | BetBoom, HEROIC | Lynn Vision, Liquid | BIG, GamerLegion, B8, SINNERS, M80, MIBR |

## 策略

默认保守模型仍保持纯 VRS。`factor-veto`/`factor-score` 是机制完整的规则版；CatBoost 系列使用近 4 个月 16 队 vs VRS Top 100 的 BO3 match/map 基础语料、BO3 地图禁选动作、Glicko 风格不确定性特征，以及 Austin/Budapest Stage 1 标签校准。所有 CatBoost 结果仍应视为实验预测，不等同于稳定历史回测结论。
