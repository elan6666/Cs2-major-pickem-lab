from __future__ import annotations

import math
from dataclasses import dataclass


DEFAULT_RATING = 1500.0
DEFAULT_RD = 350.0
Q = math.log(10) / 400.0


@dataclass(frozen=True)
class RatingState:
    mean: float = DEFAULT_RATING
    deviation: float = DEFAULT_RD


def initial_rating_from_row(row: dict[str, str]) -> RatingState:
    base_score = number(row, "factor_score", number(row, "feature_score", number(row, "score", DEFAULT_RATING)))
    sample_confidence = number(row, "sample_confidence_factor", number(row, "sample_confidence", 50.0))
    map_depth = number(row, "map_pool_depth_factor", 50.0)
    roster_confidence = number(row, "roster_data_factor", 50.0)
    confidence = max(0.0, min(100.0, (sample_confidence * 0.45) + (map_depth * 0.35) + (roster_confidence * 0.20)))
    deviation = 60.0 + (100.0 - confidence) * 2.2
    return RatingState(mean=base_score, deviation=deviation)


def expected_score(left: RatingState, right: RatingState) -> float:
    scale = math.sqrt(1.0 + (3.0 * Q * Q * right.deviation * right.deviation) / (math.pi * math.pi))
    g = 1.0 / scale
    exponent = -g * (left.mean - right.mean) / 400.0
    return 1.0 / (1.0 + math.pow(10.0, exponent))


def update_rating(player: RatingState, opponents: list[tuple[RatingState, float]]) -> RatingState:
    if not opponents:
        return player
    variance_inv = 0.0
    delta_sum = 0.0
    for opponent, score in opponents:
        g = glicko_g(opponent.deviation)
        expectation = 1.0 / (1.0 + math.pow(10.0, -g * (player.mean - opponent.mean) / 400.0))
        variance_inv += (g * g) * expectation * (1.0 - expectation)
        delta_sum += g * (score - expectation)
    if variance_inv <= 0:
        return player
    d_squared = 1.0 / (Q * Q * variance_inv)
    new_deviation = 1.0 / math.sqrt((1.0 / (player.deviation * player.deviation)) + (1.0 / d_squared))
    new_mean = player.mean + (Q / ((1.0 / (player.deviation * player.deviation)) + (1.0 / d_squared))) * delta_sum
    return RatingState(mean=new_mean, deviation=max(30.0, min(DEFAULT_RD, new_deviation)))


def glicko_g(deviation: float) -> float:
    return 1.0 / math.sqrt(1.0 + (3.0 * Q * Q * deviation * deviation) / (math.pi * math.pi))


def rating_features(left: dict[str, str], right: dict[str, str]) -> dict[str, float]:
    left_rating = initial_rating_from_row(left)
    right_rating = initial_rating_from_row(right)
    return {
        "glicko_mean_diff": left_rating.mean - right_rating.mean,
        "glicko_uncertainty_diff": left_rating.deviation - right_rating.deviation,
        "glicko_expected": expected_score(left_rating, right_rating),
        "left_glicko_mean": left_rating.mean,
        "right_glicko_mean": right_rating.mean,
        "left_glicko_rd": left_rating.deviation,
        "right_glicko_rd": right_rating.deviation,
    }


def number(row: dict[str, str], field: str, default: float) -> float:
    value = row.get(field, "")
    if value is None or str(value).strip() == "":
        return default
    return float(str(value).strip())
