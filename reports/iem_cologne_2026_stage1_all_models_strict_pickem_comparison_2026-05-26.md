# Stage 1 模型对比

这份报告对比已生成的 Stage 1 预测输出。它是预测结果对比，不等同于已完成历史回测。

## 排名

| 排名 | 模型 | 配置模型 | 通过概率 | 期望猜中 | 3-0 | 0-3 | 晋级 |
|---:|---|---|---:|---:|---|---|---|
| 1 | vrs-reasonable | catboost | 61.6% | 4.89 | BIG, BetBoom | Lynn Vision, NRG | MIBR, THUNDER dOWNUNDER, SINNERS, HEROIC, GamerLegion, Sharks |
| 2 | vrs | vrs | 49.4% | 4.53 | GamerLegion, B8 | FlyQuest, THUNDER dOWNUNDER | BetBoom, BIG, HEROIC, MIBR, M80, SINNERS |
| 3 | hltv-feature | feature-score | 47.1% | 4.44 | GamerLegion, B8 | FlyQuest, THUNDER dOWNUNDER | BetBoom, BIG, HEROIC, M80, MIBR, SINNERS |
| 4 | vrs-tier | catboost | 45.0% | 4.33 | BIG, BetBoom | Lynn Vision, NRG | MIBR, THUNDER dOWNUNDER, SINNERS, FlyQuest, HEROIC, GamerLegion |
| 5 | strict-real-catboost | catboost | 44.7% | 4.32 | HEROIC, BetBoom | Lynn Vision, Sharks | B8, FlyQuest, TYLOO, M80, MIBR, GamerLegion |
| 6 | vrs-interaction | catboost | 44.2% | 4.29 | BIG, BetBoom | Lynn Vision, Gaimin Gladiators | MIBR, THUNDER dOWNUNDER, SINNERS, HEROIC, Sharks, FlyQuest |
| 7 | logistic | logistic | 37.6% | 4.09 | GamerLegion, B8 | FlyQuest, Lynn Vision | BIG, BetBoom, HEROIC, SINNERS, MIBR, M80 |
| 8 | weighted-finetune | catboost | 30.7% | 3.81 | GamerLegion, BIG | Lynn Vision, Liquid | BetBoom, HEROIC, B8, SINNERS, MIBR, M80 |
| 9 | factor-score | factor-score | 28.9% | 3.74 | M80, BetBoom | FlyQuest, Lynn Vision | B8, GamerLegion, BIG, HEROIC, MIBR, SINNERS |
| 10 | factor-weight | factor-score | 28.7% | 3.72 | M80, BetBoom | FlyQuest, Lynn Vision | B8, GamerLegion, BIG, HEROIC, MIBR, SINNERS |
| 11 | bo3-catboost-shallow | catboost | 28.6% | 3.73 | GamerLegion, BIG | Lynn Vision, Liquid | BetBoom, B8, HEROIC, SINNERS, MIBR, M80 |

## 策略

默认保守模型仍保持纯 VRS。`factor-veto`/`factor-score` 是机制完整的规则版；CatBoost 系列使用近 4 个月 16 队 vs VRS Top 100 的 BO3 match/map 基础语料、BO3 地图禁选动作、Glicko 风格不确定性特征，以及 Austin/Budapest Stage 1 标签校准。所有 CatBoost 结果仍应视为实验预测，不等同于稳定历史回测结论。
