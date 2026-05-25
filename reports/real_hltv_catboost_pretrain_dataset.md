# HLTV CatBoost Pretrain Dataset

- Input: `data/real_hltv/stage1_last4months_hltv_match_rows.csv`
- Output: `data/real_hltv/stage1_last4months_match_map_features.csv`
- Featureized rows: 34
- Teams with rows: B8, BIG, BetBoom, GamerLegion, HEROIC, Liquid, M80, SINNERS

## Sources

- `https://www.hltv.org/matches/2393415/big-vs-heroic-cct-global-finals-2026`
- `https://www.hltv.org/matches/2394109/match`
- `https://www.hltv.org/matches/2394113/match`
- `https://www.hltv.org/matches/2394164/liquid-vs-m80-iem-atlanta-2026`

## Notes

Rows were extracted from official HLTV team match pages opened through the web tool and cached as local source snippets. Only rows where both teams are in the Stage 1 snapshot are converted into CatBoost pairwise examples.
