# Stage 1 CatBoost 训练报告

## 两阶段训练状态

- 第一阶段：近 4 个月 16 支队伍 vs VRS Top 100 match/map 预训练行数：1500
- 第一阶段模式：`last_4_month_bo3_pretrain`
- 第二阶段：`austin_budapest_major_calibration_weighted_pairwise`
- 训练样本：1924 pairwise examples

## 模型参数

- iterations: 120
- depth: 3
- learning_rate: 0.05
- l2_leaf_reg: 8.0

## 说明

这个模型已经能完整进入 Stage 1 Swiss + Pick'Em 预测链路。若没有真实近 4 个月 match/map 预训练表，它会退化为 Austin/Budapest Stage 1 最终标签的弱监督 pairwise 训练，不能当作稳定生产模型。
