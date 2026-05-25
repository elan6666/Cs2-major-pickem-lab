# CS2 Major Pick'Em 预测器

这是一个面向 CS2 Major Pick'Em 的本地预测工具。当前主目标是 IEM Cologne Major 2026 Stage 1：模拟 16 队瑞士轮，输出每队 3-0、0-3、晋级、最终战绩分布，并给出以“猜中至少 5 个”为目标的 Pick'Em 推荐卡。

## GitHub 元信息建议

```text
Repository name: cs2-major-pickem-lab
Description: CS2 Major Pick'Em simulator with weighted CatBoost finetuning, map veto modeling, and Valve-style Swiss pairing checks.
Topics: cs2, counter-strike, pickem, major, esports, swiss-system, catboost, map-veto, monte-carlo, prediction-model
```

中文一句话：这是一个可复现的 CS2 Major Pick'Em 研究工具，主模型使用近 4 个月 BO3 数据预训练、Austin/Budapest Major 加权校准、两层 ban/pick 策略和 Valve/majors.im 风格瑞士轮模拟。

默认 Stage 1 Pick'Em 规则：

```text
2 个 3-0
2 个 0-3
6 个 3-1 / 3-2 晋级
通过线 = 至少猜中 5 个
```

## 当前主模型

当前 README 以 `vrs-tier-scoreline-map-catboost` 作为主模型。它是在 `weighted-finetune-latest` 链路上加入 V社排名分层地图胜率和 CS2 比分质量后的增强版本：

```text
近 4 个月 16 支队伍 vs VRS Top 100 的 BO3 match/map 数据
-> Austin 2025 Stage 1 + Budapest 2025 Stage 1 加权校准
-> Glicko 风格实力/不确定性特征
-> CatBoost 两两对比模型
-> V社排名 top10/20/30/40/50/70/100 分层地图强度
-> MR12/加时感知比分质量、净胜回合、惜败信号
-> 近期 BO3 ban/pick 基础倾向 + Major ban/pick 修正
-> Valve/majors.im 风格 16 队瑞士轮模拟
-> Pick'Em 通过率优化
```

最新同口径结果：

```text
vrs-tier-scoreline-map-catboost
通过率：78.0%
期望猜中：5.38
3-0：BetBoom, GamerLegion
0-3：Lynn Vision, NRG
晋级：BIG, MIBR, THUNDER dOWNUNDER, SINNERS, FlyQuest, HEROIC
```

扩展模型：`weighted-finetune-latest` 保留为上一代主模型对照；`vrs-complete-veto` 保留为保守 VRS 基线扩展。主模型历史 Austin/Budapest 晋级评估为 Brier 0.0544、对数损失 0.2085、晋级命中率 90.6%。

## 环境

```bash
conda create -y -n cs2-major-predictor -c conda-forge --override-channels --no-default-packages python=3.11 pip
conda activate cs2-major-predictor
```

如果本地 conda 能直接使用 `conda-forge`，也可以运行：

```bash
conda env create -f environment.yml
```

## 快速运行

```bash
python3 -m stage1_predictor.cli \
  --teams data/sample_stage1_teams.csv \
  --simulations 50000 \
  --seed 42 \
  --report reports/stage1_prediction_sample.md \
  --csv reports/stage1_prediction_sample.csv \
  --json reports/stage1_prediction_sample.json
```

## 生成 Cologne Stage 1 输入

Cologne Stage 1 当前使用 majors.im/Valve 2026-05-04 global standings 的 Stage 内种子顺序，并以 2026-05-23 作为当前特征截止日。

```bash
python3 -m stage1_predictor.build_stage_teams \
  --config data/stage_configs/iem_cologne_2026_stage1.json \
  --output data/iem_cologne_2026_stage1_teams.csv
```

## 扩展模型：weighted-finetune-latest

这是上一代主模型，现作为扩展模型和消融对照保留。它使用最新 Cologne 队伍、最新因素快照、完整 BO3 map-stats、两层 ban/pick 策略、历史校准参数和最新瑞士轮规则：

```bash
python3 -m stage1_predictor.cli \
  --teams data/iem_cologne_2026_stage1_teams.csv \
  --model catboost \
  --model-json reports/models/bo3_stage1_catboost_pairwise_weighted_finetune_2026-05-25.json \
  --model-target advanced \
  --feature-snapshot data/snapshots/iem_cologne_major_2026_stage1_factor_weights_trained_2026-05-25.csv \
  --calibration-json reports/stage1_factor_veto_calibration.json \
  --map-stats data/bo3/bo3_stage1_last4months_map_stats_complete_2026-05-25.csv \
  --map-pool Ancient,Anubis,Dust2,Inferno,Mirage,Nuke,Overpass \
  --veto-policy contextual-bandit \
  --bandit-policy-json reports/models/bo3_two_layer_veto_bandit_policy_2026-05-25.json \
  --simulations 10000 \
  --seed 42 \
  --report reports/iem_cologne_2026_stage1_prediction_weighted-finetune-latest_latest_rules_2026-05-25.md \
  --csv reports/iem_cologne_2026_stage1_prediction_weighted-finetune-latest_latest_rules_2026-05-25.csv \
  --json reports/iem_cologne_2026_stage1_prediction_weighted-finetune-latest_latest_rules_2026-05-25.json
```

## 额外扩展模型：vrs-complete-veto

`vrs-complete-veto` 使用 VRS 分数作为队伍强度基础，并启用 complete veto/map-stats 链路。它适合作为保守对照或扩展模型，不是当前 README 主模型。

```bash
python3 -m stage1_predictor.cli \
  --teams data/iem_cologne_2026_stage1_teams.csv \
  --model vrs \
  --calibration-json reports/stage1_factor_veto_calibration.json \
  --map-stats data/bo3/bo3_stage1_last4months_map_stats_complete_2026-05-25.csv \
  --map-pool Ancient,Anubis,Dust2,Inferno,Mirage,Nuke,Overpass \
  --veto-policy contextual-bandit \
  --bandit-policy-json reports/models/bo3_true_veto_bandit_policy_complete_2026-05-25.json \
  --simulations 10000 \
  --seed 42 \
  --report reports/iem_cologne_2026_stage1_prediction_vrs_complete_veto_2026-05-25.md \
  --csv reports/iem_cologne_2026_stage1_prediction_vrs_complete_veto_2026-05-25.csv \
  --json reports/iem_cologne_2026_stage1_prediction_vrs_complete_veto_2026-05-25.json
```

当前最新同口径重跑中，VRS 的最新版为 `vrs-latest`，使用两层 ban/pick 策略，结果为 81.0% 通过、5.54 期望猜中；`vrs-complete-veto` 保留为命名扩展产物和历史对照。

## 当前主模型：vrs-tier-scoreline-map-catboost

这版模型把每支队伍每张图按对手 V社排名拆开：累计层使用前10、前20、前30、前40、前50、前70、前100；诊断层保留 1-10、11-20、21-30、31-40、41-50、51-70、71-100。每个队伍-地图行包含出场数、胜场、原始胜率、贝叶斯平滑胜率、平均净胜回合、平均比分质量、加时次数和惜败次数。

比分质量按 CS2 MR12 与加时处理：13:3 是强负面，11:13 是小负面，14:16 / 16:14 这种加时图接近中性小幅度信号。小样本分层胜率会往队伍该图整体水平和全局地图基线回拉，避免一场爆冷或刷弱队直接支配模型。

```bash
python3 -m stage1_predictor.build_vrs_tier_map_features \
  --matches data/bo3/bo3_stage1_last4months_matches_complete_2026-05-25.csv \
  --maps data/bo3/bo3_stage1_last4months_maps_complete_2026-05-25.csv \
  --feature-snapshot data/snapshots/iem_cologne_major_2026_stage1_factor_weights_trained_2026-05-25.csv \
  --base-map-stats data/bo3/bo3_stage1_last4months_map_stats_complete_2026-05-25.csv \
  --team-map-output data/bo3/bo3_stage1_last4months_vrs_tier_scoreline_map_features_2026-05-25.csv \
  --snapshot-output data/snapshots/iem_cologne_major_2026_stage1_vrs_tier_scoreline_features_2026-05-25.csv \
  --map-stats-output data/bo3/bo3_stage1_last4months_vrs_tier_scoreline_map_stats_2026-05-25.csv \
  --report reports/vrs_tier_scoreline_map_features_2026-05-25.md
```

```bash
python3 -m stage1_predictor.build_catboost_pretrain_from_bo3 \
  --matches data/bo3/bo3_stage1_last4months_matches_complete_2026-05-25.csv \
  --maps data/bo3/bo3_stage1_last4months_maps_complete_2026-05-25.csv \
  --feature-snapshot data/snapshots/iem_cologne_major_2026_stage1_vrs_tier_scoreline_features_2026-05-25.csv \
  --vrs-tier-map-features data/bo3/bo3_stage1_last4months_vrs_tier_scoreline_map_features_2026-05-25.csv \
  --output data/bo3/bo3_stage1_last4months_catboost_vrs_tier_scoreline_pretrain_2026-05-25.csv \
  --report reports/bo3_stage1_last4months_catboost_vrs_tier_scoreline_pretrain_2026-05-25.md
```

```bash
python3 -m stage1_predictor.train_catboost_model \
  --pretrain-matches data/bo3/bo3_stage1_last4months_catboost_vrs_tier_scoreline_pretrain_2026-05-25.csv \
  --require-real-pretrain \
  --snapshots data/snapshots/blast_austin_major_2025_stage1_2025-06-02.csv data/snapshots/starladder_budapest_major_2025_stage1_2025-10-06.csv \
  --labels data/labels/blast_austin_2025_stage1_labels.csv data/labels/starladder_budapest_2025_stage1_labels.csv \
  --pretrain-weight-scale 1.0 \
  --major-weight-scale 2.5 \
  --training-mode-name austin_budapest_major_calibration_weighted_pairwise_with_vrs_tier_scoreline_features \
  --iterations 300 \
  --depth 4 \
  --learning-rate 0.035 \
  --l2-leaf-reg 10.0 \
  --model-output reports/models/bo3_stage1_catboost_vrs_tier_scoreline_weighted_finetune_2026-05-25.cbm \
  --metadata-json reports/models/bo3_stage1_catboost_vrs_tier_scoreline_weighted_finetune_2026-05-25.json \
  --report reports/bo3_stage1_catboost_vrs_tier_scoreline_training_2026-05-25.md
```

```bash
python3 -m stage1_predictor.cli \
  --teams data/iem_cologne_2026_stage1_teams.csv \
  --model catboost \
  --model-json reports/models/bo3_stage1_catboost_vrs_tier_scoreline_weighted_finetune_2026-05-25.json \
  --feature-snapshot data/snapshots/iem_cologne_major_2026_stage1_vrs_tier_scoreline_features_2026-05-25.csv \
  --calibration-json reports/stage1_factor_veto_calibration.json \
  --map-stats data/bo3/bo3_stage1_last4months_vrs_tier_scoreline_map_stats_2026-05-25.csv \
  --map-pool Ancient,Anubis,Dust2,Inferno,Mirage,Nuke,Overpass \
  --veto-policy contextual-bandit \
  --bandit-policy-json reports/models/bo3_two_layer_veto_bandit_policy_2026-05-25.json \
  --simulations 10000 \
  --seed 42 \
  --report reports/iem_cologne_2026_stage1_prediction_vrs-tier-scoreline-map-catboost_2026-05-25.md \
  --csv reports/iem_cologne_2026_stage1_prediction_vrs-tier-scoreline-map-catboost_2026-05-25.csv \
  --json reports/iem_cologne_2026_stage1_prediction_vrs-tier-scoreline-map-catboost_2026-05-25.json
```

## 可用模型

```text
vrs            默认 VRS 分数基线
feature-score  使用特征快照中的指定分数字段
factor-score   因素综合模型：VRS + HLTV + 样本 + 赛区/路径代理
logistic       两个历史 Stage 1 事件训练出的实验逻辑回归基线
elo            规划中，等待历史 match-level 数据
glicko         已作为 CatBoost 的队伍实力/不确定性特征层
catboost       已可运行：CatBoost + Glicko 特征 + contextual-bandit veto
xgboost        规划中，作为 CatBoost 之后的对照实验
lightgbm       规划中，等待更多验证数据和依赖
```

## Weighted Finetune 扩展模型训练

这条链路已经能完整预测 Stage 1：

```text
Glicko-style mean/RD features
-> CatBoost pairwise match model
-> contextual-bandit veto prior
-> BO1/BO3 Swiss Monte Carlo
-> Pick'Em optimizer
```

`weighted-finetune-latest` 扩展模型训练命令：

```bash
python3 -m stage1_predictor.train_catboost_model \
  --pretrain-matches data/bo3/bo3_stage1_last4months_catboost_pretrain_complete_2026-05-25.csv \
  --require-real-pretrain \
  --snapshots data/snapshots/blast_austin_major_2025_stage1_2025-06-02.csv data/snapshots/starladder_budapest_major_2025_stage1_2025-10-06.csv \
  --labels data/labels/blast_austin_2025_stage1_labels.csv data/labels/starladder_budapest_2025_stage1_labels.csv \
  --pretrain-weight-scale 1.0 \
  --major-weight-scale 2.5 \
  --training-mode-name combined_weighted_bo3_pretrain_major_finetune \
  --iterations 300 \
  --depth 4 \
  --learning-rate 0.035 \
  --l2-leaf-reg 10.0 \
  --model-output reports/models/bo3_stage1_catboost_pairwise_weighted_finetune_2026-05-25.cbm \
  --metadata-json reports/models/bo3_stage1_catboost_pairwise_weighted_finetune_2026-05-25.json \
  --report reports/bo3_stage1_catboost_training_weighted_finetune_2026-05-25.md
```

两层 ban/pick 策略训练命令：

```bash
python3 -m stage1_predictor.train_bandit_policy \
  --veto-actions data/bo3/bo3_stage1_last4months_veto_actions_complete_2026-05-25.csv \
  --major-veto-actions data/bo3/bo3_major_veto_actions_complete_2026-05-25.csv \
  --major-correction-weight 0.50 \
  --output-json reports/models/bo3_two_layer_veto_bandit_policy_2026-05-25.json \
  --report reports/bo3_two_layer_veto_bandit_policy_2026-05-25.md
```

`weighted-finetune-latest` 使用的数据：

```text
data/bo3/bo3_stage1_last4months_catboost_pretrain_complete_2026-05-25.csv
data/bo3/bo3_stage1_last4months_veto_actions_complete_2026-05-25.csv
data/bo3/bo3_major_veto_actions_complete_2026-05-25.csv
data/bo3/bo3_stage1_last4months_map_stats_complete_2026-05-25.csv
```

完整数据量：

```text
近 4 个月 BO3 pretrain rows：1500
近 4 个月 ordered veto actions：2622
两个 Major ordered veto actions：1484
当前 Cologne 16 队 x 7 图 map-stats：112
```

## 严格真实小样本扩展模型

仓库仍保留一版小样本严格真实 HLTV pretrain 表：

```text
data/real_hltv/stage1_last4months_hltv_match_rows.csv
data/real_hltv/stage1_last4months_match_map_features.csv
reports/real_hltv_catboost_pretrain_dataset.md
```

它来自官方 HLTV match pages 的本地 source snippets，覆盖 17 张 map rows，构造成 34 条 bidirectional CatBoost pairwise rows。它适合做“来源更严格但样本更少”的扩展模型，不是当前主模型。

严格真实 pretrain 校验：

```bash
python3 -m stage1_predictor.validate_real_data \
  --pretrain-csv data/real_hltv/stage1_last4months_match_map_features.csv \
  --report reports/real_data_provenance_validation.md
```

旧的命令行 HLTV fetch attempt 仍会记录为 FAIL，因为本机直接请求 HLTV 会返回 403 / Cloudflare challenge；这不会再冒充成功抓取。

严格真实小样本训练：

```bash
python3 -m stage1_predictor.train_catboost_model \
  --require-real-pretrain \
  --pretrain-matches data/real_hltv/stage1_last4months_match_map_features.csv \
  --snapshots data/snapshots/blast_austin_major_2025_stage1_2025-06-02.csv data/snapshots/starladder_budapest_major_2025_stage1_2025-10-06.csv \
  --labels data/labels/blast_austin_2025_stage1_labels.csv data/labels/starladder_budapest_2025_stage1_labels.csv \
  --model-output reports/models/strict_real_stage1_catboost_pairwise.cbm \
  --metadata-json reports/models/strict_real_stage1_catboost_pairwise.json \
  --report reports/strict_real_stage1_catboost_training.md
```

## HLTV 数据抓取与快照

本机直接请求 HLTV 时会遇到 Cloudflare challenge。项目不会假装抓取成功，而是把真实请求状态写入报告，再用已验证的 HLTV 派生缓存保证结果可复现。

```bash
python3 -m stage1_predictor.scrape_hltv_team_metrics \
  --teams data/iem_cologne_2026_stage1_teams.csv \
  --output reports/hltv_scrape_smoke_2026-05-23.csv \
  --raw-dir data/raw/hltv \
  --attempt-json reports/hltv_scrape_attempt_2026-05-23.json \
  --source-report reports/hltv_scrape_sources_2026-05-23.md \
  --fallback-csv data/raw/hltv/iem_cologne_2026_stage1_team_metrics_2026-05-23.csv \
  --strict
```

生成 HLTV team-level 特征快照：

```bash
python3 -m stage1_predictor.build_hltv_feature_snapshot \
  --teams data/iem_cologne_2026_stage1_teams.csv \
  --config data/stage_configs/iem_cologne_2026_stage1.json \
  --hltv-team-stats reports/hltv_scrape_smoke_2026-05-23.csv \
  --prediction-cutoff 2026-05-23 \
  --feature-window-end 2026-05-23 \
  --output data/snapshots/iem_cologne_major_2026_stage1_hltv_features_2026-05-23.csv \
  --strict
```

## 因素综合模型

因素综合模型优先纳入当前能稳定获得、且实际有价值的因素：

- 基础实力：VRS 积分与种子路径。
- 近期状态/火力：HLTV Rating 3.0、K/D、每图 K-D 差。
- 地图池代理：HLTV 地图样本量和样本置信度。
- 对手质量代理：赛区先验，直到 Top 5/10/20/30 对手分层数据可用。
- 阵容数据置信度：区分全队历史统计与当前阵容页代理。

```bash
python3 -m stage1_predictor.factor_snapshot \
  --input data/snapshots/iem_cologne_major_2026_stage1_hltv_features_2026-05-23.csv \
  --output data/snapshots/iem_cologne_major_2026_stage1_factor_scores_2026-05-23.csv \
  --report reports/iem_cologne_2026_stage1_factor_score_model.md \
  --json reports/iem_cologne_2026_stage1_factor_score_model.json
```

## BO1 / BO3 与 ban-pick 模拟

瑞士轮不是简单的单场胜率排序。项目现在支持地图 veto 模拟：

- BO1：双方轮流 ban，直到剩一张图。
- BO3：双方先 ban，再各自 pick，一轮二次 ban 后留下 decider。
- 每张图胜率会结合队伍地图胜率、样本量、pick/ban 倾向和可选经济局/首杀代理。
- 缺少地图数据的队伍会回退到中性地图假设，避免伪造强信号。

运行“因素综合 + veto”正式实验模型：

```bash
python3 -m stage1_predictor.cli \
  --teams data/iem_cologne_2026_stage1_teams.csv \
  --model factor-score \
  --feature-snapshot data/snapshots/iem_cologne_major_2026_stage1_factor_scores_2026-05-23.csv \
  --map-stats data/raw/hltv/iem_cologne_2026_stage1_map_stats_2026-05-23.csv \
  --map-pool Ancient,Anubis,Dust2,Inferno,Mirage,Nuke,Overpass \
  --simulations 50000 \
  --seed 42 \
  --report reports/iem_cologne_2026_stage1_prediction_factor_veto.md \
  --csv reports/iem_cologne_2026_stage1_prediction_factor_veto.csv \
  --json reports/iem_cologne_2026_stage1_prediction_factor_veto.json
```

注意：`--map-pool` 必须在发布前按官方 Cologne Major Stage 1 实际地图池复核。

运行“因素综合 + veto + 历史校准”保守实验模型：

```bash
python3 -m stage1_predictor.train_factor_veto_calibration \
  --snapshots data/snapshots/blast_austin_major_2025_stage1_2025-06-02.csv data/snapshots/starladder_budapest_major_2025_stage1_2025-10-06.csv \
  --labels data/labels/blast_austin_2025_stage1_labels.csv data/labels/starladder_budapest_2025_stage1_labels.csv \
  --output-json reports/stage1_factor_veto_calibration.json \
  --report reports/stage1_factor_veto_calibration.md \
  --simulations 2500

python3 -m stage1_predictor.cli \
  --teams data/iem_cologne_2026_stage1_teams.csv \
  --model factor-score \
  --feature-snapshot data/snapshots/iem_cologne_major_2026_stage1_factor_scores_2026-05-23.csv \
  --map-stats data/raw/hltv/iem_cologne_2026_stage1_map_stats_2026-05-23.csv \
  --calibration-json reports/stage1_factor_veto_calibration.json \
  --simulations 50000 \
  --seed 42 \
  --report reports/iem_cologne_2026_stage1_prediction_factor_veto_calibrated.md \
  --csv reports/iem_cologne_2026_stage1_prediction_factor_veto_calibrated.csv \
  --json reports/iem_cologne_2026_stage1_prediction_factor_veto_calibrated.json
```

这版只微调全局概率校准层：`scale`、`bo1_shrink`、`bo3_shrink`、`veto_weight`。当前历史 map-stats 不完整，所以 `veto_weight` 保持 1.0，主要学习瑞士轮/BO1/BO3 的保守概率尺度。

运行“训练 factor 权重 + veto + 历史校准”的完整实验模型：

```bash
python3 -m stage1_predictor.train_factor_weights \
  --snapshots data/snapshots/blast_austin_major_2025_stage1_2025-06-02.csv data/snapshots/starladder_budapest_major_2025_stage1_2025-10-06.csv \
  --labels data/labels/blast_austin_2025_stage1_labels.csv data/labels/starladder_budapest_2025_stage1_labels.csv \
  --calibration-json reports/stage1_factor_veto_calibration.json \
  --output-json reports/stage1_factor_weights_training.json \
  --report reports/stage1_factor_weights_training.md \
  --simulations 800 \
  --rounds 2

python3 -m stage1_predictor.factor_snapshot \
  --input data/snapshots/iem_cologne_major_2026_stage1_hltv_features_2026-05-23.csv \
  --weights-json reports/stage1_factor_weights_training.json \
  --output data/snapshots/iem_cologne_major_2026_stage1_factor_weights_trained_2026-05-25.csv \
  --report reports/iem_cologne_2026_stage1_factor_weights_trained_model_2026-05-25.md \
  --json reports/iem_cologne_2026_stage1_factor_weights_trained_model_2026-05-25.json

python3 -m stage1_predictor.cli \
  --teams data/iem_cologne_2026_stage1_teams.csv \
  --model factor-score \
  --feature-snapshot data/snapshots/iem_cologne_major_2026_stage1_factor_weights_trained_2026-05-25.csv \
  --map-stats data/raw/hltv/iem_cologne_2026_stage1_map_stats_2026-05-23.csv \
  --calibration-json reports/stage1_factor_veto_calibration.json \
  --simulations 50000 \
  --seed 42 \
  --report reports/iem_cologne_2026_stage1_prediction_factor_weight_veto_calibrated.md \
  --csv reports/iem_cologne_2026_stage1_prediction_factor_weight_veto_calibrated.csv \
  --json reports/iem_cologne_2026_stage1_prediction_factor_weight_veto_calibrated.json
```

训练权重版当前学到：基础实力/VRS `33%`、HLTV rating `15%`、火力/KD `10%`、地图样本深度 `8%`、样本置信度 `8%`、对手质量代理 `14%`、阵容数据可得性 `5%`、种子路径 `7%`。Austin/Budapest 历史快照没有完整 HLTV/KD/map-depth 字段，所以可识别变化主要来自 VRS、对手质量代理和种子路径。

## 雷达图与 notebook

生成中文因素雷达图和每队一张 PNG：

```bash
python3 -m stage1_predictor.radar_chart \
  --snapshot data/snapshots/iem_cologne_major_2026_stage1_vrs_tier_scoreline_features_2026-05-25.csv \
  --output reports/figures/iem_cologne_2026_stage1_vrs_tier_scoreline_radar_2026-05-25.svg \
  --columns 4 \
  --team-png-dir reports/figures/teams \
  --prediction-json reports/iem_cologne_2026_stage1_prediction_vrs-tier-scoreline-map-catboost_2026-05-25.json \
  --model-name vrs-tier-scoreline-map-catboost
```

Notebook：

```text
notebooks/iem_cologne_2026_stage1_factor_radar.ipynb
```

输出图：

```text
reports/figures/iem_cologne_2026_stage1_vrs_tier_scoreline_radar_2026-05-25.svg
reports/figures/teams/*.png
```

每队 PNG 雷达图使用 2026-05-25 V社排名分层 + 比分质量增强快照，并在图内标注当前主模型 `vrs-tier-scoreline-map-catboost` 的晋级概率、3-0 概率、0-3 概率和最常见战绩。

| GamerLegion | BIG | BetBoom | HEROIC |
|---|---|---|---|
| <img src="reports/figures/teams/gamerlegion_radar.png" width="220"> | <img src="reports/figures/teams/big_radar.png" width="220"> | <img src="reports/figures/teams/betboom_radar.png" width="220"> | <img src="reports/figures/teams/heroic_radar.png" width="220"> |
| SINNERS | B8 | MIBR | M80 |
| <img src="reports/figures/teams/sinners_radar.png" width="220"> | <img src="reports/figures/teams/b8_radar.png" width="220"> | <img src="reports/figures/teams/mibr_radar.png" width="220"> | <img src="reports/figures/teams/m80_radar.png" width="220"> |
| TYLOO | Sharks | FlyQuest | NRG |
| <img src="reports/figures/teams/tyloo_radar.png" width="220"> | <img src="reports/figures/teams/sharks_radar.png" width="220"> | <img src="reports/figures/teams/flyquest_radar.png" width="220"> | <img src="reports/figures/teams/nrg_radar.png" width="220"> |
| Gaimin Gladiators | THUNDER dOWNUNDER | Liquid | Lynn Vision |
| <img src="reports/figures/teams/gaimin_gladiators_radar.png" width="220"> | <img src="reports/figures/teams/thunder_downunder_radar.png" width="220"> | <img src="reports/figures/teams/liquid_radar.png" width="220"> | <img src="reports/figures/teams/lynn_vision_radar.png" width="220"> |

## 模型对比

最新推荐对比使用同一份最新 Cologne 输入、同一份完整 ban/pick、同一份两层 bandit、同一份瑞士轮规则和同一份全局校准参数：

```bash
python3 -m stage1_predictor.compare_models \
  --summary vrs-tier-scoreline-map-catboost=reports/iem_cologne_2026_stage1_prediction_vrs-tier-scoreline-map-catboost_2026-05-25.json \
  --summary weighted-finetune-latest=reports/iem_cologne_2026_stage1_prediction_weighted-finetune-latest_latest_rules_2026-05-25.json \
  --summary vrs-latest=reports/iem_cologne_2026_stage1_prediction_vrs-latest_latest_rules_2026-05-25.json \
  --summary hltv-feature-latest=reports/iem_cologne_2026_stage1_prediction_hltv-feature-latest_latest_rules_2026-05-25.json \
  --summary strict-real-catboost-latest=reports/iem_cologne_2026_stage1_prediction_strict-real-catboost-latest_latest_rules_2026-05-25.json \
  --summary bo3-catboost-shallow-latest=reports/iem_cologne_2026_stage1_prediction_bo3-catboost-shallow-latest_latest_rules_2026-05-25.json \
  --report reports/iem_cologne_2026_stage1_all_models_latest_rules_comparison_2026-05-25.md \
  --json reports/iem_cologne_2026_stage1_all_models_latest_rules_comparison_2026-05-25.json
```

当前 README 主模型：

```text
vrs-tier-scoreline-map-catboost: 78.0% 通过，5.38 期望猜中
```

当前同口径完整榜单：

```text
catboost-major-only-latest: 85.4% 通过，5.67 期望猜中
vrs-latest: 81.0% 通过，5.54 期望猜中
hltv-feature-latest: 80.3% 通过，5.48 期望猜中
vrs-tier-scoreline-map-catboost: 78.0% 通过，5.38 期望猜中
strict-real-catboost-latest: 75.8% 通过，5.32 期望猜中
logistic-latest: 72.3% 通过，5.18 期望猜中
weighted-finetune-latest: 62.6% 通过，4.88 期望猜中
factor-score-latest: 61.1% 通过，4.83 期望猜中
factor-weight-latest: 60.5% 通过，4.81 期望猜中
bo3-catboost-shallow-latest: 60.1% 通过，4.80 期望猜中
```

说明：`catboost-major-only-latest` 当前通过率最高，但它主要吃 Austin/Budapest 两个 Major 标签，样本少、过拟合风险高；所以 README 不把它设为主模型。`vrs-tier-scoreline-map-catboost` 继承 weighted-finetune 的训练链路，并加入对手 V社排名分层地图胜率和比分质量，因此现在作为主模型；`weighted-finetune-latest`、`vrs-complete-veto` / `vrs-latest` 作为扩展对照。

## 校准参数公平对照

这组对照让所有模型使用同一份概率校准参数：

```text
reports/stage1_factor_veto_calibration.json
```

其中 `vrs-calibrated`、`hltv-feature-score-calibrated`、`logistic-calibrated`、`factor-score-calibrated` 只使用训练后的 `scale / bo1_shrink / bo3_shrink`；`factor-veto-calibrated` 和 `factor-weight-veto-calibrated` 还额外启用地图 ban/pick。

```bash
python3 -m stage1_predictor.compare_models \
  --summary vrs-calibrated=reports/iem_cologne_2026_stage1_prediction_vrs_calibrated.json \
  --summary hltv-feature-score-calibrated=reports/iem_cologne_2026_stage1_prediction_hltv_feature_score_calibrated.json \
  --summary logistic-calibrated=reports/iem_cologne_2026_stage1_prediction_logistic_calibrated.json \
  --summary factor-score-calibrated=reports/iem_cologne_2026_stage1_prediction_factor_score_calibrated.json \
  --summary factor-veto-calibrated=reports/iem_cologne_2026_stage1_prediction_factor_veto_calibrated.json \
  --summary factor-weight-veto-calibrated=reports/iem_cologne_2026_stage1_prediction_factor_weight_veto_calibrated.json \
  --report reports/iem_cologne_2026_stage1_calibrated_model_comparison.md \
  --json reports/iem_cologne_2026_stage1_calibrated_model_comparison.json
```

当前 calibrated-only 排名：

```text
factor-veto-calibrated: 63.4% 通过，4.93 期望猜中
factor-weight-veto-calibrated: 62.6% 通过，4.90 期望猜中
vrs-calibrated: 62.0% 通过，4.87 期望猜中
hltv-feature-score-calibrated: 60.8% 通过，4.84 期望猜中
logistic-calibrated: 59.4% 通过，4.79 期望猜中
factor-score-calibrated: 54.6% 通过，4.65 期望猜中
```

## 历史训练基线

```bash
python3 -m stage1_predictor.train_stage1_model \
  --snapshots data/snapshots/blast_austin_major_2025_stage1_2025-06-02.csv data/snapshots/starladder_budapest_major_2025_stage1_2025-10-06.csv \
  --labels data/labels/blast_austin_2025_stage1_labels.csv data/labels/starladder_budapest_2025_stage1_labels.csv \
  --output-json reports/stage1_model_training.json \
  --report reports/stage1_model_training.md
```

历史训练目前只有 Austin 2025 Stage 1 和 Budapest 2025 Stage 1 两个新赛制样本，所以它是防泄漏训练管线和校准脚手架，不是稳定生产模型。

## 后续阶段 smoke

Stage 2、Stage 3、Playoffs 目前只有 smoke 引擎。真实预测要等官方队伍、种子、开局对阵、赛制和 bracket 发布。

```bash
python3 -m stage1_predictor.cli \
  --teams data/sample_stage1_teams.csv \
  --stage-name "Stage 3 Smoke" \
  --advance-label "Qualify for Playoffs" \
  --all-bo3 \
  --simulations 1000 \
  --seed 42 \
  --report reports/stage3_all_bo3_smoke.md

python3 -m stage1_predictor.playoffs_cli \
  --teams data/sample_playoff_teams.csv \
  --simulations 1000 \
  --seed 42 \
  --final-best-of 5 \
  --report reports/playoffs_smoke.md \
  --csv reports/playoffs_smoke.csv \
  --json reports/playoffs_smoke.json
```

## 验证

```bash
python3 -m unittest
python3 -m compileall -q stage1_predictor tests
```

## 注意事项

- 这是 Stage 1 Pick'Em 预测工具，不是投注或赔率模型。
- 赔率不作为模型输入。
- HLTV 命令行抓取会遇到 challenge；项目会记录真实抓取尝试，并使用可复现的 HLTV 派生缓存。
- `data/sample_stage1_teams.csv` 是合成样例。
- 瑞士轮配对已按 Valve/majors.im Cologne 口径核对：首轮种子配对、同战绩分组、Buchholz 排序、避免重复交手、4/5 轮 6 队优先表都已实现。任意手工场景可用 `stage1_predictor.inspect_swiss_pairings` 对照。
- Cologne Stage 1 的队伍、种子、开局对阵和地图池必须在发布前按官方信息复核。
