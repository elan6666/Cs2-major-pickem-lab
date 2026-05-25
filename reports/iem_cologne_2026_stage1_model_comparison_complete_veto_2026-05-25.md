# Stage 1 模型对比

这份报告对比已生成的 Stage 1 预测输出。它是预测结果对比，不等同于已完成历史回测。

## 排名

| 排名 | 模型 | 配置模型 | 通过概率 | 期望猜中 | 3-0 | 0-3 | 晋级 |
|---:|---|---|---:|---:|---|---|---|
| 1 | strict-real-catboost-complete-veto | catboost | 75.0% | 5.33 | HEROIC, M80 | Lynn Vision, Sharks | BetBoom, B8, FlyQuest, TYLOO, Liquid, GamerLegion |
| 2 | vrs-complete-veto | vrs | 73.8% | 5.25 | B8, HEROIC | FlyQuest, THUNDER dOWNUNDER | BIG, GamerLegion, BetBoom, SINNERS, M80, TYLOO |
| 3 | factor-complete-veto | factor-score | 63.7% | 4.91 | M80, B8 | FlyQuest, Liquid | BIG, BetBoom, GamerLegion, HEROIC, SINNERS, TYLOO |
| 4 | bo3-catboost-complete-veto | catboost | 59.3% | 4.79 | SINNERS, HEROIC | Lynn Vision, Liquid | BIG, BetBoom, GamerLegion, B8, M80, MIBR |

## 策略

默认保守模型仍保持 VRS-only。`factor-veto`/`factor-score` 是机制完整的规则版；`strict-real-catboost` 使用小样本 HLTV pretrain；`bo3-catboost-complete-veto` 使用 BO3.gg 近 4 个月 16 队 vs VRS Top 100 match/map pretrain、BO3 match detail + HLTV supplement ordered veto actions、Glicko-style uncertainty features 和 CatBoost。瑞士轮配对已按 Valve Major 规则处理：首轮种子配对，第 2/3 轮高种子对可用低种子，第 4/5 轮 6 队组使用官方优先配对表。所有 CatBoost 结果仍应视为实验预测，不等同于稳定历史回测结论。
