# Stage 1 加权重训评估

| 模型 | Pick'Em 通过率 | 期望猜中 | Brier 分数 | 对数损失 | 晋级命中率 | 历史事件 | 历史队伍 |
|---|---:|---:|---:|---:|---:|---:|---:|
| vrs-tier-scoreline-map-catboost | 78.0% | 5.38 | 0.0544 | 0.2085 | 90.6% | 2 | 32 |
| weighted-finetune-latest | 62.6% | 4.88 | 0.0503 | 0.2019 | 90.6% | 2 | 32 |

## 口径

Pick'Em 通过率和期望猜中来自当前 Cologne Stage 1 模拟；Brier 分数、对数损失、晋级命中率来自 Austin 2025 Stage 1 与 Budapest 2025 Stage 1 的赛前预测对最终晋级标签回测。
