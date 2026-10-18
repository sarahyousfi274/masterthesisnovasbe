"""Builds the sequence of screens for one session.

Half the participants get Track 1 and half Track 2, so that order and fatigue
effects can be checked. Within each block all four nodes (three measurement
nodes plus the attention or outcome node) are shuffled, so the attention
check does not sit at a predictable position. For each interval node the
order of the optimistic and the pessimistic value is also randomised.

Demographics, the warm-up and the starting situation screen all come BEFORE
the first block, so participants have context when the first decision lands.
"""

from __future__ import annotations

import random

from . import content


def build(track: int, seed: int) -> list[dict]:
    """Return the ordered list of screens for one session."""
    rng = random.Random(seed)
    screens: list[dict] = [
        {"id": "consent", "kind": "consent"},
        {"id": "filter", "kind": "filter"},
        {"id": "setup", "kind": "setup"},
        {"id": "code", "kind": "code"},
        {"id": "profile", "kind": "profile"},
        {"id": "experience", "kind": "experience"},
        {"id": "risk", "kind": "risk"},
        {"id": "warmup_intro", "kind": "warmup_intro"},
        {"id": "practice_name", "kind": "practice_name"},
        {"id": "practice_low", "kind": "practice_range", "half": "low"},
        {"id": "practice_high", "kind": "practice_range", "half": "high"},
        {"id": "starting_situation", "kind": "starting_situation"},
    ]

    for position, domain in enumerate(content.TRACKS[track], start=1):
        block = content.BLOCKS[domain]
        screens.append({"id": f"intro_{domain}", "kind": "block_intro",
                        "domain": domain})

        # All four nodes shuffled: three measurement + the attention/outcome
        # node. This removes the fixed last-position pattern of earlier builds.
        nodes = list(block["nodes"]) + [block["attention"]]
        rng.shuffle(nodes)

        for order_in_block, node_id in enumerate(nodes, start=1):
            spec = content.SCREENS[node_id]
            common = {"node": node_id, "domain": domain,
                      "block_position": position,
                      "node_position": order_in_block}
            if spec["kind"] == "interval":
                # Randomise whether optimistic or pessimistic is asked first.
                halves = ["optimistic", "pessimistic"]
                rng.shuffle(halves)
                for half in halves:
                    suffix = "opt" if half == "optimistic" else "pes"
                    screens.append({"id": f"{node_id}_{suffix}",
                                    "kind": "interval", "half": half,
                                    **common})
            else:
                screens.append({"id": node_id, "kind": spec["kind"], **common})

        screens.append({"id": f"report_{domain}", "kind": "report",
                        "domain": domain})

    screens += [
        {"id": "suspicion", "kind": "suspicion"},
        {"id": "end", "kind": "end"},
    ]
    return screens


def assign_track(rng: random.Random) -> int:
    return rng.choice([1, 2])


def make_code(rng: random.Random) -> str:
    """Pseudonym code shown to the participant, used for withdrawal and to
    link the session to the follow-up a week later."""
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"   # no I or O
    digits = "23456789"                     # no 0 or 1
    return (
        "".join(rng.choice(letters) for _ in range(3))
        + "-"
        + "".join(rng.choice(digits) for _ in range(4))
    )


def progress(screens: list[dict], index: int) -> tuple[int, int]:
    """Position for the progress bar, deliberately coarse so that it does not
    reveal the structure of the blocks."""
    return min(index + 1, len(screens)), len(screens)


# Screens where a Back button is allowed. Everything else is one-way, so that
# answers are not adjusted retrospectively.
BACK_ALLOWED = {"warmup_intro", "practice_name", "practice_range",
                "starting_situation"}
