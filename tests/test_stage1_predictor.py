from __future__ import annotations

import json
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from stage1_predictor.calibration import load_calibration_params
from stage1_predictor.bandit_veto import BanditPolicy, action_value, train_bandit_policy_from_csv, train_two_layer_bandit_policy_from_csv
from stage1_predictor.catboost_model import FEATURES, NUMERIC_FEATURES, PairwiseExample, build_pair_features, load_pretrain_examples, resolve_model_path
from stage1_predictor.data_provenance import validate_fetch_attempt_report, validate_pretrain_csv, validate_source_csv
from stage1_predictor.evaluate_prediction_metrics import evaluate_history
from stage1_predictor.io import validate_teams
from stage1_predictor.labels import validate_label_rows
from stage1_predictor.map_veto import best_of_three_probability, load_map_stats, simulate_bo1_veto, simulate_bo3_veto, veto_adjusted_win_probability
from stage1_predictor.model_registry import apply_team_model
from stage1_predictor.build_hltv_feature_snapshot import build_hltv_feature_snapshot
from stage1_predictor.build_catboost_pretrain_from_hltv_matches import build_pretrain_rows
from stage1_predictor.collect_bo3_dataset import flatten_veto_actions, render_veto_sequence
from stage1_predictor.factor_snapshot import build_factor_rows, load_factor_weights
from stage1_predictor.hltv_data import (
    is_cloudflare_challenge,
    parse_hltv_team_overview_current_roster,
    parse_hltv_team_stats,
)
from stage1_predictor.models import SimulationOutcome, Team, TeamState
from stage1_predictor.pickem import PickemConfig, evaluate_card, recommend_pickem_card, summarize_probabilities
from stage1_predictor.playoffs import run_playoff_simulations, summarize_playoff_probabilities
from stage1_predictor.rating_system import initial_rating_from_row, rating_features
from stage1_predictor.swiss import SimulationConfig, adjusted_win_probability, enumerate_possible_first_round, pair_six_team_group_by_valve_priority, run_simulations
from stage1_predictor.snapshots import validate_snapshot_row
from stage1_predictor.train_factor_veto_calibration import CalibrationCandidate, build_candidates
from stage1_predictor.train_catboost_model import scale_examples
from stage1_predictor.train_factor_weights import candidate_neighbors, factor_score
from stage1_predictor.trained_model import logit, validate_snapshot_matches_teams
from stage1_predictor.vrs import build_teams_from_stage_config, parse_vrs_markdown


def sample_teams() -> list[Team]:
    return [Team(seed=index + 1, name=f"Team {index + 1}", score=1800 - index * 20) for index in range(16)]


def sample_playoff_teams() -> list[Team]:
    return [Team(seed=index + 1, name=f"Team {index + 1}", score=1900 - index * 35) for index in range(8)]


class Stage1PredictorTests(unittest.TestCase):
    def test_validate_teams_requires_16_teams(self) -> None:
        with self.assertRaises(ValueError):
            validate_teams(sample_teams()[:15])

    def test_first_round_pairings_are_seed_based(self) -> None:
        pairings = enumerate_possible_first_round(sample_teams())
        self.assertEqual(pairings[0], ("Team 1", "Team 9"))
        self.assertEqual(pairings[-1], ("Team 8", "Team 16"))

    def test_six_team_group_uses_valve_priority_table(self) -> None:
        group = [TeamState(team=Team(seed=index + 1, name=f"Team {index + 1}", score=1500)) for index in range(6)]
        pairings = pair_six_team_group_by_valve_priority(group)
        self.assertIsNotNone(pairings)
        self.assertEqual([(left.team.name, right.team.name) for left, right in pairings or []], [("Team 1", "Team 6"), ("Team 2", "Team 5"), ("Team 3", "Team 4")])

        group[0].opponents.add("Team 6")
        pairings = pair_six_team_group_by_valve_priority(group)
        self.assertIsNotNone(pairings)
        self.assertEqual([(left.team.name, right.team.name) for left, right in pairings or []], [("Team 1", "Team 5"), ("Team 2", "Team 6"), ("Team 3", "Team 4")])

    def test_simulation_advances_exactly_8_teams(self) -> None:
        outcomes = run_simulations(sample_teams(), 50, 7, SimulationConfig())
        self.assertEqual(len(outcomes), 50)
        for outcome in outcomes:
            self.assertEqual(len(outcome.advanced), 8)
            eliminated = [record for record in outcome.records.values() if record[1] == 3]
            self.assertEqual(len(eliminated), 8)

    def test_simulation_is_reproducible_with_seed(self) -> None:
        first = run_simulations(sample_teams(), 20, 99, SimulationConfig())
        second = run_simulations(sample_teams(), 20, 99, SimulationConfig())
        self.assertEqual(first, second)

    def test_probability_summary_contains_all_records(self) -> None:
        outcomes = run_simulations(sample_teams(), 100, 3, SimulationConfig())
        probabilities = summarize_probabilities(sample_teams(), outcomes)
        self.assertEqual(len(probabilities), 16)
        for item in probabilities:
            self.assertEqual(set(item.record_probabilities), {"3-0", "3-1", "3-2", "2-3", "1-3", "0-3"})

    def test_pickem_card_evaluation(self) -> None:
        outcomes = [
            SimulationOutcome(
                records={},
                advanced=frozenset({"A", "B", "C", "D", "E", "F", "G", "H"}),
                three_zero=frozenset({"A"}),
                zero_three=frozenset({"P"}),
            ),
            SimulationOutcome(
                records={},
                advanced=frozenset({"B", "C", "D", "E", "F", "G", "H", "I"}),
                three_zero=frozenset({"B"}),
                zero_three=frozenset({"Q"}),
            ),
        ]
        card = evaluate_card(
            outcomes,
            three_zero=("A",),
            zero_three=("P",),
            advance=("B", "C", "D", "E", "F", "G"),
            pass_threshold=5,
        )
        self.assertEqual(card.pass_probability, 1.0)
        self.assertEqual(card.expected_correct, 7.0)

    def test_default_pickem_recommendation_uses_two_two_six_card(self) -> None:
        outcomes = run_simulations(sample_teams(), 100, 13, SimulationConfig())
        probabilities = summarize_probabilities(sample_teams(), outcomes)
        card = recommend_pickem_card(probabilities, outcomes, PickemConfig())
        self.assertEqual(len(card.three_zero), 2)
        self.assertEqual(len(card.zero_three), 2)
        self.assertEqual(len(card.advance), 6)
        self.assertFalse(set(card.three_zero) & set(card.zero_three))
        self.assertFalse((set(card.three_zero) | set(card.zero_three)) & set(card.advance))

    def test_vrs_parser_keeps_best_duplicate_team_rank(self) -> None:
        markdown = """
| Standing | Points | Team Name | Roster | |
| 18 | 1526 | BIG | blameF, faveN | details |
| 202 | 745 | BIG | academy-style duplicate | details |
"""
        entries = parse_vrs_markdown(markdown)
        self.assertEqual(entries["BIG"].rank, 18)
        self.assertEqual(entries["BIG"].points, 1526)

    def test_vrs_stage_config_can_auto_assign_seeds_by_rank(self) -> None:
        markdown_lines = ["| Standing | Points | Team Name | Roster | |"]
        for rank in range(1, 17):
            markdown_lines.append(f"| {rank} | {2000 - rank} | Team {rank} | roster | details |")

        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "vrs.md"
            cache_path.write_text("\n".join(markdown_lines), encoding="utf-8")
            config = {
                "event_id": "event",
                "prediction_cutoff": "2026-01-01",
                "vrs_cache_path": str(cache_path),
                "teams": [{"team": f"Team {rank}"} for rank in range(16, 0, -1)],
            }
            teams = build_teams_from_stage_config(config)

        self.assertEqual([team.name for team in teams[:2]], ["Team 1", "Team 2"])
        self.assertEqual([team.seed for team in teams], list(range(1, 17)))

    def test_snapshot_row_rejects_feature_date_after_cutoff(self) -> None:
        row = {
            "event_id": "event",
            "stage_id": "stage1",
            "team": "Team",
            "prediction_cutoff": "2026-04-06",
            "feature_window_start": "2026-04-01",
            "feature_window_end": "2026-04-07",
            "feature_date": "2026-04-07",
            "sample_weight": "1.0",
        }
        errors = validate_snapshot_row(row, 2)
        self.assertTrue(any("feature_window_end" in error for error in errors))
        self.assertTrue(any("feature_date" in error for error in errors))

    def test_label_rows_reject_inconsistent_record_flags(self) -> None:
        rows = []
        records = ["3-0", "3-0", "3-1", "3-1", "3-1", "3-2", "3-2", "3-2", "2-3", "2-3", "2-3", "1-3", "1-3", "1-3", "0-3", "0-3"]
        for index, record in enumerate(records):
            rows.append(
                {
                    "event_id": "event",
                    "stage_id": "stage1",
                    "team": f"Team {index + 1}",
                    "final_record": record,
                    "advanced": "true" if index == 15 else str(record.startswith("3")).lower(),
                    "went_3_0": str(record == "3-0").lower(),
                    "went_0_3": str(record == "0-3").lower(),
                    "source": "test",
                }
            )

        errors = validate_label_rows(rows)
        self.assertTrue(any("advanced does not match" in error for error in errors))

    def test_logit_round_trip_midpoint(self) -> None:
        self.assertAlmostEqual(logit(0.5), 0.0)

    def test_model_snapshot_team_match_validation(self) -> None:
        rows = [{"team": f"Team {index + 1}"} for index in range(15)]
        with self.assertRaises(ValueError):
            validate_snapshot_matches_teams(sample_teams(), rows)

    def test_feature_score_model_uses_selected_score_column(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            snapshot = Path(temp_dir) / "features.csv"
            lines = ["team,feature_score"]
            for team in sample_teams():
                lines.append(f"{team.name},{2000 - team.seed}")
            snapshot.write_text("\n".join(lines), encoding="utf-8")
            teams = apply_team_model(
                sample_teams(),
                model="feature-score",
                scale=120,
                feature_snapshot=str(snapshot),
                score_column="feature_score",
            )
        self.assertEqual(teams[0].score, 1999)
        self.assertIn("model=feature-score", teams[0].notes)

    def test_factor_score_model_defaults_to_factor_score_column(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            snapshot = Path(temp_dir) / "factors.csv"
            lines = ["team,factor_score,feature_score"]
            for team in sample_teams():
                lines.append(f"{team.name},{2100 - team.seed},100")
            snapshot.write_text("\n".join(lines), encoding="utf-8")
            teams = apply_team_model(
                sample_teams(),
                model="factor-score",
                scale=120,
                feature_snapshot=str(snapshot),
            )
        self.assertEqual(teams[0].score, 2099)
        self.assertIn("model=factor-score", teams[0].notes)

    def test_planned_models_fail_clearly(self) -> None:
        with self.assertRaises(NotImplementedError):
            apply_team_model(sample_teams(), model="xgboost", scale=120)

    def test_catboost_model_requires_feature_snapshot_and_model_json(self) -> None:
        with self.assertRaises(ValueError):
            apply_team_model(sample_teams(), model="catboost", scale=120)

    def test_map_veto_bo1_adjusts_probability(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "maps.csv"
            path.write_text(
                "\n".join(
                    [
                        "team,map,maps_played,win_rate,pick_rate,ban_rate",
                        "Team 1,Ancient,10,80,30,0",
                        "Team 1,Nuke,10,20,0,40",
                        "Team 2,Ancient,10,30,0,35",
                        "Team 2,Nuke,10,75,30,0",
                        "Team 2,Inferno,10,40,5,10",
                    ]
                ),
                encoding="utf-8",
            )
            stats = load_map_stats(path)
        selected = simulate_bo1_veto("Team 1", "Team 2", ("Ancient", "Nuke", "Inferno"), stats)
        self.assertIn(selected, {"Ancient", "Nuke", "Inferno"})
        probability = veto_adjusted_win_probability(sample_teams()[0], sample_teams()[1], 1, 0.5, ("Ancient", "Nuke", "Inferno"), stats)
        self.assertNotEqual(probability, 0.5)

    def test_veto_weight_can_disable_map_adjustment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "maps.csv"
            path.write_text(
                "\n".join(
                    [
                        "team,map,maps_played,win_rate,pick_rate,ban_rate",
                        "Team 1,Ancient,10,90,30,0",
                        "Team 2,Ancient,10,10,0,30",
                        "Team 1,Nuke,10,90,30,0",
                        "Team 2,Nuke,10,10,0,30",
                        "Team 1,Inferno,10,90,30,0",
                        "Team 2,Inferno,10,10,0,30",
                    ]
                ),
                encoding="utf-8",
            )
            stats = load_map_stats(path)
        teams = sample_teams()
        without_veto = adjusted_win_probability(teams[0], teams[1], 1, SimulationConfig(map_pool=("Ancient", "Nuke", "Inferno"), map_stats=stats, veto_weight=0.0))
        with_veto = adjusted_win_probability(teams[0], teams[1], 1, SimulationConfig(map_pool=("Ancient", "Nuke", "Inferno"), map_stats=stats, veto_weight=1.0))
        baseline = adjusted_win_probability(teams[0], teams[1], 1, SimulationConfig())
        self.assertAlmostEqual(without_veto, baseline)
        self.assertGreater(with_veto, without_veto)

    def test_bandit_policy_can_train_from_true_veto_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "veto.csv"
            output = Path(temp_dir) / "policy.json"
            path.write_text(
                "\n".join(
                    [
                        "team,opponent,action,map,reward",
                        "Team 1,Team 2,pick,Ancient,1",
                        "Team 1,Team 2,ban,Nuke,0",
                    ]
                ),
                encoding="utf-8",
            )
            payload = train_bandit_policy_from_csv(path, output)
            self.assertTrue(output.exists())
        self.assertEqual(payload["map_rewards"]["Ancient"], 1.0)

    def test_two_layer_bandit_policy_adds_major_corrections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            recent = root / "recent.csv"
            major = root / "major.csv"
            output = root / "policy.json"
            recent.write_text(
                "\n".join(
                    [
                        "team,opponent,action,map,reward",
                        "Team 1,Team 2,pick,Ancient,0.2",
                        "Team 1,Team 2,ban,Nuke,0.4",
                    ]
                ),
                encoding="utf-8",
            )
            major.write_text(
                "\n".join(
                    [
                        "team,opponent,action,map,reward",
                        "Team 1,Team 2,pick,Ancient,0.8",
                        "Team 1,Team 2,ban,Nuke,0.1",
                    ]
                ),
                encoding="utf-8",
            )
            payload = train_two_layer_bandit_policy_from_csv(recent, major, output, major_correction_weight=0.5)
        self.assertAlmostEqual(payload["major_map_corrections"]["Ancient"], 0.6)  # type: ignore[index]
        self.assertEqual(payload["recent_example_count"], 2)
        self.assertEqual(payload["major_example_count"], 2)

    def test_action_value_uses_major_correction_layer(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            stats_path = Path(temp_dir) / "maps.csv"
            stats_path.write_text(
                "\n".join(
                    [
                        "team,map,maps_played,win_rate,pick_rate,ban_rate",
                        "Team 1,Ancient,10,50,0,0",
                        "Team 2,Ancient,10,50,0,0",
                    ]
                ),
                encoding="utf-8",
            )
            stats = load_map_stats(stats_path)
        without_major = BanditPolicy(map_rewards={"Ancient": 0.0}, action_rewards={"pick": 0.0})
        with_major = BanditPolicy(
            map_rewards={"Ancient": 0.0},
            action_rewards={"pick": 0.0},
            major_map_corrections={"Ancient": 1.0},
            major_action_corrections={"pick": 1.0},
            major_correction_weight=1.0,
        )
        self.assertGreater(
            action_value("Team 1", "Team 2", "Ancient", stats, with_major, "pick"),
            action_value("Team 1", "Team 2", "Ancient", stats, without_major, "pick"),
        )

    def test_map_veto_order_follows_valve_major_rules(self) -> None:
        ban_calls: list[str] = []

        def fake_ban(team: str, opponent: str, remaining: list[str], map_stats: object) -> str:
            ban_calls.append(team)
            return remaining[0]

        with patch("stage1_predictor.map_veto.choose_ban", fake_ban):
            simulate_bo1_veto("Team A", "Team B", ("A", "B", "C", "D", "E", "F", "G"), {})
        self.assertEqual(ban_calls, ["Team A", "Team A", "Team B", "Team B", "Team B", "Team A"])

        ban_calls = []

        def fake_pick(team: str, opponent: str, remaining: list[str], map_stats: object) -> str:
            return remaining[0]

        with patch("stage1_predictor.map_veto.choose_ban", fake_ban), patch("stage1_predictor.map_veto.choose_pick", fake_pick):
            simulate_bo3_veto("Team A", "Team B", ("A", "B", "C", "D", "E", "F", "G"), {})
        self.assertEqual(ban_calls, ["Team A", "Team B", "Team B", "Team A"])

    def test_bo3_match_maps_render_ordered_veto_actions(self) -> None:
        match = {
            "id": 119562,
            "slug": "liquid-vs-m80-cs-go-13-05-2026",
            "start_date": "2026-05-13T00:00:00.000Z",
            "team1": {"id": 790, "name": "Liquid"},
            "team2": {"id": 7430, "name": "M80"},
            "winner_team": {"id": 790, "name": "Liquid"},
            "games": [{"id": 1, "map_name": "de_dust2", "winner_clan_name": "Liquid"}],
            "_detail": {
                "match_maps": [
                    {"order": 2, "team_id": 7430, "choice_type": 2, "maps": {"name": "Nuke", "map_name": "de_nuke"}, "teams": {"id": 7430, "name": "M80"}},
                    {"order": 1, "team_id": 790, "choice_type": 2, "maps": {"name": "Overpass", "map_name": "de_overpass"}, "teams": {"id": 790, "name": "Liquid"}},
                    {"order": 3, "team_id": 790, "choice_type": 1, "maps": {"name": "Dust2", "map_name": "de_dust2"}, "teams": {"id": 790, "name": "Liquid"}},
                    {"order": 7, "team_id": None, "choice_type": 3, "maps": {"name": "Ancient", "map_name": "de_ancient"}, "teams": None},
                ]
            },
        }
        self.assertEqual(
            render_veto_sequence(match),
            "Liquid remove Overpass | M80 remove Nuke | Liquid pick Dust2 | Ancient left over",
        )
        rows = flatten_veto_actions(match, "test")
        self.assertEqual([row["action"] for row in rows], ["ban", "ban", "pick", "leftover"])
        self.assertEqual(rows[2]["map_won"], "true")
        self.assertEqual(rows[2]["reward"], "1.000")

    def test_glicko_features_include_uncertainty_from_sample_confidence(self) -> None:
        high = {"team": "A", "score": "1600", "sample_confidence_factor": "100", "map_pool_depth_factor": "100", "roster_data_factor": "100"}
        low = {"team": "B", "score": "1500", "sample_confidence_factor": "0", "map_pool_depth_factor": "0", "roster_data_factor": "0"}
        self.assertLess(initial_rating_from_row(high).deviation, initial_rating_from_row(low).deviation)
        features = rating_features(high, low)
        self.assertGreater(features["glicko_mean_diff"], 0)
        self.assertLess(features["glicko_uncertainty_diff"], 0)

    def test_catboost_pair_features_include_glicko_and_categoricals(self) -> None:
        left = {
            "event_id": "event",
            "team": "Team 1",
            "seed": "1",
            "score": "1600",
            "vrs_points": "1600",
            "region": "EU",
            "hltv_rating3": "1.10",
            "hltv_kd": "1.05",
            "hltv_maps": "120",
            "base_strength_factor": "100",
            "seed_path_factor": "100",
            "hltv_rating_factor": "100",
            "firepower_factor": "100",
            "map_pool_depth_factor": "100",
            "sample_confidence_factor": "100",
            "opponent_quality_proxy_factor": "100",
            "roster_data_factor": "80",
            "overall_factor_rating": "95",
        }
        right = dict(left, team="Team 2", seed="16", score="1400", vrs_points="1400", region="Asia", overall_factor_rating="40")
        features = build_pair_features(left, right)
        self.assertEqual(features["team"], "Team 1")
        self.assertEqual(features["same_region"], "False")
        self.assertGreater(float(features["glicko_expected"]), 0.5)

    def test_catboost_pretrain_csv_loads_featureized_match_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "pretrain.csv"
            cache = Path(temp_dir) / "match.html"
            cache.write_text("<html>real match</html>", encoding="utf-8")
            path.write_text(
                ",".join([*FEATURES, "target", "sample_weight", "source_url", "cache_path"]) + "\n"
                + ",".join(
                    ["0" if name in NUMERIC_FEATURES else "X" for name in FEATURES]
                    + ["1", "0.5", "https://www.hltv.org/matches/1/example", str(cache)]
                )
                + "\n",
                encoding="utf-8",
            )
            examples = load_pretrain_examples(path)
            provenance = validate_pretrain_csv(path)
        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0].target, 1)
        self.assertEqual(examples[0].weight, 0.5)
        self.assertTrue(provenance.ok)

    def test_catboost_example_scaling_preserves_features_and_scales_weight(self) -> None:
        example = PairwiseExample(features={"score_diff": 1.0, "team": "A"}, target=1, weight=0.4)
        scaled = scale_examples([example], 2.5)
        self.assertEqual(scaled[0].features, example.features)
        self.assertEqual(scaled[0].target, example.target)
        self.assertAlmostEqual(scaled[0].weight, 1.0)

    def test_prediction_metrics_evaluate_historical_advancement(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prediction = root / "prediction.json"
            labels = root / "labels.csv"
            prediction.write_text(
                json.dumps(
                    {
                        "probabilities": [
                            {"team": "Team 1", "p_advance": "80.0%"},
                            {"team": "Team 2", "p_advance": "20.0%"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            labels.write_text(
                "\n".join(
                    [
                        "event_id,stage_id,team,final_record,advanced,went_3_0,went_0_3,source",
                        "event,stage1,Team 1,3-1,true,false,false,test",
                        "event,stage1,Team 2,1-3,false,false,false,test",
                    ]
                ),
                encoding="utf-8",
            )
            metrics = evaluate_history(prediction, labels)
        self.assertAlmostEqual(metrics["brier_score"], 0.04)
        self.assertAlmostEqual(metrics["advance_accuracy"], 1.0)

    def test_hltv_match_rows_build_bidirectional_catboost_pretrain_rows(self) -> None:
        snapshot_rows = {
            "Team 1": {
                "event_id": "event",
                "team": "Team 1",
                "seed": "1",
                "score": "1600",
                "vrs_points": "1600",
                "region": "EU",
                "hltv_rating3": "1.10",
                "hltv_kd": "1.05",
                "hltv_maps": "120",
                "base_strength_factor": "100",
                "seed_path_factor": "100",
                "hltv_rating_factor": "100",
                "firepower_factor": "100",
                "map_pool_depth_factor": "100",
                "sample_confidence_factor": "100",
                "opponent_quality_proxy_factor": "100",
                "roster_data_factor": "80",
                "overall_factor_rating": "95",
                "format_type": "new_32_team_stage1",
                "round_system": "swiss_16_3win_3loss",
            },
            "Team 2": {
                "event_id": "event",
                "team": "Team 2",
                "seed": "2",
                "score": "1500",
                "vrs_points": "1500",
                "region": "EU",
                "hltv_rating3": "1.00",
                "hltv_kd": "1.00",
                "hltv_maps": "80",
                "base_strength_factor": "70",
                "seed_path_factor": "90",
                "hltv_rating_factor": "50",
                "firepower_factor": "50",
                "map_pool_depth_factor": "60",
                "sample_confidence_factor": "80",
                "opponent_quality_proxy_factor": "100",
                "roster_data_factor": "80",
                "overall_factor_rating": "70",
                "format_type": "new_32_team_stage1",
                "round_system": "swiss_16_3win_3loss",
            },
        }
        rows = build_pretrain_rows(
            [
                {
                    "team": "Team 1",
                    "opponent": "Team 2",
                    "target": "1",
                    "sample_weight": "0.8",
                    "source_url": "https://www.hltv.org/matches/1/example",
                    "cache_path": "/tmp/example.html",
                    "match_date": "2026-05-01",
                    "map": "Ancient",
                    "best_of": "BO3",
                    "veto_sequence": "Team 1 pick Ancient",
                    "score_for": "13",
                    "score_against": "10",
                }
            ],
            snapshot_rows,
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["target"], "1")
        self.assertEqual(rows[1]["target"], "0")
        self.assertEqual(rows[0]["source_url"], "https://www.hltv.org/matches/1/example")

    def test_real_data_validator_rejects_cloudflare_fetch_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            raw = Path(temp_dir) / "blocked.html"
            raw.write_text("<title>Just a moment...</title>", encoding="utf-8")
            report = Path(temp_dir) / "attempt.json"
            report.write_text(
                '{"attempts":[{"url":"https://www.hltv.org/stats/teams?csVersion=CS2","status_code":403,"blocked":true,"path":"'
                + str(raw)
                + '"}]}',
                encoding="utf-8",
            )
            result = validate_fetch_attempt_report(report)
        self.assertFalse(result.ok)
        self.assertTrue(any("did not fetch successfully" in error for error in result.errors))

    def test_real_data_validator_requires_hltv_source_urls(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "metrics.csv"
            path.write_text("team,source_url\nTeam,https://example.com/not-hltv\n", encoding="utf-8")
            result = validate_source_csv(path)
        self.assertFalse(result.ok)
        self.assertTrue(any("not an HLTV URL" in error for error in result.errors))

    def test_resolve_model_path_accepts_workspace_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            model = root / "model.cbm"
            model.write_text("model", encoding="utf-8")
            metadata = root / "nested" / "metadata.json"
            metadata.parent.mkdir()
            resolved = resolve_model_path(str(model), metadata)
        self.assertEqual(resolved, model)

    def test_best_of_three_probability_uses_three_maps(self) -> None:
        self.assertAlmostEqual(best_of_three_probability([0.6, 0.6, 0.6]), 0.648)

    def test_hltv_stats_parser_handles_rendered_rows(self) -> None:
        source = """
Team Maps K-D Diff K/D Rating 3.0
Image: United States NRG 527 +3370 1.10 1.10
Image: Europe GamerLegion 512 -633 0.98 1.04
"""
        metrics = parse_hltv_team_stats(source, ["NRG", "GamerLegion"])
        self.assertEqual(metrics["NRG"].maps, 527)
        self.assertEqual(metrics["GamerLegion"].kd_diff, -633)

    def test_hltv_team_overview_parser_averages_current_roster(self) -> None:
        source = """
Player Status Time on team Maps played Rating 3.0
INS
STARTER
2 years
1 month
278
1.09
Vexite
STARTER
2 years
1 month
278
1.08
nettik
STARTER
1 year
2 months
138
1.04
jks
STARTER
10 months
100
1.13
story
STARTER
4 months
46
1.13
* Will only show stats for a player's current team period.
"""
        metric = parse_hltv_team_overview_current_roster(source, "FlyQuest")
        self.assertIsNotNone(metric)
        assert metric is not None
        self.assertEqual(metric.maps, 168)
        self.assertAlmostEqual(metric.rating, 1.094)

    def test_cloudflare_challenge_detection(self) -> None:
        self.assertTrue(is_cloudflare_challenge("<title>Just a moment...</title><script src='/cdn-cgi/challenge-platform/x'></script>"))

    def test_build_hltv_feature_snapshot_writes_scores(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            teams_csv = root / "teams.csv"
            teams_csv.write_text(
                "\n".join(
                    ["seed,team,score,region,notes"]
                    + [f"{team.seed},{team.name},{team.score},EU," for team in sample_teams()]
                ),
                encoding="utf-8",
            )
            config = root / "config.json"
            config.write_text(
                '{"event_id":"event","stage_id":"stage1","prediction_cutoff":"2026-05-23"}',
                encoding="utf-8",
            )
            hltv_csv = root / "hltv.csv"
            hltv_csv.write_text(
                "team,maps,kd_diff,kd,rating3,source_type,source_url\nTeam 1,120,+100,1.10,1.12,team_stats,https://www.hltv.org/stats/teams?csVersion=CS2\n",
                encoding="utf-8",
            )
            output = root / "features.csv"
            build_hltv_feature_snapshot(
                teams_csv=teams_csv,
                config_path=config,
                hltv_team_stats_path=hltv_csv,
                output_path=output,
                prediction_cutoff="2026-05-23",
                feature_window_start="2026-02-23",
                feature_window_end="2026-05-23",
            )
            text = output.read_text(encoding="utf-8")
        self.assertIn("feature_score", text)
        self.assertIn("Team 1", text)
        self.assertIn("team_stats", text)

    def test_factor_snapshot_builds_explainable_factor_score(self) -> None:
        rows = []
        for team in sample_teams():
            rows.append(
                {
                    "team": team.name,
                    "seed": str(team.seed),
                    "score": f"{team.score:.0f}",
                    "vrs_points": f"{team.score:.0f}",
                    "region": "EU",
                    "hltv_maps": str(100 + team.seed),
                    "hltv_kd_diff": str(200 - team.seed),
                    "hltv_kd": "1.05",
                    "hltv_rating3": "1.07",
                    "hltv_source_type": "team_stats_all_time",
                }
            )
        factor_rows = build_factor_rows(rows)
        self.assertEqual(len(factor_rows), 16)
        self.assertIn("factor_score", factor_rows[0])
        self.assertIn("base_strength_factor", factor_rows[0])
        self.assertIn("地图 veto", factor_rows[0]["unavailable_factor_notes"])

    def test_factor_snapshot_accepts_trained_weights(self) -> None:
        rows = []
        for team in sample_teams():
            rows.append(
                {
                    "team": team.name,
                    "seed": str(team.seed),
                    "score": f"{team.score:.0f}",
                    "vrs_points": f"{team.score:.0f}",
                    "region": "EU",
                    "hltv_maps": "100",
                    "hltv_rating3": "1.05",
                    "hltv_source_type": "team_stats_all_time",
                }
            )
        prior_rows = build_factor_rows(rows)
        seed_heavy = {
            "base_strength_factor": 0.01,
            "hltv_rating_factor": 0.01,
            "firepower_factor": 0.01,
            "map_pool_depth_factor": 0.01,
            "sample_confidence_factor": 0.01,
            "opponent_quality_proxy_factor": 0.01,
            "roster_data_factor": 0.01,
            "seed_path_factor": 0.93,
        }
        trained_rows = build_factor_rows(rows, seed_heavy)
        self.assertNotEqual(prior_rows[-1]["factor_score"], trained_rows[-1]["factor_score"])

    def test_factor_weight_helpers_normalize_json_and_neighbors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "weights.json"
            path.write_text(
                '{"weights":{"base_strength_factor":35,"hltv_rating_factor":15,"firepower_factor":10,"map_pool_depth_factor":8,"sample_confidence_factor":8,"opponent_quality_proxy_factor":12,"roster_data_factor":5,"seed_path_factor":7}}',
                encoding="utf-8",
            )
            weights = load_factor_weights(path)
        self.assertAlmostEqual(sum(weights.values()), 1.0)
        neighbors = candidate_neighbors(weights, [0.02])
        self.assertGreater(len(neighbors), 1)
        self.assertAlmostEqual(sum(neighbors[-1].values()), 1.0)

    def test_factor_score_uses_weighted_factor_columns(self) -> None:
        row = {
            "base_strength_factor": "100",
            "hltv_rating_factor": "0",
            "firepower_factor": "0",
            "map_pool_depth_factor": "0",
            "sample_confidence_factor": "0",
            "opponent_quality_proxy_factor": "0",
            "roster_data_factor": "0",
            "seed_path_factor": "0",
        }
        weights = {
            "base_strength_factor": 1.0,
            "hltv_rating_factor": 0.0,
            "firepower_factor": 0.0,
            "map_pool_depth_factor": 0.0,
            "sample_confidence_factor": 0.0,
            "opponent_quality_proxy_factor": 0.0,
            "roster_data_factor": 0.0,
            "seed_path_factor": 0.0,
        }
        self.assertEqual(factor_score(row, weights), 1670.0)

    def test_calibration_json_loads_parameters(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "calibration.json"
            path.write_text(
                '{"parameters":{"scale":105,"bo1_shrink":0.65,"bo3_shrink":1.0,"veto_weight":0.8}}',
                encoding="utf-8",
            )
            params = load_calibration_params(path)
        self.assertEqual(params.scale, 105)
        self.assertEqual(params.bo1_shrink, 0.65)
        self.assertEqual(params.veto_weight, 0.8)

    def test_factor_veto_calibration_candidate_grid(self) -> None:
        candidates = build_candidates([90, 120], [0.65], [1.0], [1.0])
        self.assertEqual(candidates[0], CalibrationCandidate(scale=90, bo1_shrink=0.65, bo3_shrink=1.0, veto_weight=1.0))
        self.assertEqual(len(candidates), 2)

    def test_playoffs_simulation_has_single_champion(self) -> None:
        outcomes = run_playoff_simulations(sample_playoff_teams(), 25, 42, SimulationConfig())
        self.assertEqual(len(outcomes), 25)
        for outcome in outcomes:
            self.assertEqual(len(outcome.semifinalists), 4)
            self.assertEqual(len(outcome.finalists), 2)
            self.assertTrue(outcome.champion)

    def test_playoff_champion_probabilities_sum_to_one(self) -> None:
        teams = sample_playoff_teams()
        outcomes = run_playoff_simulations(teams, 100, 42, SimulationConfig())
        rows = summarize_playoff_probabilities(teams, outcomes)
        self.assertAlmostEqual(sum(float(row["p_champion"]) for row in rows), 1.0)


if __name__ == "__main__":
    unittest.main()
