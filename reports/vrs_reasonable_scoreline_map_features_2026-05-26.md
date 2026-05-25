# VRS Tier Scoreline Map Features

- Matches input: `data/bo3/bo3_stage1_last4months_matches_complete_2026-05-25.csv`
- Maps input: `data/bo3/bo3_stage1_last4months_maps_complete_2026-05-25.csv`
- Team-map output: `data/bo3/bo3_stage1_last4months_vrs_reasonable_scoreline_map_features_2026-05-26.csv`
- Augmented snapshot: `data/snapshots/iem_cologne_major_2026_stage1_vrs_reasonable_scoreline_features_2026-05-26.csv`
- Scoreline-adjusted map stats: `data/bo3/bo3_stage1_last4months_vrs_reasonable_scoreline_map_stats_2026-05-26.csv`
- Team-map rows: `430`
- Teams: `91`
- Maps: `7`
- Directed map observations: `1500`
- Overtime observations: `168`
- Close-loss observations: `173`
- VRS rank snapshots used: `2026-01-05, 2026-02-02, 2026-03-02, 2026-04-06, 2026-05-04, match_row`

## Feature Design

- Cumulative tiers: VRS top 10/20/30/40/50/70/100.
- Diagnostic buckets: VRS 1-10, 11-20, 21-30, 31-40, 41-50, 51-70, 71-100.
- Smoothed win rates use Bayesian shrinkage toward a blend of team-map baseline and global map baseline.
- Scoreline quality is MR12/overtime aware: regulation margins scale strongly, overtime margins stay close to zero.
- Interaction features combine scoreline quality with opponent VRS rank, map win rate with sample confidence, scoreline quality with sample confidence, map strength with pick/ban credibility, BO1 upset risk with BO3 map depth, close/overtime results with opponent strength, and recency with opponent quality.
- Match-date VRS rank lookup uses the latest available Valve `standings_global_YYYY_MM_DD.md` snapshot at or before each BO3 match date; if none is older than the match, it falls back to the earliest available snapshot.
- Expected-margin residual compares the actual map round margin against the margin implied by the two teams' VRS ranks, so narrow wins over weak opposition can become negative and close losses to strong opposition can become positive.
- The map_veto-compatible win rate uses veto-credible map strength, so a strong map that is rarely picked or often banned is discounted before Swiss BO1/BO3 simulation.
