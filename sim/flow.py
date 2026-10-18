"""Builds the sequence of screens for one session.

Half the participants get Track 1 and half Track 2, so that order and fatigue
effects can be checked.

Within a block, nodes that build on each other keep their order (you decide
when to fundraise before you decide how; you open roles before you fill one).
The remaining nodes, including the attention check, are inserted at random
positions, so the attention check does not sit at a predictable place.

Every screen carries a `section`, which drives the bar at the top.
"""

from __future__ import annotations

import random

from . import content

# Screens that only show information. Going back to one of them cannot change
# an answer, so a Back button is offered on the screen that follows them.
INFO_KINDS = {"consent", "warmup_intro", "starting_situation", "block_intro",
              "report"}

# In this section every screen may go back (questions about the person).
BACK_SECTIONS = {content.SECTION_ABOUT}


def build(track: int, seed: int) -> list[dict]:
    """Return the ordered list of screens for one session."""
    rng = random.Random(seed)
    about, how, startup, wrap = (content.SECTION_ABOUT, content.SECTION_HOW,
                                 content.SECTION_STARTUP, content.SECTION_WRAP)
    screens: list[dict] = [
        {"id": "consent", "kind": "consent", "section": None},
        {"id": "filter", "kind": "filter", "section": about},
        {"id": "email", "kind": "email", "section": about},
        {"id": "profile", "kind": "profile", "section": about},
        {"id": "experience", "kind": "experience", "section": about},
        {"id": "risk", "kind": "risk", "section": about},
        {"id": "warmup_intro", "kind": "warmup_intro", "section": how},
        {"id": "practice_choice", "kind": "practice_choice", "section": how},
        {"id": "practice_range", "kind": "practice_range", "section": how},
        {"id": "setup", "kind": "setup", "section": startup},
        {"id": "starting_situation", "kind": "starting_situation",
         "section": startup},
    ]

    for position, domain in enumerate(content.TRACKS[track], start=1):
        block = content.BLOCKS[domain]
        section = block["title"]
        screens.append({"id": f"intro_{domain}", "kind": "block_intro",
                        "domain": domain, "section": section})

        nodes = list(block["sequence"])
        for node_id in block["floating"]:
            nodes.insert(rng.randint(0, len(nodes)), node_id)

        for order_in_block, node_id in enumerate(nodes, start=1):
            spec = content.SCREENS[node_id]
            screen = {"id": node_id, "kind": spec["kind"], "node": node_id,
                      "domain": domain, "block_position": position,
                      "node_position": order_in_block, "section": section}
            if spec["kind"] == "interval":
                # Which of the two fields comes first is randomised.
                screen["first"] = rng.choice(["best", "worst"])
            screens.append(screen)

        screens.append({"id": f"report_{domain}", "kind": "report",
                        "domain": domain, "section": section})

    screens += [
        {"id": "suspicion", "kind": "suspicion", "section": wrap},
        {"id": "end", "kind": "end", "section": wrap},
    ]
    return screens


def sections(screens: list[dict]) -> list[str]:
    """The sections in the order this participant meets them."""
    out: list[str] = []
    for sc in screens:
        sec = sc.get("section")
        if sec and sec not in out:
            out.append(sec)
    return out


def back_allowed(screens: list[dict], index: int) -> bool:
    """Back is offered among the questions about the person, and on any screen
    whose previous screen was information only. Never on the end screen."""
    if index <= 0 or screens[index]["kind"] == "end":
        return False
    if screens[index].get("section") in BACK_SECTIONS:
        return True
    return screens[index - 1]["kind"] in INFO_KINDS


def assign_track(rng: random.Random) -> int:
    return rng.choice([1, 2])


def make_code(rng: random.Random) -> str:
    """Internal session id. Never shown to the participant; it links the
    answers to the separately stored email address."""
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    digits = "23456789"
    return ("".join(rng.choice(letters) for _ in range(3)) + "-"
            + "".join(rng.choice(digits) for _ in range(4)))
