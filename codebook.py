"""Access to the hidden reference values.

Nothing in this module is ever rendered to a participant during the session.
The debrief reads it through `draw_reference_value` and `contest_outcome` only.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

CODEBOOK_PATH = Path(__file__).with_name("codebook.json")


@lru_cache(maxsize=1)
def load() -> dict:
    with CODEBOOK_PATH.open(encoding="utf-8") as fh:
        book = json.load(fh)
    if book.get("contest_variant") == "walkthrough":
        for node_id, node in book["nodes"].items():
            variant = node.get("walkthrough_variant")
            if variant:
                node.update(variant)
    return book


def node(node_id: str) -> dict:
    return load()["nodes"][node_id]


def version() -> str:
    return f'{load()["codebook_version"]}-{load().get("contest_variant", "harmonised")}'


# ---------------------------------------------------------------------------
# Contests
# ---------------------------------------------------------------------------

def contest_params(node_id: str) -> dict:
    """Prize, costs and win probabilities, with expected values computed."""
    spec = node(node_id)
    out = {
        "prize": spec["prize"],
        "competitors": spec["competitors"],
        "options": {},
    }
    for key, opt in spec["options"].items():
        ev = opt["win_probability"] * spec["prize"] - opt["cost"]
        out["options"][key] = {**opt, "expected_value": ev}
    out["base_cost"] = spec["options"]["B"]["cost"]
    out["upgrade_cost"] = spec["options"]["C"]["cost"]
    return out


def contest_outcome(node_id: str, option_key: str, rng) -> dict:
    """Draw the outcome of one contest. Called only at the debrief."""
    params = contest_params(node_id)
    opt = params["options"][option_key]
    if opt["win_probability"] == 0:
        return {"entered": False, "won": None, "net": 0,
                "win_probability": 0.0, "prize": params["prize"]}
    won = rng.random() < opt["win_probability"]
    net = (params["prize"] if won else 0) - opt["cost"]
    return {"entered": True, "won": won, "net": net,
            "win_probability": opt["win_probability"], "prize": params["prize"],
            "cost": opt["cost"], "expected_value": opt["expected_value"]}


# ---------------------------------------------------------------------------
# Reference distributions for the interval nodes
# ---------------------------------------------------------------------------

def _percentile_points(node_id: str) -> list[tuple[float, float]]:
    pts = node(node_id)["reference_percentiles"]
    return sorted((float(p), float(v)) for p, v in pts.items())


def reference_quantile(node_id: str, p: float) -> float:
    """Quantile function, log-linear between the stated percentile points.

    A parametric fit was rejected: the published percentiles for F3 are not
    exactly lognormal, and forcing a fit would move the reference away from the
    figures that are actually documented.
    """
    pts = _percentile_points(node_id)
    if p <= pts[0][0]:
        lo, hi = pts[0], pts[1]
    elif p >= pts[-1][0]:
        lo, hi = pts[-2], pts[-1]
    else:
        lo = max((pt for pt in pts if pt[0] <= p), key=lambda t: t[0])
        hi = min((pt for pt in pts if pt[0] >= p), key=lambda t: t[0])
        if lo[0] == hi[0]:
            return lo[1]
    frac = (p - lo[0]) / (hi[0] - lo[0])
    lo_v = max(lo[1], 1e-9)
    hi_v = max(hi[1], 1e-9)
    return math.exp(math.log(lo_v) + frac * (math.log(hi_v) - math.log(lo_v)))


def reference_cdf(node_id: str, value: float) -> float:
    """Share of the reference distribution at or below `value`."""
    pts = _percentile_points(node_id)
    value = max(float(value), 1e-9)
    if value <= pts[0][1]:
        # Extrapolate below the lowest stated percentile, floored at 0.
        lo, hi = pts[0], pts[1]
        slope = (hi[0] - lo[0]) / max(math.log(hi[1]) - math.log(lo[1]), 1e-9)
        return max(0.0, lo[0] + slope * (math.log(value) - math.log(max(lo[1], 1e-9))))
    if value >= pts[-1][1]:
        lo, hi = pts[-2], pts[-1]
        slope = (hi[0] - lo[0]) / max(math.log(hi[1]) - math.log(lo[1]), 1e-9)
        return min(1.0, hi[0] + slope * (math.log(value) - math.log(hi[1])))
    for (p_lo, v_lo), (p_hi, v_hi) in zip(pts, pts[1:]):
        if v_lo <= value <= v_hi:
            frac = (math.log(value) - math.log(max(v_lo, 1e-9))) / max(
                math.log(max(v_hi, 1e-9)) - math.log(max(v_lo, 1e-9)), 1e-9)
            return p_lo + frac * (p_hi - p_lo)
    return 1.0


def reference_width(node_id: str) -> float:
    """Width of the reference 10th to 90th percentile range."""
    return reference_quantile(node_id, 0.90) - reference_quantile(node_id, 0.10)


def draw_reference_value(node_id: str, rng) -> float:
    """One realised value from the reference distribution, for the debrief."""
    return reference_quantile(node_id, rng.random())


# ---------------------------------------------------------------------------
# Ladder reference values
# ---------------------------------------------------------------------------

def ladder_reference(node_id: str, state: dict | None = None) -> float:
    """Reference value in the node's own unit.

    F1 is state-dependent: the reference is the delay that still leaves the
    documented runway buffer at the moment the raise starts.
    """
    spec = node(node_id)
    if "reference_rule" in spec and state is not None:
        runway = state.get("runway", 0)
        return max(0.0, runway - spec["reference_runway_remaining"])
    return float(spec["reference_value"])


def ladder_option_value(node_id: str, option_index: int) -> float:
    return float(node(node_id)["option_values"][option_index])
