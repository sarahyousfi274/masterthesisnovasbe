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

No outcome feedback before the end (review of 20 October, A9)
- Customers, morale and market confidence say how well a choice worked.
  Changes to them are held back in state["deferred"] and applied in one step
  by settle(), in the final report after K1. During the session revenue stays
  at its starting value, so net burn and runway change only through costs.
- Money spent or raised, ownership given up, monthly costs and people joining
  are known at the moment of the decision and are applied at once.

Finance
- F1 stores the runway left when the round starts (fundraise_left). No running
  costs are charged for the waiting time: each month's burn is already paid at
  the end of each area. A start with fewer than 6 months left closes on worse
  terms, applied in the final report: €15,000 bridge fee on the loan, or 2
  extra ownership points on the SAFE or the priced round.

Every change is returned as an event so the report can say where each number
came from.
"""

from __future__ import annotations

import copy

from . import content

TRACKED = ("cash", "burn", "revenue", "customers", "team_size", "pending_hires",
           "ownership", "morale", "market_confidence")
SCALE_KEYS = ("morale", "market_confidence")
DEFERRED_KEYS = ("customers", "morale", "market_confidence")   # shown only at the end
SET_KEYS = ("pending_hires", "fundraise_left", "f4_route")      # a plan, not an increment
LATE_START_MONTHS = 6
LATE_FEE_LOAN = 15_000
LATE_OWNERSHIP = 2


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

def apply(state: dict, effects: dict, label: str | None = None) -> dict:
    """Return a new state with `effects` applied. Customer, morale and market
    confidence effects are held back (see DEFERRED_KEYS) under `label`."""
    new = copy.deepcopy(state)
    new.setdefault("deferred", [])

    spend = effects.get("spend_launch_budget")
    if spend:
        new["cash"] -= launch_budget(state) if spend is True else int(spend)

    if "raise" in effects:
        new["cash"] += effects["raise"]

    held = {k: v for k, v in effects.items() if k in DEFERRED_KEYS and v}
    if held:
        new["deferred"] = new["deferred"] + [{"label": label or "Other", "delta": held}]

    for key, delta in effects.items():
        if key in ("spend_launch_budget", "raise") or key in DEFERRED_KEYS:
            continue
        if key in SET_KEYS:
            new[key] = delta
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
    """No longer charged (review A3): each month's burn is paid at the end of
    each area, so waiting costs nothing extra. Kept so older callers still work."""
    return 0


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
            refresh(s)
            word = "person" if joining == 1 else "people"
            label = f"New team members start ({joining} {word})"
            events.append({"label": label, "delta": diff(before, s)})
            s.setdefault("deferred", []).append(
                {"label": label, "delta": {"morale": -1 if joining >= 4 else 1}})

    before = copy.deepcopy(s)
    s["cash"] = max(0, s["cash"] - burn(s))
    refresh(s)
    events.append({"label": "One month of running costs", "delta": diff(before, s)})

    if s["runway"] < content.SHORT_RUNWAY_MONTHS:
        s.setdefault("deferred", []).append(
            {"label": "Short runway weighs on morale", "delta": {"morale": -1}})

    return refresh(s), events


def settle(state: dict) -> tuple[dict, list[dict]]:
    """Final report: apply everything held back during the session, plus the
    terms of a late fundraising start. Returns the new state and its events."""
    s = copy.deepcopy(state)
    events: list[dict] = []
    for entry in s.get("deferred", []):
        before = copy.deepcopy(s)
        for key, delta in entry["delta"].items():
            if key in SCALE_KEYS:
                s[key] = max(1, min(5, s[key] + delta))
            else:
                s[key] = max(0, s.get(key, 0) + delta)
        refresh(s)
        d = diff(before, s)
        if d:
            events.append({"label": entry["label"], "delta": d})
    s["deferred"] = []

    left, route = s.get("fundraise_left"), s.get("f4_route")
    if left is not None and route and left < LATE_START_MONTHS:
        before = copy.deepcopy(s)
        if route == "loan":
            s["cash"] = max(0, s["cash"] - LATE_FEE_LOAN)
            label = "Late fundraising start: bridge fee on the loan"
        else:
            s["ownership"] = max(0, s["ownership"] - LATE_OWNERSHIP)
            label = "Late fundraising start: the round closed on worse terms"
        refresh(s)
        events.append({"label": label, "delta": diff(before, s)})
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
             "customers", "fundraise_left")}


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
