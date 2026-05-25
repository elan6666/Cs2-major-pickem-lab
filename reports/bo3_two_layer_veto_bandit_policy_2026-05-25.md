# Contextual Bandit Veto Policy

- 模式：`two_layer_recent_bo3_with_major_correction`
- exploration: 0.2
- Major 修正权重：0.5
- 近 4 个月动作行数：2622
- Major 动作行数：1484

## Map Rewards

| 地图 | reward prior |
|---|---:|
| Ancient | +0.461 |
| Anubis | +0.527 |
| Dust2 | +0.520 |
| Inferno | +0.483 |
| Mirage | +0.492 |
| Nuke | +0.460 |
| Overpass | +0.499 |

## Major 修正

| 地图 | Major 修正 |
|---|---:|
| Ancient | +0.051 |
| Anubis | +0.054 |
| Dust2 | -0.091 |
| Inferno | +0.039 |
| Mirage | -0.034 |
| Nuke | +0.014 |
| Overpass | +0.039 |
| Train | +0.014 |

## 说明

如果同时输入近 4 个月真实 veto action CSV 和 Major veto action CSV，策略会先用近 4 个月 BO3 学基础地图倾向，再用 Major 数据生成额外修正；如果只输入一份真实序列，则学习单层 action/map 经验奖励。当前策略仍是轻量上下文选择策略，不是完整博弈树。
