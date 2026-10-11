"""Builds the sequence of screens for one session.

Half the participants get Track 1 and half Track 2, so that order and fatigue
effects can be checked. Within each block the three measurement nodes run in
random order and the outcome or filler node is last.
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
        {"id": "practice_name", "kind": "practice_name"},
        {"id": "practice_low", "kind": "practice_range", "half": "low"},
        {"id": "practice_high", "kind": "practice_range", "half": "high"},
    ]

    for position, domain in enumerate(content.TRACKS[track], start=1):
        block = content.BLOCKS[domain]
        screens.append({"id": f"intro_{domain}", "kind": "block_intro", "domain": domain})

        nodes = list(block["nodes"])
        rng.shuffle(nodes)
        for order_in_block, node_id in enumerate(nodes, start=1):
            spec = content.SCREENS[node_id]
            common = {"node": node_id, "domain": domain,
                      "block_position": position, "node_position": order_in_block}
            if spec["kind"] == "interval":
                screens.append({"id": f"{node_id}_opt", "kind": "interval",
                                "half": "optimistic", **common})
                screens.append({"id": f"{node_id}_pes", "kind": "interval",
                                "half": "pessimistic", **common})
            else:
                screens.append({"id": node_id, "kind": spec["kind"], **common})

        last = block["last"]
        screens.append({"id": last, "kind": content.SCREENS[last]["kind"],
                        "node": last, "domain": domain,
                        "block_position": position, "node_position": 4})
        screens.append({"id": f"report_{domain}", "kind": "report", "domain": domain})

    screens += [
        {"id": "suspicion", "kind": "suspicion"},
        {"id": "profile", "kind": "profile"},
        {"id": "experience", "kind": "experience"},
        {"id": "risk", "kind": "risk"},
        {"id": "debrief_purpose", "kind": "debrief_purpose"},
        {"id": "debrief_data", "kind": "debrief_data"},
        {"id": "debrief_results", "kind": "debrief_results"},
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
