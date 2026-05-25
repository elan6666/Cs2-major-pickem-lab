from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CalibrationParams:
    scale: float
    bo1_shrink: float
    bo3_shrink: float
    veto_weight: float = 1.0


def load_calibration_params(path: str | Path) -> CalibrationParams:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    params = payload.get("parameters", payload)
    return CalibrationParams(
        scale=float(params["scale"]),
        bo1_shrink=float(params["bo1_shrink"]),
        bo3_shrink=float(params["bo3_shrink"]),
        veto_weight=float(params.get("veto_weight", 1.0)),
    )
