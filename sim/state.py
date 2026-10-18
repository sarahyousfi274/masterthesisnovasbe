"""The situation that travels through the game.

Only the chosen options change it, through the effect table in content.py.
Reference values and measurement results never touch it.

At the end of each area one month of running costs (the burn) is deducted, so
runway visibly shrinks and fundraising timing has a consequence. Roles opened
in H1 stay open roles; only an actual hire (H4) adds to the team.

Every change is also recorded as an event, so the report at the end of an
area can say exactly where each number came from.
"""

from __future__ import annotations

import copy

from . import content

TRACKED = ("cash", "burn", "runway", "team_size", "pending_hires", "customers",
           "morale", "market_confidence")


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
    """G1 spends a quarter of current cash, rounded to the nearest 100."""
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
            new["pending_hires"] = delta      # H1 sets the plan
        else:
            new[key] = new.get(key, 0) + delta

    new["cash"] = max(0, new["cash"])
    new["burn"] = max(0, new["burn"])
    new["team_size"] = max(1, new["team_size"])
    new["customers"] = max(0, new["customers"])
    new["runway"] = runway(new)
    return new


def advance_block(state: dict) -> dict:
    """End of an area: one month of running costs is paid."""
    new = copy.deepcopy(state)
    new["cash"] = max(0, new["cash"] - new["burn"])
    new["runway"] = runway(new)
    return new


def contest_effects(cost: int) -> dict:
    return {"cash": -cost} if cost else {}


def diff(before: dict, after: dict) -> dict:
    """Changed tracked fields, as after minus before."""
    out = {}
    for key in TRACKED:
        if key == "runway":
            continue
        d = (after.get(key) or 0) - (before.get(key) or 0)
        if d:
            out[key] = d
    return out


def snapshot(state: dict) -> dict:
    """Logged with every answer and used as a control variable
    (Chen, Croson, Elfenbein and Posen 2018)."""
    return {k: state.get(k) for k in
            ("cash", "burn", "runway", "team_size", "pending_hires",
             "morale", "market_confidence", "customers", "revenue")}


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def money(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}€{abs(value):,.0f}"


def format_value(key: str, state: dict) -> str:
    v = state.get(key, 0) or 0
    if key in ("cash", "burn"):
        return money(v)
    if key == "runway":
        return "8+ years" if v >= 99 else f"{v} months"
    if key == "team_size":
        return f"{v} " + ("person" if v == 1 else "people")
    if key == "pending_hires":
        return f"{v} " + ("role" if v == 1 else "roles")
    if key in ("morale", "market_confidence"):
        return f"{v} / 5"
    return f"{v:,.0f}"


def format_delta(key: str, d: float) -> str:
    sign = "+" if d > 0 else "−"
    a = abs(d)
    if key in ("cash", "burn"):
        return f"{sign}€{a:,.0f}"
    if key == "runway":
        return f"{sign}{a:.0f} mo"
    return f"{sign}{a:,.0f}"
