# 瑞士轮规则与 majors.im 对齐检查

## 来源

- Valve Major Supplemental Rulebook：`https://github.com/ValveSoftware/counter-strike_rules_and_regs/blob/main/major-supplemental-rulebook.md`
- majors.im Cologne 页面：`https://majors.im/2026/cologne`
- majors.im 前端 sourcemap：
  - `https://majors.im/static/js/895.d5062342.chunk.js.map`
  - `https://majors.im/static/js/189.5ed011ee.chunk.js.map`

## 已核对规则

- Stage 1 是 16 队瑞士轮，3 胜晋级、3 负淘汰。
- 晋级局和淘汰局是 BO3，其余是 BO1。
- 同一阶段尽量避免重复交手。
- 首轮配对是 1-9、2-10、3-11、4-12、5-13、6-14、7-15、8-16。
- 第 2/3 轮按同战绩组内高种子对可用低种子。
- 第 4/5 轮的 6 队组使用 15 行优先表，选择第一行不会产生重复交手的配对。
- majors.im Cologne 初始数据使用 2026-05-04 Valve global standings 的 Stage 内种子顺序。

## 本地改动

- `data/stage_configs/iem_cologne_2026_stage1.json` 已切到 2026-05-04 VRS 缓存，并保留 2026-05-23 作为当前特征截止日。
- `stage1_predictor/swiss.py` 的非 6 队组递归配对已对齐 majors.im：
  - 前 3 轮取第一个合法高低配。
  - 后 2 轮取差距分最高的合法高低配。
  - 6 队组继续使用 Valve/majors.im 的 15 行优先表。
- 新增 `stage1_predictor.inspect_swiss_pairings`，可用 locked-results CSV 复现任意 majors.im 手工模拟场景的下一轮配对。

## 已跑验证

### 初始配对

报告：`reports/swiss_pairing_check_initial_2026-05-25.md`

结果：

- GamerLegion vs NRG
- B8 vs TYLOO
- HEROIC vs Sharks
- BetBoom vs Gaimin Gladiators
- BIG vs Liquid
- M80 vs Lynn Vision
- MIBR vs THUNDER dOWNUNDER
- SINNERS vs FlyQuest

这与 Valve 首轮 1-9 到 8-16 规则，以及 majors.im Cologne 初始数据一致。

### Round 4 六队组样例

输入：`data/validation/majors_im_cologne_round4_six_team_sample.csv`

报告：`reports/swiss_pairing_check_round4_six_team_sample_2026-05-25.md`

2-1 组排序后是 HEROIC、BetBoom、BIG、M80、MIBR、SINNERS。按 6 队组优先表第一行 1-6、2-5、3-4，且没有重复交手，所以本地输出：

- HEROIC vs SINNERS
- BetBoom vs MIBR
- BIG vs M80

1-2 组同理输出：

- NRG vs Lynn Vision
- TYLOO vs Liquid
- Sharks vs Gaimin Gladiators

## 剩余检查口径

如果要核对你在 majors.im 上点出来的某个具体场景，把那一串已选胜负转成 CSV：

```csv
round,winner,loser,best_of
1,GamerLegion,NRG,1
...
```

然后运行：

```bash
python3 -m stage1_predictor.inspect_swiss_pairings \
  --teams data/iem_cologne_2026_stage1_teams.csv \
  --locked-results path/to/your_scenario.csv \
  --report reports/your_scenario_pairing_check.md \
  --json reports/your_scenario_pairing_check.json
```

即可把本地下一轮配对和 majors.im 页面结果逐项对照。
