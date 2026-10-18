"""The situation that travels through the game.

Only the chosen options change it, through the effect table in content.py.
Reference values and measurement results never touch it.

Between blocks:
- One month of burn is deducted from cash, so fundraising timing has a visible
  consequence. The deduction is small compared with the block effects, but it
  moves the runway downwards and makes delay visible.

Planned hires (pending_hires) are shown separately in the situation report
and are NOT folded into team_size. Only an actual hiring decision (H4) raises
team_size.
"""

from __future__ import annotations

import copy

from . import content


def new_state(solo: bool) -> dict:
    state = copy.deepcopy(content.START_STATE)
    if solo:
        state["team_size"] = 1
    state["runway"] = runway(state)
    return state


def runway(state: dict) -> int:
    if state["burn"] <= 0:
        return 99
    return max(0, int(state["cash"] // state["burn"]))


def launch_budget(state: dict) -> int:
    """G1 spends 25 percent of current cash, so the split stays comparable
    across situations and tracks."""
    return int(round(state["cash"] * 0.25, -2))


def apply(state: dict, effects: dict) -> dict:
    """Return a new state with `effects` applied."""
    new = copy.deepcopy(state)

    if effects.get("spend_launch_budget"):
        new["cash"] -= launch_budget(state)

    for key, delta in effects.items():
        if key == "spend_launch_budget":
            continue
        if key in ("morale", "market_confidence"):
            new[key] = max(1, min(5, new[key] + delta))
        elif key == "pending_hires":
            # Overwrite rather than add: H1 sets the plan for that block.
            new["pending_hires"] = delta
        else:
            new[key] = new.get(key, 0) + delta

    new["cash"] = max(0, new["cash"])
    new["burn"] = max(0, new["burn"])
    new["team_size"] = max(1, new["team_size"])
    new["customers"] = max(0, new["customers"])
    new["runway"] = runway(new)
    return new


def advance_block(state: dict) -> dict:
    """End of a block: one month of burn is deducted from cash.

    Pending hires stay pending; they do not join the team automatically.
    Opening a role is not the same as filling it (feedback 2026-10-18).
    """
    new = copy.deepcopy(state)
    new["cash"] = max(0, new["cash"] - new["burn"])
    new["runway"] = runway(new)
    return new


def contest_effects(cost: int) -> dict:
    return {"cash": -cost} if cost else {}


def report_rows(state: dict) -> list[tuple[str, str, str]]:
    """The situation report. State only, no judgement of the choices.

    Each row is (label, value, help_text) so hover tips can explain the field.
    """
    rows = [
        (content.STATE_LABELS["cash"],
         f'{state["cash"]:,.0f} euros',
         content.STATE_HELP["cash"]),
        (content.STATE_LABELS["burn"],
         f'{state["burn"]:,.0f} euros',
         content.STATE_HELP["burn"]),
        (content.STATE_LABELS["runway"],
         "more than 8 years" if state["runway"] >= 99 else f'{state["runway"]} months',
         content.STATE_HELP["runway"]),
        (content.STATE_LABELS["team_size"],
         f'{state["team_size"]} ' + ("person" if state["team_size"] == 1 else "people"),
         content.STATE_HELP["team_size"]),
    ]
    pending = state.get("pending_hires", 0)
    if pending:
        rows.append((content.STATE_LABELS["pending_hires"],
                     f'{pending} ' + ("role" if pending == 1 else "roles"),
                     content.STATE_HELP["pending_hires"]))
    rows.extend([
        (content.STATE_LABELS["morale"], f'{state["morale"]} of 5',
         content.STATE_HELP["morale"]),
        (content.STATE_LABELS["market_confidence"],
         f'{state["market_confidence"]} of 5',
         content.STATE_HELP["market_confidence"]),
        (content.STATE_LABELS["customers"], f'{state["customers"]:,.0f}',
         content.STATE_HELP["customers"]),
    ])
    return rows


def snapshot(state: dict) -> dict:
    """Logged at every measurement node and used as a control variable
    (Chen, Croson, Elfenbein and Posen 2018)."""
    return {k: state.get(k) for k in
            ("cash", "burn", "runway", "team_size", "pending_hires",
             "morale", "market_confidence", "customers", "revenue")}
