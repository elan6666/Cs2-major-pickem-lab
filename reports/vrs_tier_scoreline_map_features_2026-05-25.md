# VRS Tier Scoreline Map Features

- Matches input: `data/bo3/bo3_stage1_last4months_matches_complete_2026-05-25.csv`
- Maps input: `data/bo3/bo3_stage1_last4months_maps_complete_2026-05-25.csv`
- Team-map output: `data/bo3/bo3_stage1_last4months_vrs_tier_scoreline_map_features_2026-05-25.csv`
- Augmented snapshot: `data/snapshots/iem_cologne_major_2026_stage1_vrs_tier_scoreline_features_2026-05-25.csv`
- Scoreline-adjusted map stats: `data/bo3/bo3_stage1_last4months_vrs_tier_scoreline_map_stats_2026-05-25.csv`
- Team-map rows: `430`
- Teams: `91`
- Maps: `7`
- Directed map observations: `1500`
- Overtime observations: `168`
- Close-loss observations: `173`

## Feature Design

- Cumulative tiers: VRS top 10/20/30/40/50/70/100.
- Diagnostic buckets: VRS 1-10, 11-20, 21-30, 31-40, 41-50, 51-70, 71-100.
- Smoothed win rates use Bayesian shrinkage toward a blend of team-map baseline and global map baseline.
- Scoreline quality is MR12/overtime aware: regulation margins scale strongly, overtime margins stay close to zero.
