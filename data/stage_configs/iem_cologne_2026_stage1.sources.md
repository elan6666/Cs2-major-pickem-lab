# IEM Cologne Major 2026 Stage 1 Sources

Generated data uses two source types:

- Stage 1 team list and opening pairings: public HLTV, EGamersWorld, and other public listings, accessed 2026-05-22.
- Team score input: official Valve Regional Standings global snapshot from 2026-04-06, stored in ValveSoftware/counter-strike_regional_standings.

Useful source URLs:

- https://www.hltv.org/events/9028/iem-cologne-major-2026-stage-1
- https://www.hltv.org/major/cologne
- https://egamersworld.com/counterstrike/event/iem-cologne-major-2026-stage-1-Vk0fTk8-me
- https://github.com/ValveSoftware/counter-strike_regional_standings/tree/main/invitation/2026

The local builder reads the official VRS snapshot through the GitHub Contents API:

```text
https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/invitation/2026/standings_global_2026_04_06.md
```

Current encoded opening pairings:

```text
GamerLegion vs NRG
B8 vs TYLOO
HEROIC vs Sharks
BetBoom vs Gaimin Gladiators
BIG vs Liquid
M80 vs Lynn Vision
MIBR vs THUNDER dOWNUNDER
SINNERS vs FlyQuest
```

Known limitation:

HLTV direct HTML scraping is blocked by Cloudflare in this environment, so this repo does not claim to have an automated HLTV scraper. The Stage 1 team list is encoded in `iem_cologne_2026_stage1.json` and VRS points are fetched programmatically from Valve's GitHub repository.
