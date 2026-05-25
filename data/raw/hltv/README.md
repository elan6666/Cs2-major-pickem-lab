# HLTV Raw Data Cache

This folder stores raw or lightly extracted HLTV source data used by the local model.

Local command-line fetching from this environment currently hits a Cloudflare challenge, so the first real-data snapshot uses values extracted from rendered HLTV pages:

- `https://www.hltv.org/stats/teams?csVersion=CS2`
- `https://www.hltv.org/team/13486/thunder-downunder`
- `https://www.hltv.org/team/12774/flyquest`

For a stricter rerun, save the rendered HLTV stats/team pages into this folder and run `stage1_predictor.build_hltv_feature_snapshot` against those files.
