# Factor-Veto 校准报告

这份报告用历史 Stage 1 样本微调 `factor-veto` 的全局概率校准层；它不改可解释因子权重，也不改 ban/pick 规则本身。

## 最终参数

- scale: `150.0`
- bo1_shrink: `0.55`
- bo3_shrink: `0.9`
- veto_weight: `1.0`

## 训练目标

- advanced 权重：50%
- went_3_0 权重：25%
- went_0_3 权重：25%

## 训练集内指标

- objective: `0.5137`
- brier: `0.1647`
- advanced_log_loss: `0.6580`
- went_3_0_log_loss: `0.4172`
- went_0_3_log_loss: `0.3217`

## Leave-One-Event-Out

| 测试赛事 | 选择参数 | 测试 objective | 测试 brier |
|---|---|---:|---:|
| blast_austin_major_2025_stage1 | scale=150.0, bo1=0.55, bo3=0.9, veto=1.0 | 0.4670 | 0.1578 |
| starladder_budapest_major_2025_stage1 | scale=150.0, bo1=0.55, bo3=0.9, veto=1.0 | 0.5469 | 0.1695 |

## 重要限制

当前历史样本只有两个新赛制 Stage 1，且历史 map-stats 不完整。因此这版校准主要学习 Swiss/BO1/BO3 概率尺度；`veto_weight` 保持为 1.0，用于当前赛事有地图数据时完整启用 ban/pick 修正。
