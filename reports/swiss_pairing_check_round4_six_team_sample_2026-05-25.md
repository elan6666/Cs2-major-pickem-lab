# 瑞士轮配对检查

- teams: `data/iem_cologne_2026_stage1_teams.csv`
- locked_results: `data/validation/majors_im_cologne_round4_six_team_sample.csv`
- 已锁定赛果数：24
- 下一轮：Round 4

## 同战绩分组

### 2-1

| 队伍 | 种子 | Buchholz | 已交手 |
|---|---:|---:|---|
| HEROIC | 3 | 3 | B8, M80, Sharks |
| BetBoom | 4 | 3 | BIG, Gaimin Gladiators, GamerLegion |
| BIG | 5 | -1 | BetBoom, Gaimin Gladiators, Liquid |
| M80 | 6 | -1 | HEROIC, Lynn Vision, Sharks |
| MIBR | 7 | -1 | B8, THUNDER dOWNUNDER, TYLOO |
| SINNERS | 8 | -1 | FlyQuest, GamerLegion, NRG |

### 1-2

| 队伍 | 种子 | Buchholz | 已交手 |
|---|---:|---:|---|
| NRG | 9 | 1 | FlyQuest, GamerLegion, SINNERS |
| TYLOO | 10 | 1 | B8, MIBR, THUNDER dOWNUNDER |
| Sharks | 11 | 1 | HEROIC, Lynn Vision, M80 |
| Gaimin Gladiators | 12 | 1 | BIG, BetBoom, Liquid |
| Liquid | 13 | -3 | BIG, FlyQuest, Gaimin Gladiators |
| Lynn Vision | 14 | -3 | M80, Sharks, THUNDER dOWNUNDER |

## 下一轮配对

| 战绩组 | 队伍 A | 队伍 B |
|---|---|---|
| 2-1 | HEROIC #3 B3 | SINNERS #8 B-1 |
| 2-1 | BetBoom #4 B3 | MIBR #7 B-1 |
| 2-1 | BIG #5 B-1 | M80 #6 B-1 |
| 1-2 | NRG #9 B1 | Lynn Vision #14 B-3 |
| 1-2 | TYLOO #10 B1 | Liquid #13 B-3 |
| 1-2 | Sharks #11 B1 | Gaimin Gladiators #12 B1 |

## 规则口径

- 首轮按 1-9、2-10、...、8-16 配对。
- 后续每轮先按同战绩分组，再按 Buchholz 分数降序、种子升序排序。
- 第 4/5 轮的 6 队组使用 Valve/majors.im 的 15 行优先配对表，并避免重复交手。
- 非 6 队组在前 3 轮取第一个合法高低配；后 2 轮取差距分最高的合法高低配。
