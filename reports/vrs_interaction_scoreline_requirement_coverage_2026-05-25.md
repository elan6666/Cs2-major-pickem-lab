# VRS interaction scoreline coverage audit

- team_map_rows: 430
- snapshot_rows: 16
- pretrain_rows: 1500
- model_feature_count: 70

| 需求 | 特征 | 快照原始列 | 训练差值/边列 | 模型输入 | 结果 |
|---|---|---|---|---|---|
| 比分质量 x 对手V社排名 | `vrs_opponent_adjusted_scoreline_quality` | yes,nz=True,min=-0.162345,max=0.251738 | `vrs_opponent_adjusted_scoreline_quality_diff` yes,nz=True,min=-1.75585,max=1.75585 | True | OK |
| 比分质量 x 对手V社排名 | `vrs_weak_opponent_close_penalty` | yes,nz=True,min=0,max=0.245 | `vrs_weak_opponent_close_penalty_diff` yes,nz=True,min=-0.83,max=0.83 | True | OK |
| 地图胜率 x 对手V社排名 | `vrs_map_win_opponent_quality` | yes,nz=True,min=-11.1853,max=9.39569 | `vrs_map_win_opponent_quality_diff` yes,nz=True,min=-49.1398,max=49.1398 | True | OK |
| 地图胜率 x 对手V社排名 | `vrs_top20_map_smoothed_win_rate` | yes,nz=True,min=30.3443,max=63.6917 | `vrs_top20_map_smoothed_win_rate_diff` yes,nz=True,min=-77.5,max=77.5 | True | OK |
| 地图胜率 x 对手V社排名 | `vrs_top50_map_smoothed_win_rate` | yes,nz=True,min=31.4414,max=63.58 | `vrs_top50_map_smoothed_win_rate_diff` yes,nz=True,min=-81.83,max=81.83 | True | OK |
| 地图胜率 x 对手V社排名 | `vrs_top100_map_smoothed_win_rate` | yes,nz=True,min=32.0986,max=68.59 | `vrs_top100_map_smoothed_win_rate_diff` yes,nz=True,min=-81.83,max=81.83 | True | OK |
| 地图胜率 x 样本量 | `vrs_map_win_sample_confidence` | yes,nz=True,min=-6.9,max=15.3792 | `vrs_map_win_sample_confidence_diff` yes,nz=True,min=-48.6429,max=48.6429 | True | OK |
| 地图胜率 x 样本量 | `vrs_tier_map_sample_log` | yes,nz=True,min=1.02896,max=2.65637 | `vrs_tier_map_sample_log_diff` yes,nz=True,min=-2.30259,max=2.30259 | True | OK |
| 比分质量 x 样本量 | `vrs_scoreline_sample_confidence` | yes,nz=True,min=-0.03449,max=0.208585 | `vrs_scoreline_sample_confidence_diff` yes,nz=True,min=-0.672739,max=0.672739 | True | OK |
| 地图强度 x veto行为 | `vrs_map_veto_credibility` | yes,nz=True,min=0.447735,max=0.669333 | `vrs_map_veto_credibility_diff` yes,nz=True,min=-0.804,max=0.804 | True | OK |
| 地图强度 x veto行为 | `vrs_map_veto_strength` | yes,nz=True,min=45.8265,max=66.3794 | `vrs_map_veto_strength_diff` yes,nz=True,min=-46.7509,max=46.7509 | True | OK |
| pick/ban x 对手地图池 | `vrs_pick_ban_opponent_pool_proxy` | yes,nz=True,min=-0.07203,max=0.295557 | `vrs_pick_ban_opponent_pool_proxy_diff` yes,nz=True,min=-0.845206,max=0.845206 | True | OK |
| pick/ban x 对手地图池 | `vrs_pick_ban_opponent_pool_edge` | pairwise only | `vrs_pick_ban_opponent_pool_edge` yes,nz=True,min=-1.40253,max=1.63628 | True | OK |
| BO1/BO3 x 地图深度 | `vrs_bo1_single_map_upset_risk` | yes,nz=True,min=0,max=0.406397 | `vrs_bo1_single_map_upset_risk_diff` yes,nz=True,min=-0.668571,max=0.668571 | True | OK |
| BO1/BO3 x 地图深度 | `vrs_bo3_map_depth_strength` | yes,nz=True,min=0.023736,max=0.307583 | `vrs_bo3_map_depth_strength_diff` yes,nz=True,min=-0.603077,max=0.603077 | True | OK |
| BO1/BO3 x 地图深度 | `vrs_bo1_bo3_map_depth_edge` | pairwise only | `vrs_bo1_bo3_map_depth_edge` yes,nz=True,min=-0.934285,max=0.934285 | True | OK |
| 加时/惜败 x 对手强度 | `vrs_overtime_strong_opponent_signal` | yes,nz=True,min=0,max=1.07143 | `vrs_overtime_strong_opponent_signal_diff` yes,nz=True,min=-1.5,max=1.5 | True | OK |
| 加时/惜败 x 对手强度 | `vrs_weak_opponent_close_penalty` | yes,nz=True,min=0,max=0.245 | `vrs_weak_opponent_close_penalty_diff` yes,nz=True,min=-0.83,max=0.83 | True | OK |
| 近期时间 x 对手质量 | `vrs_recent_strong_opponent_score` | yes,nz=True,min=-0.093854,max=0.033222 | `vrs_recent_strong_opponent_score_diff` yes,nz=True,min=-0.768764,max=0.768764 | True | OK |
| 种子路径 x 队伍波动 | `vrs_team_volatility` | yes,nz=True,min=2.67439,max=6.23276 | `vrs_team_volatility_diff` yes,nz=True,min=-7.932,max=7.932 | True | OK |
| 种子路径 x 队伍波动 | `vrs_seed_volatility_rebound` | yes,nz=True,min=0,max=3.70292 | `vrs_seed_volatility_rebound_diff` yes,nz=True,min=-12.75,max=12.75 | True | OK |

COVERAGE_OK=True
