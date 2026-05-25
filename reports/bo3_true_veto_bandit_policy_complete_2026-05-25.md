# Contextual Bandit Veto Policy

- 模式：`true_veto_action_bandit`
- exploration: 0.2

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

## 说明

如果输入真实 veto action CSV，这里会学习每个 action/map 的经验奖励；如果没有真实序列，则用地图胜率、pick rate、ban rate 构造 prior，让 veto 不再是纯随机选图。当前策略仍是轻量 contextual bandit prior，不是完整 minimax 博弈树。
