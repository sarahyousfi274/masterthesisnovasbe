"""Builds the sequence of screens for one session.

Participants are spread evenly over three tracks (a Latin square of the three
areas after Building the product), so order and fatigue effects are balanced
across areas and can be checked. See assign_track for the balanced allocation.

Within an area, nodes that build on each other keep their order (you decide
when to fundraise before you decide how; you open roles before you fill one).
Each contest comes as a pair with its rank question, which is asked first, and
the pair is inserted at a random position. The two attention checks sit in the
second and third area of the track, at a random position but never first.

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
        {"id": "sim_start", "kind": "transition", "section": None},
        {"id": "setup", "kind": "setup", "section": startup},
        {"id": "starting_situation", "kind": "starting_situation",
         "section": startup},
    ]

    for position, domain in enumerate(content.TRACKS[track], start=1):
        block = content.BLOCKS[domain]
        section = block["title"]
        screens.append({"id": f"intro_{domain}", "kind": "block_intro",
                        "domain": domain, "section": section})

        # Story order first; units (rank question + its contest) are inserted
        # as a pair at a random position.
        units: list[list[str]] = [[n] for n in block["sequence"]]
        # With an outcome node, inserted units go before it, never after.
        tail = 1 if block.get("outcome_last") else 0
        for unit in block.get("units", []):
            units.insert(rng.randint(0, len(units) - tail), list(unit))
        # Attention checks go into areas 2 and 3, never as the first decision.
        if position in (2, 3):
            check = content.ATTENTION_CHECKS[position - 2]
            units.insert(rng.randint(1, len(units) - tail), [check])
        nodes = [n for unit in units for n in unit]

        for order_in_block, node_id in enumerate(nodes, start=1):
            spec = content.SCREENS[node_id]
            screen = {"id": node_id, "kind": spec["kind"], "node": node_id,
                      "domain": domain, "block_position": position,
                      "node_position": order_in_block, "section": section}
            if spec["kind"] == "hire":
                # Which candidate is described first is randomised and stored.
                screen["first"] = rng.choice(["A", "B"])
            screens.append(screen)

        screens.append({"id": f"report_{domain}", "kind": "report",
                        "domain": domain, "section": section})

    final = content.SECTION_FINAL
    screens.append({"id": "final_intro", "kind": "final_intro", "section": final})
    for node_id in content.FINAL_ROUND:
        screens.append({"id": node_id, "kind": content.SCREENS[node_id]["kind"],
                        "node": node_id, "domain": "final", "section": final})
    # Final report: every outcome that was held back during the session.
    screens.append({"id": "report_final", "kind": "report", "domain": "final",
                    "section": final})
    screens += [
        {"id": "suspicion", "kind": "suspicion", "section": wrap},
        {"id": "end", "kind": "end", "section": wrap},
        {"id": "closed", "kind": "closed", "section": wrap},
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
    """Where a Back button is offered.

    - Among the questions about the person (filter to risk attitude).
    - In "How it works", from the first example back to the overview.
    - In the simulation only once per area: from the first decision back to the
      area's starting situation. Never between decisions, never from an area
      intro to the previous report, never in the wrap-up.
    """
    if index <= 0:
        return False
    here, prev = screens[index], screens[index - 1]
    if here.get("section") in BACK_SECTIONS:
        return True
    if here.get("section") == content.SECTION_HOW:
        return prev["kind"] == "warmup_intro"
    return prev["kind"] == "block_intro" and here.get("node") is not None


def assign_track(rng: random.Random, load: dict | None = None) -> int:
    """Balanced allocation. `load` counts, per track, the sessions completed so
    far plus those still running (see storage.track_load). The new participant
    gets the track with the lowest count; ties are broken at random. Without
    counts (for example if the database cannot be reached) the track is drawn
    at random, which is still unbiased, only less even."""
    tracks = sorted(content.TRACKS)
    if not load:
        return rng.choice(tracks)
    low = min(load.get(t, 0) for t in tracks)
    return rng.choice([t for t in tracks if load.get(t, 0) == low])


def make_code(rng: random.Random) -> str:
    """Internal session id. Never shown to the participant; it links the
    answers to the separately stored email address."""
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    digits = "23456789"
    return ("".join(rng.choice(letters) for _ in range(3)) + "-"
            + "".join(rng.choice(digits) for _ in range(4)))
