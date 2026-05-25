from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bandit_veto import load_bandit_policy
from .calibration import load_calibration_params
from .io import load_locked_results, load_teams
from .map_veto import load_map_stats, parse_map_pool
from .model_registry import MODEL_CHOICES, apply_team_model, resolve_model_name
from .pickem import PickemConfig, recommend_pickem_card, summarize_probabilities
from .reporting import (
    render_markdown_report,
    write_json_summary,
    write_markdown_report,
    write_probability_csv,
)
from .swiss import SimulationConfig, run_simulations
from .train_stage1_model import TARGETS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CS2 Major Stage 1 Pick'Em predictor")
    parser.add_argument("--teams", required=True, help="Path to teams CSV")
    parser.add_argument("--locked-results", help="Optional locked results CSV")
    parser.add_argument("--snapshot", help="Optional pre-event feature snapshot for model scoring")
    parser.add_argument("--model-json", help="Optional trained model JSON for model-derived scoring")
    parser.add_argument("--model", default="vrs", choices=MODEL_CHOICES)
    parser.add_argument("--model-target", default="advanced", choices=TARGETS)
    parser.add_argument("--feature-snapshot", help="Optional feature snapshot for feature-score model")
    parser.add_argument("--score-column", default="feature_score", help="Score column for feature-score model")
    parser.add_argument("--stage-name", default="Stage 1", help="Report label for the Swiss stage")
    parser.add_argument("--advance-label", default="晋级", help="Report label for reaching the next phase")
    parser.add_argument("--simulations", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--scale", type=float, default=120.0)
    parser.add_argument("--bo1-shrink", type=float, default=0.70)
    parser.add_argument("--bo3-shrink", type=float, default=1.00)
    parser.add_argument("--veto-weight", type=float, default=1.00)
    parser.add_argument("--calibration-json", help="Optional factor-veto calibration JSON")
    parser.add_argument("--all-bo3", action="store_true")
    parser.add_argument("--map-stats", help="Optional team map stats CSV for veto-adjusted match probabilities")
    parser.add_argument("--map-pool", help="Comma-separated active map pool for veto simulation")
    parser.add_argument("--veto-policy", default="greedy", choices=("greedy", "contextual-bandit"))
    parser.add_argument("--bandit-policy-json", help="Optional trained contextual bandit veto policy JSON")
    parser.add_argument("--pass-threshold", type=int, default=5)
    parser.add_argument("--three-zero-picks", type=int, default=2)
    parser.add_argument("--zero-three-picks", type=int, default=2)
    parser.add_argument("--advance-picks", type=int, default=6)
    parser.add_argument("--report", help="Optional Markdown report path")
    parser.add_argument("--csv", help="Optional probability CSV output path")
    parser.add_argument("--json", help="Optional JSON summary output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    selected_model = resolve_model_name(args.model, args.snapshot, args.model_json)
    effective_score_column = args.score_column
    if selected_model == "factor-score" and effective_score_column == "feature_score":
        effective_score_column = "factor_score"
    teams = load_teams(args.teams)
    try:
        teams = apply_team_model(
            teams=teams,
            model=args.model,
            scale=args.scale,
            snapshot=args.snapshot,
            model_json=args.model_json,
            model_target=args.model_target,
            feature_snapshot=args.feature_snapshot,
            score_column=args.score_column,
        )
    except (ValueError, NotImplementedError) as exc:
        parser.error(str(exc))
    locked_results = load_locked_results(args.locked_results)
    calibration = load_calibration_params(args.calibration_json) if args.calibration_json else None
    sim_config = SimulationConfig(
        scale=calibration.scale if calibration else args.scale,
        bo1_shrink=calibration.bo1_shrink if calibration else args.bo1_shrink,
        bo3_shrink=calibration.bo3_shrink if calibration else args.bo3_shrink,
        veto_weight=calibration.veto_weight if calibration else args.veto_weight,
        all_bo3=args.all_bo3,
        map_pool=parse_map_pool(args.map_pool) if args.map_stats else (),
        map_stats=load_map_stats(args.map_stats) if args.map_stats else None,
        veto_policy=args.veto_policy,
        bandit_policy=load_bandit_policy(args.bandit_policy_json) if args.bandit_policy_json else None,
    )
    pickem_config = PickemConfig(
        pass_threshold=args.pass_threshold,
        three_zero_picks=args.three_zero_picks,
        zero_three_picks=args.zero_three_picks,
        advance_picks=args.advance_picks,
    )

    outcomes = run_simulations(
        teams=teams,
        simulations=args.simulations,
        seed=args.seed,
        config=sim_config,
        locked_results=locked_results,
    )
    probabilities = summarize_probabilities(teams, outcomes)
    card = recommend_pickem_card(probabilities, outcomes, pickem_config)

    settings = {
        "teams": str(Path(args.teams)),
        "locked_results": str(Path(args.locked_results)) if args.locked_results else "",
        "snapshot": str(Path(args.snapshot)) if args.snapshot else "",
        "model_json": str(Path(args.model_json)) if args.model_json else "",
        "model": selected_model,
        "model_target": args.model_target if args.model_json else "",
        "feature_snapshot": str(Path(args.feature_snapshot)) if args.feature_snapshot else "",
        "score_column": effective_score_column if args.feature_snapshot else "",
        "stage_name": args.stage_name,
        "advance_label": args.advance_label,
        "simulations": args.simulations,
        "seed": args.seed,
        "scale": args.scale,
        "effective_scale": sim_config.scale,
        "bo1_shrink": args.bo1_shrink,
        "effective_bo1_shrink": sim_config.bo1_shrink,
        "bo3_shrink": args.bo3_shrink,
        "effective_bo3_shrink": sim_config.bo3_shrink,
        "veto_weight": sim_config.veto_weight,
        "calibration_json": str(Path(args.calibration_json)) if args.calibration_json else "",
        "all_bo3": args.all_bo3,
        "map_stats": str(Path(args.map_stats)) if args.map_stats else "",
        "map_pool": ", ".join(sim_config.map_pool) if args.map_stats else "",
        "veto_policy": sim_config.veto_policy if args.map_stats else "",
        "bandit_policy_json": str(Path(args.bandit_policy_json)) if args.bandit_policy_json else "",
        "catboost_metadata": read_model_metadata(args.model_json) if selected_model == "catboost" and args.model_json else "",
        "pass_threshold": args.pass_threshold,
        "three_zero_picks": args.three_zero_picks,
        "zero_three_picks": args.zero_three_picks,
        "advance_picks": args.advance_picks,
    }

    report = render_markdown_report(probabilities, card, settings)
    if args.report:
        write_markdown_report(args.report, report)
    if args.csv:
        write_probability_csv(args.csv, probabilities)
    if args.json:
        write_json_summary(args.json, probabilities, card, settings)

    print(report)
    return 0


def read_model_metadata(path: str) -> dict[str, object]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {
        "model_path": payload.get("model_path", ""),
        "stage1_training_mode": payload.get("stage1_training_mode", ""),
        "stage2_training_mode": payload.get("stage2_training_mode", ""),
        "example_count": payload.get("example_count", 0),
    }


if __name__ == "__main__":
    raise SystemExit(main())
