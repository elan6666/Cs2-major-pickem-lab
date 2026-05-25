# Stage 1 BO1/BO3 校准报告

这份报告用历史 Stage 1 样本微调全局概率校准层；重点是分别选择 BO1 和 BO3 的收缩参数，避免把两种赛制当成同一种不确定性。

## 最终参数

- scale: `105.0`
- bo1_shrink: `0.7`
- bo3_shrink: `1.0`
- veto_weight: `1.0`

## 训练目标

- advanced 权重：50%
- went_3_0 权重：25%
- went_0_3 权重：25%

## 训练集内指标

- objective: `0.1965`
- brier: `0.0542`
- advanced_log_loss: `0.1817`
- went_3_0_log_loss: `0.2301`
- went_0_3_log_loss: `0.1924`

## Leave-One-Event-Out

| 测试赛事 | 选择参数 | 测试 objective | 测试 brier |
|---|---|---:|---:|
| blast_austin_major_2025_stage1 | scale=105.0, bo1=0.7, bo3=1.0, veto=1.0 | 0.1779 | 0.0467 |
| starladder_budapest_major_2025_stage1 | scale=105.0, bo1=0.7, bo3=1.0, veto=1.0 | 0.2135 | 0.0619 |

## 重要限制

当前历史样本只有两个新赛制 Stage 1，且历史 map-stats 不完整。因此这版校准主要学习 Swiss/BO1/BO3 概率尺度；`veto_weight` 保持为 1.0，用于当前赛事有地图数据时完整启用 ban/pick 修正。
