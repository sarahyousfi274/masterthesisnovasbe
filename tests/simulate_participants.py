"""Evaluation episode 1 of Section 4.3.

"Before any founder takes part, simulated participants with known bias
parameters test whether the scoring recovers them, which bears on the scoring
inference."

Each synthetic participant carries three true parameters, one per form. The
script generates their decisions from those parameters, runs the real scoring
module over the result and reports how well the recovered scores correlate with
the parameters that produced them.

Run with:  python -m tests.simulate_participants
"""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sim import codebook, content, flow, scoring, state as game  # noqa: E402

N_PARTICIPANTS = 300
NOISE = 0.45          # decision noise, in units of the bias parameters


# ---------------------------------------------------------------------------
# Generating one synthetic participant
# ---------------------------------------------------------------------------

def _nearest_option(values: list[float], target: float) -> int:
    return min(range(len(values)), key=lambda i: abs(values[i] - target))


def simulate(code: str, truth: dict, rng: random.Random) -> list[dict]:
    """Produce response rows in the shape storage.fetch_responses returns."""
    track = flow.assign_track(rng)
    screens = flow.build(track, rng.randrange(1, 2**31 - 1))
    st = game.new_state(solo=False)
    rows: list[dict] = []
    index = 0

    for sc in screens:
        node_id = sc.get("node")
        if node_id is None:
            continue
        spec = codebook.load()["nodes"].get(node_id)
        if spec is None:
            continue
        snap = game.snapshot(st)
        kind = spec.get("type")

        if kind == "ladder":
            values = spec["option_values"]
            reference = codebook.ladder_reference(node_id, snap)
            spread = (max(values) - min(values)) or 1.0
            target = reference + spec["sign"] * (
                truth["est"] + rng.gauss(0, NOISE)) * spread * 0.5
            idx = _nearest_option(values, target)
            rows.append(_row(code, node_id, sc, index, snap,
                             option_key="ABCDEFG"[idx], option_index=idx))
            effects = content.SCREENS[node_id]["options"][idx].get("effects", {})
            st = game.apply(st, effects)

        elif kind == "contest":
            params = codebook.contest_params(node_id)
            # Perceived chance of winning, centred on the true 1 in 10.
            perceived = min(0.95, params["options"]["B"]["win_probability"]
                            * math.exp(truth["plc"] + rng.gauss(0, NOISE)))
            ev_b = perceived * params["prize"] - params["options"]["B"]["cost"]
            upgrade = min(0.95, params["options"]["C"]["win_probability"]
                          * math.exp(truth["plc"] + rng.gauss(0, NOISE)))
            ev_c = upgrade * params["prize"] - params["options"]["C"]["cost"]
            if max(ev_b, ev_c) <= 0:
                idx, key = 0, "A"
            elif ev_c > ev_b:
                idx, key = 2, "C"
            else:
                idx, key = 1, "B"
            rows.append(_row(code, node_id, sc, index, snap,
                             option_key=key, option_index=idx))
            st = game.apply(st, game.contest_effects(params["options"][key]["cost"]))

        elif kind == "interval":
            ref_lo = codebook.reference_quantile(node_id, 0.10)
            ref_hi = codebook.reference_quantile(node_id, 0.90)
            ref_mid = math.sqrt(ref_lo * ref_hi)
            log_half = (math.log(ref_hi) - math.log(ref_lo)) / 2
            # Narrower than the reference when the overprecision parameter is high.
            half = log_half * math.exp(-truth["prc"] - rng.gauss(0, NOISE * 0.5))
            centre = math.log(ref_mid) + rng.gauss(0, 0.25)
            lower = math.exp(centre - half)
            upper = math.exp(centre + half)
            # Scoring sorts the pair, so it does not matter which half holds
            # which value. The UI itself randomises opt/pes order anyway.
            rows.append(_row(code, node_id, sc, index, snap,
                             screen_id=f"{node_id}_opt", numeric_value=lower))
            index += 1
            rows.append(_row(code, node_id, sc, index, snap,
                             screen_id=f"{node_id}_pes", numeric_value=upper))

        elif kind == "attention_check":
            passed = rng.random() < 0.93
            correct = spec["correct_option"]
            if spec.get("mode") == "includes":
                key = "A," + correct if passed else "A,B"
                idx = None
            else:
                key = correct if passed else rng.choice(
                    [k for k in "ABCD" if k != correct])
                idx = "ABCD".index(key)
            rows.append(_row(code, node_id, sc, index, snap,
                             option_key=key, option_index=idx))

        elif kind == "outcome":
            # F4: higher overestimation makes the loan more likely.
            # H4: higher overprecision makes the gut-feeling hire more likely.
            driver = truth["est"] if node_id == "F4" else truth["prc"]
            p = 1 / (1 + math.exp(-1.1 * driver))
            if node_id == "F4":
                key = "A" if rng.random() < p else rng.choice(["B", "C"])
            else:
                key = "B" if rng.random() < p else rng.choice(["A", "C"])
            idx = "ABC".index(key)
            rows.append(_row(code, node_id, sc, index, snap,
                             option_key=key, option_index=idx))
            st = game.apply(st, content.SCREENS[node_id]["options"][idx].get("effects", {}))

        index += 1
        if sc.get("node_position") == 4:
            st = game.advance_block(st)

    return rows


def _row(code, node_id, sc, index, snap, *, screen_id=None, option_key=None,
         option_index=None, numeric_value=None) -> dict:
    return {
        "code": code,
        "screen_id": screen_id or node_id,
        "node": node_id,
        "domain": sc.get("domain"),
        "block_position": sc.get("block_position"),
        "node_position": sc.get("node_position"),
        "screen_index": index,
        "option_key": option_key,
        "option_index": option_index,
        "numeric_value": numeric_value,
        "text_value": None,
        "response_seconds": 8.0,
        "state_json": json.dumps(snap),
        "answered_at": None,
    }


# ---------------------------------------------------------------------------
# Recovery check
# ---------------------------------------------------------------------------

def pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den else float("nan")


def main() -> int:
    rng = random.Random(20261011)
    truths, scored = {}, {}

    for i in range(N_PARTICIPANTS):
        code = f"SIM-{i:04d}"
        truth = {"est": rng.gauss(0, 1), "plc": rng.gauss(0, 1), "prc": rng.gauss(0, 1)}
        truths[code] = truth
        scored[code] = scoring.score_participant(simulate(code, truth, rng), seed=i)

    standardised = scoring.standardise(scored)

    print(f"Simulated participants: {N_PARTICIPANTS}")
    print(f"Codebook: {codebook.version()}\n")

    print("Recovery of the true bias parameters by the form scores")
    print("-" * 62)
    ok = True
    for form, key in (("overestimation", "est"), ("overplacement", "plc"),
                      ("overprecision", "prc")):
        codes = [c for c in standardised
                 if f"form_{form}" in standardised[c]["_indices"]]
        recovered = [standardised[c]["_indices"][f"form_{form}"] for c in codes]
        true = [truths[c][key] for c in codes]
        r = pearson(true, recovered)
        flag = "ok " if r >= 0.70 else "LOW"
        ok &= r >= 0.70
        print(f"  {form:<16} r = {r:5.3f}   {flag}  (n = {len(codes)})")

    print("\nDiscriminant check: each form score against the other two parameters")
    print("-" * 62)
    for form, key in (("overestimation", "est"), ("overplacement", "plc"),
                      ("overprecision", "prc")):
        codes = [c for c in standardised
                 if f"form_{form}" in standardised[c]["_indices"]]
        recovered = [standardised[c]["_indices"][f"form_{form}"] for c in codes]
        others = []
        for other_key in ("est", "plc", "prc"):
            if other_key == key:
                continue
            r = pearson([truths[c][other_key] for c in codes], recovered)
            others.append(f"{other_key} {r:+.3f}")
        print(f"  {form:<16} {'   '.join(others)}")

    print("\nNode level summary")
    print("-" * 62)
    summary = scoring.sample_summary(standardised)
    for node_id in sorted(summary):
        row = summary[node_id]
        if row["form"] == "overestimation":
            print(f"  {node_id}  mean distance {row['mean_distance']:+.3f}  |  "
                  f"above/at/below {row['share_above_reference']:.0%}/"
                  f"{row['share_at_reference']:.0%}/"
                  f"{row['share_below_reference']:.0%}  |  "
                  f"options above reference: {row['options_above_reference']}, "
                  f"below: {row['options_below_reference']}")
        elif row["form"] == "overplacement":
            print(f"  {node_id}  entry rate {row['entry_rate']:.0%} "
                  f"(break-even {row['break_even_entry_rate']:.0%}), "
                  f"upgrade {row['upgrade_rate']:.0%}")
        elif row["form"] == "overprecision":
            print(f"  {node_id}  median width ratio {row['median_width_ratio']:.2f}, "
                  f"expected coverage {row['mean_expected_coverage']:.0%} "
                  f"(target {row['target_coverage']:.0%}), "
                  f"hit rate {row['hit_rate']:.0%}")
        elif "pass_rate" in row:
            print(f"  {node_id}  attention check passed by {row['pass_rate']:.0%}")
        elif "choices" in row:
            print(f"  {node_id}  choices {row['choices']}")

    print("\nCorrelations between the three form scores")
    print("-" * 62)
    pairs = [("overestimation", "overplacement"), ("overestimation", "overprecision"),
             ("overplacement", "overprecision")]
    for a, b in pairs:
        codes = [c for c in standardised
                 if f"form_{a}" in standardised[c]["_indices"]
                 and f"form_{b}" in standardised[c]["_indices"]]
        r = pearson([standardised[c]["_indices"][f"form_{a}"] for c in codes],
                    [standardised[c]["_indices"][f"form_{b}"] for c in codes])
        print(f"  {a} / {b}: r = {r:+.3f}")
    print("\n(The three parameters were drawn independently, so these should sit "
          "near zero.\n Requirement R2 asks the same of the real sample.)")

    print("\nRESULT:", "scoring recovers the parameters" if ok
          else "recovery below 0.70 for at least one form")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
