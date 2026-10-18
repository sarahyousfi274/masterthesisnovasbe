"""The situation that travels through the game.

Only the chosen options change it, through the effect table in content.py and
the fixed rules below. Reference values and measurement results never touch it.

Economics
- Revenue follows the number of customers (about €89 per customer per month).
- Net burn = monthly costs − monthly revenue. Runway = cash / net burn.

Fixed rules, applied at the end of each area (end_of_area)
- One month of net burn is paid.
- Team area only: everyone hired in this area starts. Open roles from H1 and a
  Head of Sales from H4 join the team and add their monthly cost. One to three
  new people lift morale (+1, help arrives); four or more at once lower it
  (−1, onboarding strain, as in the walkthrough).
- If runway falls below SHORT_RUNWAY_MONTHS, the team feels it (morale −1).

Finance
- F1 stores the months until fundraising starts. When the money from F4
  arrives, the net burn for those months is paid first, so starting late has a
  visible cost. When the round closes is never shown.

Every change is returned as an event so the report can say where each number
came from.
"""

from __future__ import annotations

import copy

from . import content

TRACKED = ("cash", "burn", "revenue", "customers", "team_size", "pending_hires",
           "ownership", "morale", "market_confidence")
SCALE_KEYS = ("morale", "market_confidence")


# ---------------------------------------------------------------------------
# Derived values
# ---------------------------------------------------------------------------

def revenue(state: dict) -> int:
    return int(round(state["customers"] * content.REVENUE_PER_CUSTOMER, -2))


def burn(state: dict) -> int:
    return max(0, state["costs"] - revenue(state))


def runway(state: dict) -> int:
    b = burn(state)
    return 99 if b <= 0 else max(0, int(state["cash"] // b))


def refresh(state: dict) -> dict:
    state["revenue"] = revenue(state)
    state["burn"] = burn(state)
    state["runway"] = runway(state)
    return state


def new_state(solo: bool) -> dict:
    state = copy.deepcopy(content.START_STATE)
    if solo:
        state["team_size"] = 1
    return refresh(state)


def launch_budget(state: dict) -> int:
    """A quarter of cash, rounded to the nearest 100."""
    return int(round(state["cash"] * 0.25, -2))


# ---------------------------------------------------------------------------
# Applying a decision
# ---------------------------------------------------------------------------

def apply(state: dict, effects: dict) -> dict:
    """Return a new state with `effects` applied."""
    new = copy.deepcopy(state)

    spend = effects.get("spend_launch_budget")
    if spend:
        new["cash"] -= launch_budget(state) if spend is True else int(spend)

    if "raise" in effects:
        # Running costs until the round starts are paid first (F1).
        delay = new.get("fundraise_delay", 0)
        new["cash"] -= delay * burn(new)
        new["cash"] += effects["raise"]

    for key, delta in effects.items():
        if key in ("spend_launch_budget", "raise"):
            continue
        if key in SCALE_KEYS:
            new[key] = max(1, min(5, new[key] + delta))
        elif key in ("pending_hires", "fundraise_delay"):
            new[key] = delta                       # a plan, not an increment
        elif key == "pending_hires_extra":
            new["pending_extra"] = new.get("pending_extra", 0) + delta
        elif key == "pending_cost_extra":
            new["pending_cost"] = new.get("pending_cost", 0) + delta
        elif key == "ownership":
            new["ownership"] = max(0, new["ownership"] + delta)
        else:
            new[key] = new.get(key, 0) + delta

    new["cash"] = max(0, new["cash"])
    new["costs"] = max(0, new["costs"])
    new["team_size"] = max(1, new["team_size"])
    new["customers"] = max(0, new["customers"])
    return refresh(new)


def delay_cost(state: dict) -> int:
    """Net burn paid between F1 and the start of the round."""
    return state.get("fundraise_delay", 0) * burn(state)


# ---------------------------------------------------------------------------
# End of an area
# ---------------------------------------------------------------------------

def end_of_area(state: dict, domain: str) -> tuple[dict, list[dict]]:
    """Apply the fixed end-of-area rules. Returns the new state and a list of
    events, each {"label": str, "delta": dict}."""
    events: list[dict] = []
    s = copy.deepcopy(state)

    if domain == "hiring":
        joining = s.get("pending_hires", 0) + s.get("pending_extra", 0)
        if joining:
            before = copy.deepcopy(s)
            s["team_size"] += joining
            s["costs"] += s.get("pending_hires", 0) * content.COST_PER_HIRE
            s["costs"] += s.get("pending_cost", 0)
            s["pending_hires"] = 0
            s["pending_extra"] = 0
            s["pending_cost"] = 0
            if joining >= 4:
                s["morale"] = max(1, s["morale"] - 1)
            else:
                s["morale"] = min(5, s["morale"] + 1)
            refresh(s)
            word = "person" if joining == 1 else "people"
            events.append({"label": f"New team members start ({joining} {word})",
                           "delta": diff(before, s)})

    before = copy.deepcopy(s)
    s["cash"] = max(0, s["cash"] - burn(s))
    refresh(s)
    events.append({"label": "One month of running costs", "delta": diff(before, s)})

    if s["runway"] < content.SHORT_RUNWAY_MONTHS and s["morale"] > 1:
        before = copy.deepcopy(s)
        s["morale"] -= 1
        events.append({"label": "Short runway weighs on the team",
                       "delta": diff(before, s)})

    return refresh(s), events


# Kept for the simulated-participant test and older callers.
def advance_block(state: dict, domain: str = "") -> dict:
    return end_of_area(state, domain)[0]


def contest_effects(cost: int) -> dict:
    return {"cash": -cost} if cost else {}


def diff(before: dict, after: dict) -> dict:
    out = {}
    for key in TRACKED:
        d = (after.get(key) or 0) - (before.get(key) or 0)
        if d:
            out[key] = d
    return out


def snapshot(state: dict) -> dict:
    """Logged with every answer and used as a control variable
    (Chen, Croson, Elfenbein and Posen 2018). Always the current state."""
    return {k: state.get(k) for k in
            ("cash", "costs", "revenue", "burn", "runway", "team_size",
             "pending_hires", "ownership", "morale", "market_confidence",
             "customers", "fundraise_delay")}


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def money(value: float) -> str:
    sign = "−" if value < 0 else ""
    return f"{sign}€{abs(value):,.0f}"


def format_value(key: str, state: dict) -> str:
    v = state.get(key, 0) or 0
    if key in ("cash", "burn", "revenue"):
        return money(v)
    if key == "runway":
        return "8+ years" if v >= 99 else f"{v} months"
    if key == "team_size":
        return f"{v} " + ("person" if v == 1 else "people")
    if key == "pending_hires":
        return f"{v} " + ("role" if v == 1 else "roles")
    if key == "ownership":
        return f"{v}%"
    if key in SCALE_KEYS:
        return f"{v} / 5"
    return f"{v:,.0f}"


def format_delta(key: str, d: float) -> str:
    sign = "+" if d > 0 else "−"
    a = abs(d)
    if key in ("cash", "burn", "revenue"):
        return f"{sign}€{a:,.0f}"
    if key == "runway":
        return f"{sign}{a:.0f} mo"
    if key == "ownership":
        return f"{sign}{a:.0f} pts"
    return f"{sign}{a:,.0f}"
