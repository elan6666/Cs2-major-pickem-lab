# CS2 比赛胜负预测数据维度

本文档用于整理 CS2 赛事胜负预测时可以收集和建模的数据维度，适用于 Major、IEM、BLAST、ESL 等职业赛事。

## 1. 基础比赛信息

- 赛事名称：例如 Austin Major、Budapest Major、Cologne Major。
- 比赛阶段：Stage 1、Stage 2、Stage 3、Playoffs、决赛。
- 赛制：BO1、BO3、BO5。
- 比赛环境：LAN、线上、演播室、竞技场舞台。
- 是否淘汰局：例如瑞士轮 0-2、1-2、2-2 局。
- 是否晋级局：例如瑞士轮 2-0、2-1 局。
- 赛程压力：是否背靠背、是否刚打完 BO3/BO5、休息时间是否充足。

## 2. 队伍基础实力

- 世界排名。
- Valve Regional Standing / VRS 排名。
- HLTV 排名。
- 所属赛区：Europe、Americas、Asia。
- 最近 3 个月整体胜率。
- 最近 6 个月整体胜率。
- 最近 5 场 / 10 场战绩。
- 最近输赢的对手质量。
- 阵容稳定性：是否近期换人、换教练、换 IGL、换 AWPer。

注意：世界排名和 VRS 排名有滞后性，不能单独作为胜负判断依据。

## 3. 对手质量修正

队伍胜率需要结合对手强度分析，避免弱队刷分造成虚高。

可以按对手排名分层统计：

- vs Top 5 胜率。
- vs Top 10 胜率。
- vs Top 15 胜率。
- vs Top 20 胜率。
- vs Top 30 胜率。
- vs Top 50 胜率。
- vs Top 70 胜率。
- vs Top 100 胜率。

同样的地图胜率也应按对手强度分层。例如某队 Ancient 胜率 75%，但主要来自 Top 50 以外的对手，那么面对 Top 10 队伍时需要降权。

## 4. 地图池与 Ban/Pick

CS2 比赛预测必须重点分析地图池，因为比赛地图由 ban/pick 决定。

核心维度：

- 常规 permaban 地图。
- 最常 pick 地图。
- 每张地图总胜率。
- 每张地图最近 3 个月胜率。
- 每张地图最近 6 个月胜率。
- 每张地图 vs Top 15 / Top 20 / Top 30 胜率。
- 地图样本量。
- BO1 中是否容易被针对。
- BO3 中是否有稳定两张强图。
- BO5 中地图池是否足够深。
- Decider 图胜率。
- 是否有新练地图或近期突然启用的地图。

地图胜率需要结合样本量。少于 5 场的地图胜率参考价值较低。

## 5. BO1 / BO3 / BO5 赛制影响

不同赛制下，预测权重不同。

### BO1

- 爆冷概率更高。
- 地图 veto 权重更高。
- 手枪局和经济局权重更高。
- 单图状态波动影响更大。
- 弱队如果能把比赛拖到自己熟悉的地图，就有更高爆冷机会。

### BO3

- 地图池深度更重要。
- 教练和 IGL 调整能力更重要。
- 队伍稳定性比 BO1 更重要。
- 一张图爆冷不一定能赢下整场。

### BO5

- 通常用于决赛。
- 地图池深度非常重要。
- 体力、专注度和抗压能力更重要。
- 强队容错率更高，弱队爆冷难度更大。

## 6. 阵营强度

CS2 地图存在 T side / CT side 偏向，队伍本身也有阵营强弱。

可统计：

- T side round win percentage。
- CT side round win percentage。
- 每张地图的 T side 胜率。
- 每张地图的 CT side 胜率。
- 上半场领先时的地图胜率。
- 上半场落后时的追分能力。
- 选边优势是否明显。
- 是否依赖 CT 开局建立优势。
- T side 进攻是否稳定。

有些队伍 CT 防守很强，但 T side 进攻效率很低。这类队伍在 CT 偏向地图上的胜率可能虚高。

## 7. 经济局能力

CS2 比赛中经济系统会连续影响多个回合，因此经济局能力很关键。

可统计：

- 手枪局胜率。
- 赢手枪后的第二回合转化率。
- 输手枪后的 force buy 胜率。
- Eco / semi-eco 翻盘率。
- Anti-eco 稳定性。
- 被 eco 翻盘率。
- 连续丢分后的止损能力。
- 对手经济被打崩后的收割能力。

强队通常 anti-eco 更稳，弱队爆冷则经常来自 force buy 或沙鹰局打断对手经济。

## 8. 个人能力与角色表现

队伍整体排名之外，还需要看关键选手状态。

可统计：

- 队内 star player rating。
- AWPer rating。
- Entry 成功率。
- Opening kill 差值。
- KAST。
- ADR。
- Impact rating。
- 多杀回合占比。
- Clutch 胜率。
- 1v1、1v2、1v3 胜率。
- 关键局 rating：例如 10-10 后、加时、图三、淘汰局。

角色维度：

- Entry 是否能稳定打开局面。
- Lurker 是否能制造后点压力。
- IGL 是否明显拖累火力。
- Support 道具和补枪是否稳定。
- Anchor 点位是否容易被针对。
- Star player 是否能拿到舒服位置。

## 9. 战术风格与克制关系

CS2 队伍之间存在风格克制，不能只看纸面实力。

常见风格维度：

- 慢控图。
- 快速爆弹。
- 默认控图。
- 激进前压。
- 重道具体系。
- 个人能力驱动。
- 强 CT 前压。
- 保守信息流。
- 喜欢赌点 / 叠点。
- 喜欢中后期转点。

需要观察：

- A 队的强项是否正好克制 B 队弱点。
- B 队是否擅长处理 A 队的默认控图。
- 某队是否容易被快攻打穿。
- 某队是否容易被慢控图消耗道具。
- IGL 是否能在比赛中快速适应对手节奏。

## 10. 韧性、抗压与爆冷能力

你提出的韧性非常关键。它可以用来衡量队伍在不利局面下是否具备爆冷能力。

可统计：

- 落后 0-5 时的地图胜率。
- 落后 2-7 时的地图胜率。
- 落后 5-10 时的地图胜率。
- 先丢手枪后的地图胜率。
- 被对手先拿到 map point 后的翻盘率。
- 加时胜率。
- 图三胜率。
- 淘汰局胜率。
- 晋级局胜率。
- 决赛 / 半决赛表现。
- 关键回合 clutch 能力。
- 连续丢分后的暂停效果。

如果一支队伍经常在落后时追回比分，说明它有较强调整能力和心理韧性，具备更高爆冷潜力。

## 11. 近期状态与趋势

近期状态比长期排名更敏感。

可统计：

- 最近 5 场战绩。
- 最近 10 场战绩。
- 最近 1 个月 rating。
- 最近 3 个月 rating。
- 最近是否连败。
- 输的比赛是否比分接近。
- 赢的比赛是否有统治力。
- 是否刚击败强队。
- 是否只是击败弱队。
- 最近地图池是否变化。
- 近期是否有战术调整。

例如 0-2 输给 Top 3 不一定说明状态差；2-1 险胜 Top 80 也不一定说明状态好。

## 12. 交手历史

Head-to-head 需要谨慎使用。

可统计：

- 双方最近交手结果。
- 相同阵容下的交手结果。
- 相同地图上的交手结果。
- LAN 交手结果。
- 淘汰赛交手结果。
- 最近一次交手距离当前多久。
- 当时地图池是否相同。
- 当时双方阵容是否相同。

如果双方阵容或 IGL 已经变化，历史交手参考价值会下降。

## 13. 外部因素

外部因素在 Major 这类大赛中影响明显。

可统计：

- LAN 经验。
- Major 经验。
- Playoffs 经验。
- 是否主场或接近主场。
- 是否有观众压力。
- 是否跨洲旅行。
- 是否存在时差影响。
- 是否签证或替补问题。
- 队员健康状况。
- 是否刚经历长时间比赛。
- 是否适应当前版本。
- 是否适应当前地图池。

## 14. 数据质量与样本量

数据建模时需要处理样本偏差。

需要注意：

- 地图样本少于 5 场时，胜率参考价值低。
- 新阵容早期数据需要降权。
- 版本更新后的旧数据需要衰减。
- 地图池变动后的旧地图数据需要衰减。
- 只打弱队刷出来的高胜率需要降权。
- 近期数据通常比全年数据更重要。
- LAN 数据和线上数据应分开统计。
- BO1、BO3、BO5 数据应分开统计。

## 15. 简化预测公式

可以先用一个可解释的加权模型：

```text
预测胜率 =
队伍基础实力
+ 地图池优势
+ Ban/Pick 优势
+ 当前状态
+ 对手强度修正
+ LAN / 大赛经验
+ 阵营强度
+ 经济局能力
+ 个人关键位状态
+ 韧性 / 抗压能力
+ 风格克制
- 样本不足惩罚
- 弱队刷分惩罚
- 阵容变动惩罚
```

## 16. 优先级最高的预测维度

如果只先做一个简单版本，建议优先收集：

1. 世界排名 / VRS 排名。
2. 最近 3 个月整体胜率。
3. 地图 ban/pick 倾向。
4. 每张地图最近 3 个月胜率。
5. 每张地图 vs Top 15 / Top 20 / Top 30 胜率。
6. BO1 / BO3 / BO5 类型。
7. T side / CT side 胜率。
8. 手枪局胜率和第二回合转化率。
9. Opening kill 差值。
10. AWPer 和 star player 近期 rating。
11. 图三 / 加时 / 淘汰局表现。
12. 落后追分和翻盘数据。
13. LAN 和 Major 经验。
14. 对手质量修正后的真实胜率。

## 17. Major 新赛制背景

从 BLAST.tv Austin Major 2025 开始，CS2 Major 使用 32 队三阶段瑞士轮结构：

- Stage 1：16 队瑞士轮。
- Stage 2：16 队瑞士轮。
- Stage 3：16 队瑞士轮。
- Playoffs：Stage 3 前 8 进入单败淘汰。

瑞士轮规则：

- 3 胜晋级。
- 3 负淘汰。
- 晋级局和淘汰局为 BO3。
- 其他比赛通常为 BO1。
- 对阵由种子、胜负记录和 Buchholz / Difficulty Score 决定。

使用该新版结构的 Major：

- BLAST.tv Austin Major 2025。
- StarLadder Budapest Major 2025。
- IEM Cologne Major 2026。

Cologne Major 2026 在新版结构上额外升级：Stage 3 全部比赛改为 BO3。

## 18. Stage 1 预测模型建议

Stage 1 的随机性通常高于 Stage 2 和 Stage 3，原因包括：

- 参赛队实力分布更宽。
- 跨赛区队伍更多，数据可比性更弱。
- BO1 比例更高，爆冷概率更高。
- 瑞士轮每一场结果都会影响后续对阵。
- 部分队伍样本少，地图胜率更容易虚高。

因此 Stage 1 不适合只做单场预测，更适合使用：

```text
单场胜率模型 + 瑞士轮蒙特卡洛模拟
```

### 第一层：单场胜率模型

第一版建议使用可解释模型，不急着直接上复杂机器学习。

推荐顺序：

1. Elo / Glicko：用于基础队伍强度。
2. Logistic Regression：用于把排名差、地图优势、近期状态等特征转成胜率。
3. XGBoost / LightGBM：等历史数据足够多后再使用。

第一版可以先用：

```text
P(A 胜 B) = 1 / (1 + exp(-(ScoreA - ScoreB) / scale))
```

Score 可以由以下部分组成：

```text
综合队伍评分 =
基础排名分
+ 近期状态分
+ 地图池分
+ Ban/Pick 优势分
+ 对手质量修正分
+ LAN / Major 经验分
+ 阵营强度分
+ 经济局能力分
+ 韧性 / 抗压分
+ 关键选手状态分
```

### 第二层：瑞士轮模拟

瑞士轮中，某一轮的结果会影响下一轮对阵，所以需要模拟整段 Stage 1。

模拟流程：

```text
1. 输入 16 支 Stage 1 队伍和初始种子。
2. 根据 Valve 规则生成 Round 1 对阵。
3. 对每场比赛计算 A/B 胜率。
4. 按胜率随机抽样比赛结果。
5. 更新每队战绩。
6. 根据瑞士轮规则生成下一轮对阵。
7. 队伍达到 3 胜则晋级，达到 3 负则淘汰。
8. 重复直到 Stage 1 结束。
9. 重复模拟 N 次，统计晋级概率和各路径概率。
```

建议模拟次数：

- 100 次：太少，只能做演示。
- 10,000 次：可以作为初版。
- 50,000 次：较稳定。
- 100,000 次：适合最终预测输出。

输出结果：

- 每队 3-0 概率。
- 每队 3-1 概率。
- 每队 3-2 概率。
- 每队晋级概率。
- 每队 2-3 概率。
- 每队 1-3 概率。
- 每队 0-3 概率。
- 最可能晋级 8 队。
- 最可能淘汰 8 队。
- 强队翻车概率。
- 弱队爆冷晋级概率。

### BO1 随机性处理

BO1 不应该和 BO3 用同样的胜率。

可以把 BO1 胜率向 50% 收缩：

```text
BO1_P = 0.5 + (Raw_P - 0.5) * 0.70
BO3_P = 0.5 + (Raw_P - 0.5) * 1.00
BO5_P = 0.5 + (Raw_P - 0.5) * 1.05
```

示例：

```text
Raw_P = 70%
BO1_P = 64%
BO3_P = 70%
BO5_P = 71%
```

这样可以体现 BO1 更容易爆冷，BO3/BO5 更接近真实实力。

## 19. 数据获取方案

主要数据源可以使用 HLTV，辅以 Valve 规则、VRS、Liquipedia 或赛事官网。

HLTV 没有稳定公开 API，网页结构也可能变化。抓取时需要缓存、限速，并保留原始页面或原始 JSON/HTML，避免重复请求和后续无法复现。

### 需要抓取的数据类型

#### 赛事与瑞士轮结果

用于回测和训练瑞士轮模拟器。

需要字段：

- event_id。
- event_name。
- stage_name。
- start_date。
- end_date。
- team_id。
- team_name。
- seed。
- final_record：例如 3-0、3-1、3-2、2-3、1-3、0-3。
- round_number。
- match_id。
- opponent_id。
- opponent_name。
- map_name。
- map_score。
- bo_type：BO1、BO3、BO5。
- match_result。

示例：Austin Major Stage 1 的 HLTV event id 是 `8436`。

页面：

```text
https://www.hltv.org/events/8436/blasttv-austin-major-2025-stage-1
```

这个页面可以拿到 Stage 1 的 16 队、最终瑞士轮战绩、每队路径、每轮对手和 BO 类型。

#### 赛前队伍状态

预测某个 Major 时，不能用 Major 之后的数据。要按赛前时间窗口截取。

例如预测 Austin Major Stage 1：

```text
Stage 1 开始：2025-06-03
建议数据窗口：2025-03-03 至 2025-06-02
```

可以额外做多个窗口：

- 最近 30 天。
- 最近 60 天。
- 最近 90 天。
- 最近 180 天。

这样能比较短期状态和长期实力。

#### 队伍整体数据

HLTV Stats Teams 页面可按日期、排名过滤、地图过滤。

页面：

```text
https://www.hltv.org/stats/teams?csVersion=CS2
```

建议抓取：

- maps。
- K-D Diff。
- K/D。
- rating。
- round win rate。
- team_id。
- team_name。
- date window。
- ranking filter。
- map filter。

HLTV 支持的常见 ranking filter：

- All。
- Top 5。
- Top 10。
- Top 20。
- Top 30。
- Top 50。

注意：HLTV 的 ranking filter 需要实际验证其含义。建模时更稳妥的方式是抓完整 match/map 明细，然后用比赛当天或赛前最近排名自己计算对手强度分层。

#### 地图数据

每支队伍每张地图需要单独统计。

建议字段：

- team_id。
- map_name。
- date_window。
- matches_played。
- win_rate。
- CT round win rate。
- T round win rate。
- pistol round win rate。
- opening kill diff。
- rating。
- vs Top 5 win rate。
- vs Top 10 win rate。
- vs Top 15 win rate。
- vs Top 20 win rate。
- vs Top 30 win rate。
- vs Top 50 win rate。
- sample_size。

HLTV 默认没有 Top 15、Top 70、Top 100 这种全部分层。Top 15 / 70 / 100 可以自己做：

```text
1. 抓取每张地图的比赛明细。
2. 给每场比赛补上对手当时排名。
3. 按对手排名分桶。
4. 自己聚合地图胜率。
```

#### Match / Map 明细

HLTV Stats Matches 页面适合抓地图级比赛明细。

页面：

```text
https://www.hltv.org/stats/matches/
```

建议字段：

- match_id。
- date。
- team1_id。
- team1_name。
- team2_id。
- team2_name。
- map_name。
- team1_score。
- team2_score。
- event_name。
- event_type：Major、Big event、LAN、Online。
- match_page_url。

这层数据最重要，因为它能自己反推出：

- 地图胜率。
- 对手质量修正胜率。
- LAN / Online 分离。
- Major / Big event 分离。
- BO1 / BO3 / BO5 分离。
- 近期状态。
- 地图样本量。

#### Ban/Pick 数据

Ban/Pick 是最难的一层，因为 HLTV 不是所有列表页都直接结构化展示，需要进入具体 match 页面或从 match 页面文本中解析 veto。

建议字段：

- match_id。
- team_a。
- team_b。
- veto_order。
- ban_1。
- ban_2。
- pick_1。
- pick_2。
- decider。
- starting_side_map1。
- starting_side_map2。
- starting_side_map3。
- bo_type。

可以衍生：

- permaban 地图。
- first ban 频率。
- first pick 频率。
- decider 频率。
- 对某队时的特殊 ban/pick 变化。

第一版如果 ban/pick 抓取困难，可以先用“历史地图出场率 + 常 ban 地图 + 地图胜率”近似。

#### 队员状态

从 HLTV player stats / team stats 抓取，按赛前窗口统计。

建议字段：

- player_id。
- player_name。
- team_id。
- rating。
- impact。
- ADR。
- KAST。
- opening kills。
- opening deaths。
- AWP kills。
- clutch wins。
- maps played。
- date_window。
- LAN only。
- vs Top 20。

重点关注：

- AWPer。
- Star player。
- Entry。
- Anchor。
- IGL 是否火力明显偏低。

### 历史回测数据集

第一批建议只做新版 32 队 Major：

1. BLAST.tv Austin Major 2025 Stage 1。
2. StarLadder Budapest Major 2025 Stage 1。
3. IEM Cologne Major 2026 Stage 1。

如果 Cologne 尚未结束，就先用于赛前预测，不用于训练回测。

每个 Stage 1 都构建一个样本：

```text
event_stage = Austin Major 2025 Stage 1
prediction_cutoff = 2025-06-02
feature_window_90d = 2025-03-03 至 2025-06-02
teams = 16
actual_results = Stage 1 真实瑞士轮结果
```

回测目标：

- 模型预测晋级概率是否接近真实结果。
- 真实晋级队是否集中在高概率区。
- 0-3 / 3-0 预测是否有效。
- 爆冷队伍是否被模型低估。
- BO1 收缩系数是否需要调整。

### 推荐数据表结构

第一版可以用 CSV 或 SQLite。

核心表：

```text
events
event_stages
teams
team_rankings
matches
maps
map_vetoes
team_map_stats_snapshot
team_form_snapshot
player_stats_snapshot
stage_simulation_results
```

最重要的是 snapshot 表。预测 Austin Major 时，snapshot 必须只包含 Austin 开赛前的数据，不能泄漏未来信息。

### 数据获取优先级

第一阶段先抓：

1. Austin Major Stage 1 真实结果。
2. Austin Major Stage 1 参赛队和种子。
3. 每队赛前 90 天整体战绩。
4. 每队赛前 90 天地图胜率。
5. 每队赛前 90 天 vs Top 20 / Top 30 / Top 50 胜率。
6. HLTV / VRS 赛前排名。

第二阶段再补：

1. Ban/Pick 明细。
2. T / CT 阵营胜率。
3. 手枪局和经济局。
4. 选手 rating 和角色数据。
5. 落后翻盘、加时、图三等韧性数据。

这样能先做出可运行的 Stage 1 蒙特卡洛模型，再逐步增加复杂特征。
