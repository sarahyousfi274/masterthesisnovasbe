"""Scoring, kept entirely outside the app so that nothing scored can leak into
the session. The app imports it only at the debrief.

Three forms, following the walkthrough of 5 October:

Overestimation  signed distance of the chosen option from the reference value,
                in the node's own unit, positive meaning more aggressive.
Overplacement   entry into contests whose expected value is negative, plus the
                size of the stake.
Overprecision   width of the stated range over the width of the reference
                range, plus the coverage of the reference distribution.

On coverage: the walkthrough scores a hit against one value drawn from the
reference distribution. That is kept for the debrief, because a participant can
understand a single realised value. For the analysis this module also reports
`expected_coverage`, the share of the reference distribution that falls inside
the stated range. It is the expectation of the binary hit without the sampling
noise of a single draw, so with one decision per cell it is the more efficient
statistic (Section 4.3 on reliability).
"""

from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict

from . import codebook

FORMS = ("overestimation", "overplacement", "overprecision")
DOMAINS = ("team", "finance", "hiring", "gtm")
TARGET_COVERAGE = 0.80


# ---------------------------------------------------------------------------
# One participant
# ---------------------------------------------------------------------------

def score_participant(responses: list[dict], seed: int | None = None) -> dict:
    """Turn the stored rows of one session into scores.

    `responses` are rows from storage.fetch_responses.
    """
    by_screen = {r["screen_id"]: r for r in responses}
    out: dict[str, dict] = {}
    rng = random.Random(seed if seed is not None else 0)

    for node_id, spec in codebook.load()["nodes"].items():
        kind = spec.get("type")
        if kind == "ladder":
            row = by_screen.get(node_id)
            if row is None or row["option_index"] is None:
                continue
            out[node_id] = _score_ladder(node_id, row)
        elif kind == "contest":
            row = by_screen.get(node_id)
            if row is None or row["option_key"] is None:
                continue
            out[node_id] = _score_contest(node_id, row, rng)
        elif kind == "interval":
            lo = by_screen.get(f"{node_id}_opt")
            hi = by_screen.get(f"{node_id}_pes")
            if lo is None or hi is None:
                continue
            out[node_id] = _score_interval(node_id, lo, hi, rng)
        elif kind == "rank":
            row = by_screen.get(node_id)
            if row is None or row["option_key"] is None:
                continue
            rank = int(row["option_key"])
            out[node_id] = {
                "node": node_id, "form": "overplacement", "domain": spec["domain"],
                "rank": rank, "reference_rank": spec["reference_rank"],
                "rank_score": spec["reference_rank"] - rank,
                "contest": spec["contest"],
                "response_seconds": row["response_seconds"],
            }
        elif kind == "attention_check":
            row = by_screen.get(node_id)
            if row is not None:
                picked = (row["option_key"] or "").split(",")
                if spec.get("mode") == "includes":
                    passed = spec["correct_option"] in picked
                else:
                    passed = row["option_key"] == spec["correct_option"]
                out[node_id] = {
                    "node": node_id, "form": "none", "domain": spec["domain"],
                    "passed": passed,
                }
        elif kind == "outcome":
            row = by_screen.get(node_id)
            if row is not None:
                out[node_id] = {
                    "node": node_id, "form": "none", "domain": spec["domain"],
                    "choice": row["option_key"],
                }
    return out


def _score_ladder(node_id: str, row: dict) -> dict:
    spec = codebook.node(node_id)
    state = json.loads(row["state_json"]) if row["state_json"] else {}
    chosen = codebook.ladder_option_value(node_id, row["option_index"])
    reference = codebook.ladder_reference(node_id, state)
    raw = spec["sign"] * (chosen - reference)

    # Ordinal distance, for reporting alongside the raw distance.
    values = spec["option_values"]
    ref_index = _interpolated_index(values, reference)
    step = spec["sign"] * (row["option_index"] - ref_index) * (
        -1 if values[0] > values[-1] else 1)

    return {
        "node": node_id, "form": "overestimation", "domain": spec["domain"],
        "chosen_option": row["option_key"], "chosen_value": chosen,
        "reference_value": reference, "raw_distance": raw, "step_distance": step,
        "response_seconds": row["response_seconds"],
    }


def _interpolated_index(values: list[float], reference: float) -> float:
    """Where the reference sits on the option ladder, allowing a value between
    two options."""
    ordered = list(enumerate(values))
    if values[0] > values[-1]:
        ordered = ordered[::-1]
    idxs = [i for i, _ in ordered]
    vals = [v for _, v in ordered]
    if reference <= vals[0]:
        return float(idxs[0])
    if reference >= vals[-1]:
        return float(idxs[-1])
    for (i_lo, v_lo), (i_hi, v_hi) in zip(ordered, ordered[1:]):
        if v_lo <= reference <= v_hi:
            frac = (reference - v_lo) / (v_hi - v_lo) if v_hi != v_lo else 0.0
            return i_lo + frac * (i_hi - i_lo)
    return float(idxs[-1])


def _score_contest(node_id: str, row: dict, rng: random.Random) -> dict:
    spec = codebook.node(node_id)
    params = codebook.contest_params(node_id)
    key = row["option_key"]
    opt = params["options"][key]
    outcome = codebook.contest_outcome(node_id, key, rng)
    return {
        "node": node_id, "form": spec.get("form", "overplacement"),
        "domain": spec["domain"], "chosen_option": key,
        "entered": 1 if opt["win_probability"] > 0 else 0,
        "stake": opt["cost"],
        "stake_ratio": opt["cost"] / params["prize"],
        "ordinal": row["option_index"],
        "expected_value": opt["expected_value"],
        "ev_loss": -opt["expected_value"],
        "outcome": outcome,
        "response_seconds": row["response_seconds"],
    }


def _score_interval(node_id: str, opt_row: dict, pes_row: dict,
                    rng: random.Random) -> dict:
    spec = codebook.node(node_id)
    a, b = opt_row["numeric_value"], pes_row["numeric_value"]
    if a is None or b is None:
        return {"node": node_id, "form": "overprecision", "domain": spec["domain"],
                "incomplete": True}
    if spec.get("scale_with"):
        state = json.loads(opt_row["state_json"]) if opt_row.get("state_json") else {}
        factor = (state.get(spec["scale_with"]) or spec["scale_base"]) / spec["scale_base"]
        if factor > 0:
            a, b = a / factor, b / factor
    lower, upper = (a, b) if a <= b else (b, a)
    reversed_order = a > b  # participant's optimistic value was the larger one

    ref_width = codebook.reference_width(node_id)
    width = upper - lower
    width_ratio = width / ref_width if ref_width else float("nan")

    cov_lo = codebook.reference_cdf(node_id, lower)
    cov_hi = codebook.reference_cdf(node_id, upper)
    expected_coverage = max(0.0, min(1.0, cov_hi - cov_lo))

    drawn = codebook.draw_reference_value(node_id, rng)
    hit = int(lower <= drawn <= upper)

    midpoint = math.sqrt(max(lower, 1e-9) * max(upper, 1e-9))
    midpoint_percentile = codebook.reference_cdf(node_id, midpoint)

    return {
        "node": node_id, "form": "overprecision", "domain": spec["domain"],
        "unit": spec["unit"],
        "optimistic": a, "pessimistic": b,
        "lower": lower, "upper": upper, "reversed_order": reversed_order,
        "width": width, "reference_width": ref_width,
        "width_ratio": width_ratio,
        "log_width_ratio": math.log(width_ratio) if width_ratio > 0 else float("-inf"),
        "expected_coverage": expected_coverage,
        "coverage_gap": TARGET_COVERAGE - expected_coverage,
        "drawn_value": drawn, "hit": hit,
        "midpoint": midpoint, "midpoint_percentile": midpoint_percentile,
        "response_seconds": (opt_row["response_seconds"] or 0)
                            + (pes_row["response_seconds"] or 0),
    }


# ---------------------------------------------------------------------------
# One sample
# ---------------------------------------------------------------------------

def _primary(entry: dict) -> float | None:
    """The score used for standardising and for the domain index."""
    form = entry.get("form")
    if entry.get("incomplete"):
        return None
    if form == "overestimation":
        return entry["raw_distance"]
    if form == "overplacement":
        if "rank_score" in entry:
            return float(entry["rank_score"])     # positive = above average
        return float(entry["ordinal"])
    if form == "overprecision":
        return -entry["log_width_ratio"]   # positive = narrower than reference
    return None


def standardise(scored: dict[str, dict[str, dict]]) -> dict[str, dict]:
    """Z-standardise each node across the sample.

    `scored` maps participant code to the output of score_participant.
    Returns the same structure with a `z` added per node.
    """
    values: dict[str, list[float]] = defaultdict(list)
    for per_node in scored.values():
        for node_id, entry in per_node.items():
            v = _primary(entry)
            if v is not None and math.isfinite(v):
                values[node_id].append(v)

    stats = {}
    for node_id, vals in values.items():
        mean = statistics.fmean(vals)
        sd = statistics.pstdev(vals) if len(vals) > 1 else 0.0
        stats[node_id] = (mean, sd)

    out = {}
    for code, per_node in scored.items():
        enriched = {}
        for node_id, entry in per_node.items():
            entry = dict(entry)
            v = _primary(entry)
            if v is not None and node_id in stats and math.isfinite(v):
                mean, sd = stats[node_id]
                entry["raw_primary"] = v
                entry["z"] = (v - mean) / sd if sd > 0 else 0.0
            enriched[node_id] = entry
        enriched["_indices"] = _indices(enriched)
        out[code] = enriched
    return out


def _indices(per_node: dict) -> dict:
    """Form scores, domain indices and the overall index for one participant."""
    by_form = defaultdict(list)
    by_domain = defaultdict(list)
    for node_id, entry in per_node.items():
        if node_id.startswith("_") or "z" not in entry:
            continue
        by_form[entry["form"]].append(entry["z"])
        by_domain[entry["domain"]].append(entry["z"])

    out = {f"form_{f}": statistics.fmean(v) for f, v in by_form.items() if v}
    out.update({f"domain_{d}": statistics.fmean(v) for d, v in by_domain.items() if v})
    all_z = [z for v in by_form.values() for z in v]
    if all_z:
        out["overall"] = statistics.fmean(all_z)
    return out


def sample_summary(standardised: dict[str, dict]) -> dict:
    """Group level figures, which is the level the design supports."""
    per_node = defaultdict(list)
    for per in standardised.values():
        for node_id, entry in per.items():
            if node_id.startswith("_"):
                continue
            per_node[node_id].append(entry)

    summary = {}
    for node_id, entries in per_node.items():
        spec = codebook.node(node_id)
        row: dict = {"form": spec.get("form"), "domain": spec.get("domain"),
                     "n": len(entries)}
        if spec.get("type") == "ladder":
            d = [e["raw_distance"] for e in entries]
            row["mean_distance"] = statistics.fmean(d)
            row["median_distance"] = statistics.median(d)
            row["share_above_reference"] = sum(x > 1e-9 for x in d) / len(d)
            row["share_at_reference"] = sum(abs(x) <= 1e-9 for x in d) / len(d)
            row["share_below_reference"] = sum(x < -1e-9 for x in d) / len(d)
            # How much room the ladder leaves on each side of the reference.
            # A ladder censored on the aggressive side can show caution better
            # than it can show overestimation (Zorowitz and Niv 2023 on ceiling
            # and floor effects).
            values = spec["option_values"]
            ref = statistics.fmean(e["reference_value"] for e in entries)
            row["options_above_reference"] = sum(
                spec["sign"] * (v - ref) > 1e-9 for v in values)
            row["options_below_reference"] = sum(
                spec["sign"] * (v - ref) < -1e-9 for v in values)
        elif spec.get("type") == "contest":
            row["entry_rate"] = statistics.fmean(e["entered"] for e in entries)
            row["upgrade_rate"] = statistics.fmean(e["ordinal"] == 2 for e in entries)
            row["mean_stake"] = statistics.fmean(e["stake"] for e in entries)
            row["break_even_entry_rate"] = codebook.node(node_id)[
                "options"]["B"]["win_probability"]
        elif spec.get("type") == "interval":
            valid = [e for e in entries if not e.get("incomplete")]
            if valid:
                row["median_width_ratio"] = statistics.median(
                    e["width_ratio"] for e in valid)
                row["mean_expected_coverage"] = statistics.fmean(
                    e["expected_coverage"] for e in valid)
                row["hit_rate"] = statistics.fmean(e["hit"] for e in valid)
                row["target_coverage"] = TARGET_COVERAGE
        elif spec.get("type") == "rank":
            ranks = [e["rank"] for e in entries]
            row["mean_rank"] = statistics.fmean(ranks)
            row["share_top_half"] = sum(r <= 5 for r in ranks) / len(ranks)
            row["reference_rank"] = spec["reference_rank"]
        elif spec.get("type") == "attention_check":
            row["pass_rate"] = statistics.fmean(e["passed"] for e in entries)
        elif spec.get("type") == "outcome":
            counts = defaultdict(int)
            for e in entries:
                counts[e["choice"]] += 1
            row["choices"] = dict(counts)
        summary[node_id] = row
    return summary
