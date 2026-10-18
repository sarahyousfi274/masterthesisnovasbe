"""Founder decision simulation.

Run with:  streamlit run app.py

The session never names confidence, calibration or overconfidence. Reference
values live only in the backend and are never shown. The full explanation of
the study is sent with the follow-up a week later.
"""

from __future__ import annotations

import copy
import random
import re
import time
from datetime import datetime, timezone

import streamlit as st

from sim import codebook, content, flow, state as game, storage, ui

st.set_page_config(page_title="Decisions in founding", page_icon="◆",
                   layout="centered", initial_sidebar_state="collapsed")
ui.inject_css()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def init() -> None:
    if "code" in st.session_state:
        return
    seed = random.randrange(1, 2**31 - 1)
    rng = random.Random(seed)
    ss = st.session_state
    ss.seed = seed
    ss.track = flow.assign_track(rng)
    ss.code = flow.make_code(rng)
    ss.screens = flow.build(ss.track, seed)
    ss.sections = flow.sections(ss.screens)
    ss.index = 0
    ss.solo = False
    ss.state = game.new_state(solo=False)
    ss.screen_entered = time.monotonic()
    ss.screen_entered_at = _now()
    ss.answers = {}            # screen id -> values, to pre-fill after Back
    ss.events = []             # what changed the numbers, per area
    ss.block_start = {}        # area -> situation when the area began
    ss.closed = set()          # areas whose month of burn has been paid
    ss.completed = False


init()
ss = st.session_state

# Local design review only: FS_DEV=1 streamlit run app.py, then ?jump=<screen id>.
# Never active on a deployment unless that environment variable is set there.
import os  # noqa: E402
if os.environ.get("FS_DEV") == "1" and st.query_params.get("jump") and not ss.get("jumped"):
    target = st.query_params.get("jump")
    ids = [s["id"] for s in ss.screens]
    if target in ids:
        ss.index = ids.index(target)
        ss.startup_name = "Northwind"
        ss.jumped = True
        if target.startswith("report_"):
            dom = target.split("_", 1)[1]
            ss.block_start[dom] = copy.deepcopy(ss.state)
            ss.state = game.apply(ss.state, {"cash": -12_000})
            ss.events.append({"domain": dom, "label": "MVP development: About half "
                              "to external developers", "delta": {"cash": -12_000}})


def screen() -> dict:
    return ss.screens[ss.index]


def elapsed() -> float:
    return round(time.monotonic() - ss.screen_entered, 3)


def advance() -> None:
    ss.index += 1
    ss.screen_entered = time.monotonic()
    ss.screen_entered_at = _now()
    st.rerun()


def go_back() -> None:
    ss.index -= 1
    ss.screen_entered = time.monotonic()
    ss.screen_entered_at = _now()
    st.rerun()


def area_start() -> dict:
    """The situation at the start of the current area. It is what the status
    strip and the numbers inside the questions show, so the display never
    moves with the decisions inside an area."""
    return ss.block_start.get(screen().get("domain"), ss.state)


def log(screen_override: dict | None = None, **kwargs) -> None:
    sc = screen_override or screen()
    snap = game.snapshot(ss.state)
    if sc.get("domain"):
        snap["runway_shown"] = area_start()["runway"]
    storage.save_response(ss.code, sc, ss.index, response_seconds=kwargs.pop(
        "response_seconds", elapsed()), state=snap, entered_at=ss.screen_entered_at,
        **kwargs)


def remember(**values) -> None:
    ss.answers[screen()["id"]] = values


def recalled(key: str, default=None):
    return ss.answers.get(screen()["id"], {}).get(key, default)


def apply_effects(effects: dict, label: str | None) -> None:
    before = ss.state
    ss.state = game.apply(ss.state, effects)
    delta = game.diff(before, ss.state)
    if label and delta:
        ss.events.append({"domain": screen().get("domain"), "label": label,
                          "delta": delta})


def fill(text: str) -> str:
    s = area_start()
    return text.format(runway=s["runway"],
                       launch_budget=game.money(game.launch_budget(s)))


def money(v: float) -> str:
    return game.money(v)


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

def frame() -> None:
    """Section bar, progress and, where allowed, the Back button."""
    sc = screen()
    ui.steps(ss.sections, sc.get("section"), ss.index / (len(ss.screens) - 1))
    if flow.back_allowed(ss.screens, ss.index):
        if st.button("← Back", key=f"back_{sc['id']}", type="tertiary"):
            go_back()


def scenario(spec: dict) -> None:
    if not spec.get("scenario"):
        return
    with st.popover("ⓘ  About this scenario"):
        st.markdown(spec["scenario"])
        if spec.get("sources"):
            st.markdown("**Data behind the scenario**")
            for src in spec["sources"]:
                st.markdown(f"- {src}")


def continue_button(key: str, label: str = "Continue") -> bool:
    return st.button(label, type="primary", key=key)


# ---------------------------------------------------------------------------
# Welcome
# ---------------------------------------------------------------------------

def render_consent(sc: dict) -> None:
    ui.eyebrow("Research study")
    st.title(content.CONSENT["title"])
    ui.html_block(f'<div class="fs-hero"><div class="lead">{content.CONSENT["lead"]}'
                  '</div></div>')
    ui.facts(content.CONSENT["facts"])
    ui.terms(content.CONSENT["sections"])
    c1, c2 = st.columns([1.3, 1])
    if c1.button(content.CONSENT["agree"], type="primary", key="consent_agree",
                 use_container_width=True):
        storage.start_session(ss.code, ss.track, ss.seed, content.APP_VERSION,
                              codebook.version())
        storage.update_session(ss.code, consent=1)
        log(option_key="agree")
        advance()
    if c2.button(content.CONSENT["decline"], key="consent_decline",
                 use_container_width=True):
        ss.declined = True
        st.rerun()


# ---------------------------------------------------------------------------
# About you
# ---------------------------------------------------------------------------

def about_header() -> None:
    ui.note(content.ABOUT_NOTE)


def render_filter(sc: dict) -> None:
    frame()
    about_header()
    ui.question(content.FILTER["question"], content.FILTER["help"])
    opts = content.FILTER["options"]
    saved = recalled("choice")
    choice = st.radio("Answer", opts, index=opts.index(saved) if saved in opts else None,
                      label_visibility="collapsed", key="filter_choice")
    if continue_button("filter_continue"):
        if choice is None:
            st.warning("Please choose Yes or No.")
            return
        remember(choice=choice)
        storage.update_session(ss.code, is_founder=int(choice == "Yes"))
        log(option_key=choice)
        if choice != "Yes":
            storage.delete(ss.code)      # the end screen promises nothing is kept
            ss.not_founder = True
            st.rerun()
        advance()


def render_email(sc: dict) -> None:
    frame()
    about_header()
    ui.question(content.EMAIL["question"], content.EMAIL["body"])
    with st.form("email_form", border=False):
        email = st.text_input(content.EMAIL["label"], value=recalled("email", ""),
                              placeholder=content.EMAIL["placeholder"],
                              key="email_value")
        submitted = st.form_submit_button("Continue", type="primary")
    if submitted:
        email = (email or "").strip().lower()
        if not EMAIL_RE.match(email):
            st.warning("Please enter a valid email address.")
            return
        remember(email=email)
        storage.save_followup(ss.code, email)
        log(option_key="provided")      # the address itself is never in responses
        advance()


def _profile_widget(field: dict):
    key, label, kind = field["key"], field["label"], field["kind"]
    saved = recalled(key)
    wkey = f"profile_{key}"
    if kind == "number":
        return st.number_input(label, min_value=field["min"], max_value=field["max"],
                               step=1, value=saved, key=wkey, placeholder="Type a number")
    if kind == "select":
        opts = field["options"]
        return st.selectbox(label, opts, index=opts.index(saved) if saved in opts else None,
                            placeholder="Select", key=wkey)
    if kind == "pills":
        return st.pills(label, field["options"], default=saved, key=wkey)
    if kind == "multi":
        return st.pills(label, field["options"], selection_mode="multi",
                        default=saved or [], key=wkey)
    return st.text_input(label, value=saved or "", key=wkey)


def render_profile(sc: dict) -> None:
    frame()
    about_header()
    ui.question(content.PROFILE["question"], content.PROFILE["body"])
    values: dict = {}
    with st.form("profile_form", border=False):
        fields = content.PROFILE_FIELDS
        i = 0
        while i < len(fields):
            f = fields[i]
            nxt = fields[i + 1] if i + 1 < len(fields) else None
            if "col" in f and nxt is not None and "col" in nxt:
                c1, c2 = st.columns(2)
                with c1:
                    values[f["key"]] = _profile_widget(f)
                with c2:
                    values[nxt["key"]] = _profile_widget(nxt)
                i += 2
            else:
                values[f["key"]] = _profile_widget(f)
                i += 1
        submitted = st.form_submit_button("Continue", type="primary")
    if submitted:
        missing = [f["label"] for f in content.PROFILE_FIELDS
                   if values.get(f["key"]) in (None, "", [])]
        if missing:
            st.warning("Please answer every question. Still open: "
                       + "; ".join(m.split(" (")[0] for m in missing) + ".")
            return
        remember(**values)
        log(text_value="; ".join(
            f"{k}={'|'.join(v) if isinstance(v, list) else v}" for k, v in values.items()))
        advance()


def render_experience(sc: dict) -> None:
    frame()
    about_header()
    ui.question(content.EXPERIENCE["question"], content.EXPERIENCE["body"])
    values = {}
    with st.form("experience_form", border=False):
        for field in content.EXPERIENCE_FIELDS:
            values[field["key"]] = st.pills(
                field["label"], content.EXPERIENCE_OPTIONS,
                default=recalled(field["key"]), key=f"exp_{field['key']}")
        submitted = st.form_submit_button("Continue", type="primary")
    if submitted:
        if any(v is None for v in values.values()):
            st.warning("Please answer each of the four questions.")
            return
        remember(**values)
        log(text_value="; ".join(f"{k}={v}" for k, v in values.items()))
        advance()


def render_risk(sc: dict) -> None:
    frame()
    about_header()
    ui.question(content.RISK["question"], content.RISK["body"])
    scale = [str(i) for i in range(11)]
    values = {}
    with st.form("risk_form", border=False):
        for item in content.RISK_ITEMS:
            st.markdown(f"**{item['label']}**")
            values[item["key"]] = st.pills(
                item["label"], scale, default=recalled(item["key"]),
                label_visibility="collapsed", key=f"risk_{item['key']}")
            ui.html_block(
                '<div style="display:flex;justify-content:space-between;'
                'font-size:0.78rem;color:#6B7280;margin:-0.4rem 0 1.1rem 0;max-width:34rem">'
                f'<span>0 = {item["low"]}</span><span>10 = {item["high"]}</span></div>')
        submitted = st.form_submit_button("Continue", type="primary")
    if submitted:
        if any(v is None for v in values.values()):
            st.warning("Please answer each of the three questions.")
            return
        remember(**values)
        log(text_value="; ".join(f"{k}={v}" for k, v in values.items()))
        advance()


# ---------------------------------------------------------------------------
# How it works
# ---------------------------------------------------------------------------

def render_warmup_intro(sc: dict) -> None:
    frame()
    st.subheader(content.WARMUP_INTRO["title"])
    ui.points(content.WARMUP_INTRO["points"])
    st.caption(content.WARMUP_INTRO["footer"])
    if continue_button("warmup_continue"):
        log(option_key="seen")
        advance()


def render_practice_choice(sc: dict) -> None:
    frame()
    ui.eyebrow(content.PRACTICE_CHOICE["tag"], muted=True)
    ui.question(content.PRACTICE_CHOICE["question"])
    opts = content.PRACTICE_CHOICE["options"]
    choice = st.radio("Order", opts, index=None, label_visibility="collapsed",
                      key="practice_choice_value")
    if continue_button("practice_choice_continue"):
        if choice is None:
            st.warning("Please pick one.")
            return
        log(text_value=choice)
        advance()


def render_practice_range(sc: dict) -> None:
    frame()
    spec = content.PRACTICE_RANGE
    ui.eyebrow(spec["tag"], muted=True)
    ui.question(spec["question"], spec["intro"])
    ui.range_diagram("lower", "higher")
    c1, c2 = st.columns(2)
    with c1:
        low = st.number_input(spec["low_label"], min_value=0, max_value=5000, step=1,
                              value=None, key="practice_low", placeholder=spec["unit"])
        st.caption(spec["low_help"])
    with c2:
        high = st.number_input(spec["high_label"], min_value=0, max_value=5000, step=1,
                               value=None, key="practice_high", placeholder=spec["unit"])
        st.caption(spec["high_help"])
    if continue_button("practice_range_continue"):
        if low is None or high is None:
            st.warning("Please enter both numbers.")
            return
        if low > high:
            st.warning("Your low estimate is higher than your high estimate. "
                       "Please check the two numbers.")
            return
        log(numeric_value=float(low), text_value=f"{low}-{high}")
        advance()


# ---------------------------------------------------------------------------
# Your startup
# ---------------------------------------------------------------------------

def render_setup(sc: dict) -> None:
    frame()
    ui.question(content.SETUP["question"], content.SETUP["body"])
    with st.form("setup_form", border=False):
        name = st.text_input(content.SETUP["name_label"],
                             placeholder=content.SETUP["name_placeholder"])
        industry = st.selectbox(content.SETUP["industry_label"], content.INDUSTRIES,
                                index=None, placeholder="Select")
        solo = st.radio(content.SETUP["solo_label"], content.SETUP["solo_options"],
                        index=None, horizontal=True)
        submitted = st.form_submit_button("Continue", type="primary")
    if submitted:
        missing = []
        if not (name or "").strip():
            missing.append("a name")
        if industry is None:
            missing.append("the industry")
        if solo is None:
            missing.append("alone or with co-founders")
        if missing:
            st.warning("Please fill in " + ", ".join(missing) + ".")
            return
        ss.solo = solo == "Alone"
        ss.state = game.new_state(solo=ss.solo)
        ss.startup_name = name.strip()
        storage.update_session(ss.code, solo=int(ss.solo), startup_name=name.strip(),
                               industry=industry)
        log(text_value=f"{name.strip()} | {industry} | {solo}")
        advance()


def render_starting_situation(sc: dict) -> None:
    frame()
    st.subheader(content.STARTING_SITUATION["title"])
    st.markdown(content.STARTING_SITUATION["body"])
    ui.status_cards(ss.state)
    if continue_button("starting_continue", content.STARTING_SITUATION["button"]):
        log(option_key="seen")
        advance()


# ---------------------------------------------------------------------------
# The four areas
# ---------------------------------------------------------------------------

def render_block_intro(sc: dict) -> None:
    frame()
    domain = sc["domain"]
    block = content.BLOCKS[domain]
    if domain not in ss.block_start:
        ss.block_start[domain] = copy.deepcopy(ss.state)
    n = content.TRACKS[ss.track].index(domain) + 1
    ui.eyebrow(f"Area {n} of 4")
    st.subheader(block["title"])
    st.markdown(block.get("intro_solo") if ss.solo and "intro_solo" in block
                else block["intro"])
    st.markdown("**Where you start this area**")
    ui.status_cards(ss.state)
    if continue_button(f"intro_{domain}_continue"):
        advance()


def _option_label(opt: dict, cost_override: int | None = None) -> str:
    label = opt.get("label_solo") if ss.solo and "label_solo" in opt else opt["label"]
    cost = cost_override if cost_override is not None else opt.get("cost")
    if cost is not None:
        label += f"  ·  {money(cost)}" if cost else "  ·  no cash cost"
    if opt.get("extra"):
        label += f"  ·  {opt['extra']}"
    return label


def render_choice(sc: dict) -> None:
    frame()
    node_id = sc["node"]
    spec = content.SCREENS[node_id]
    ui.hud(area_start())
    q = spec.get("question_solo") if ss.solo and "question_solo" in spec else spec["question"]
    ui.question(fill(q), fill(spec["body"]) if spec.get("body") else None)
    scenario(spec)

    labels = [_option_label(o) for o in spec["options"]]
    if spec.get("display") == "pills":
        choice = st.pills("Options", labels, label_visibility="collapsed",
                          key=f"choice_{node_id}")
    else:
        choice = st.radio("Options", labels, index=None, label_visibility="collapsed",
                          key=f"choice_{node_id}")
    if continue_button(f"choice_{node_id}_continue"):
        if choice is None:
            st.warning("Please choose one of the options.")
            return
        idx = labels.index(choice)
        opt = spec["options"][idx]
        log(option_key=opt["key"], option_index=idx)
        event = f'{spec["event"]}: {opt["label"]}' if spec.get("event") else None
        effects = dict(opt.get("effects", {}))
        if effects.get("spend_launch_budget") is True:
            effects["spend_launch_budget"] = game.launch_budget(area_start())
        apply_effects(effects, event)
        advance()


def render_multi(sc: dict) -> None:
    frame()
    node_id = sc["node"]
    spec = content.SCREENS[node_id]
    ui.hud(area_start())
    ui.question(spec["question"], spec.get("body"))
    labels = [o["label"] for o in spec["options"]]
    picked = st.pills("Options", labels, selection_mode="multi",
                      label_visibility="collapsed", key=f"multi_{node_id}")
    if continue_button(f"multi_{node_id}_continue"):
        if not picked:
            st.warning("Please select at least one option.")
            return
        keys = sorted(spec["options"][labels.index(p)]["key"] for p in picked)
        log(option_key=",".join(keys))
        advance()


def render_contest(sc: dict) -> None:
    frame()
    node_id = sc["node"]
    spec = content.SCREENS[node_id]
    params = codebook.contest_params(node_id)
    ui.hud(area_start())
    ui.question(spec["question"].format(prize=money(params["prize"])),
                spec["body"].format(prize=money(params["prize"]),
                                    base_cost=money(params["base_cost"])))
    scenario(spec)
    labels = []
    for opt in spec["options"]:
        cost = params["options"][opt["key"]]["cost"]
        labels.append(_option_label(opt, cost_override=cost if cost else None))
    choice = st.radio("Options", labels, index=None, label_visibility="collapsed",
                      key=f"contest_{node_id}")
    if continue_button(f"contest_{node_id}_continue"):
        if choice is None:
            st.warning("Please choose one of the options.")
            return
        idx = labels.index(choice)
        key = spec["options"][idx]["key"]
        log(option_key=key, option_index=idx)
        cost = params["options"][key]["cost"]
        apply_effects(game.contest_effects(cost),
                      f'{spec["event"]}: {spec["options"][idx]["label"]}' if cost else None)
        advance()


def _interval_input(spec: dict, which: str, node_id: str):
    unit = spec["unit"]
    more = spec["optimistic_is_high"] == (which == "best")
    label = f'{spec[f"{which}_label"]} ({"more" if more else "fewer"} {unit})'
    is_money = spec["unit"] == "euros"
    val = st.number_input(label, min_value=int(spec["min_value"]),
                          max_value=int(spec["max_value"]), step=int(spec["step"]),
                          value=None, key=f"interval_{node_id}_{which}",
                          placeholder="€" if is_money else spec["unit"])
    st.caption(spec[f"{which}_help"])
    if is_money and val is not None:
        ui.html_block(f'<div class="fs-echo">{money(val)} per month</div>')
    return val


def render_interval(sc: dict) -> None:
    frame()
    node_id = sc["node"]
    spec = content.SCREENS[node_id]
    ui.hud(area_start())
    if spec.get("chart") == "revenue":
        ui.bar_chart(content.CHART_REVENUE, money, "Monthly revenue so far",
                     "In 12 months")
    elif spec.get("chart") == "customers":
        ui.bar_chart(content.CHART_CUSTOMERS, lambda v: f"{v:,.0f}",
                     "New paying customers from the channel", "Next 6 months")
    ui.question(fill(spec["question"]),
                "Give two numbers, a best case and a worst case, so that you are "
                "fairly sure the real value lies between them.")
    scenario(spec)
    high_is_best = spec["optimistic_is_high"]
    unit = spec["unit"]
    ui.range_diagram(f"fewer {unit}", f"more {unit}")

    order = ["best", "worst"] if sc.get("first", "best") == "best" else ["worst", "best"]
    cols = st.columns(2)
    vals = {}
    for col, which in zip(cols, order):
        with col:
            vals[which] = _interval_input(spec, which, node_id)

    if continue_button(f"interval_{node_id}_continue"):
        best, worst = vals["best"], vals["worst"]
        if best is None or worst is None:
            st.warning("Please enter both numbers.")
            return
        if (high_is_best and best < worst) or (not high_is_best and best > worst):
            st.warning("Your best case is worse than your worst case. "
                       "Please check the two numbers.")
            return
        t = elapsed()
        log({**sc, "id": f"{node_id}_opt"}, numeric_value=float(best),
            text_value=f"first={order[0]}", response_seconds=t)
        log({**sc, "id": f"{node_id}_pes"}, numeric_value=float(worst),
            text_value=f"first={order[0]}", response_seconds=0.0)
        advance()


def render_report(sc: dict) -> None:
    frame()
    domain = sc["domain"]
    if domain not in ss.closed:
        before = ss.state
        ss.state = game.advance_block(ss.state)
        ss.events.append({"domain": domain, "label": "One month of running costs",
                          "delta": game.diff(before, ss.state)})
        ss.closed.add(domain)
    block = content.BLOCKS[domain]
    ui.eyebrow(f"Area {content.TRACKS[ss.track].index(domain) + 1} of 4 complete")
    st.subheader("Where things stand")
    ui.status_cards(ss.state, before=ss.block_start.get(domain))
    st.markdown("**What changed in this area**")
    ui.changes([e for e in ss.events if e["domain"] == domain])
    if continue_button(f"report_{domain}_continue"):
        log(option_key="seen")
        advance()


# ---------------------------------------------------------------------------
# Wrap-up
# ---------------------------------------------------------------------------

def render_suspicion(sc: dict) -> None:
    frame()
    ui.eyebrow(content.SUSPICION["lead"], muted=True)
    st.subheader(content.SUSPICION["title"])
    ui.question(content.SUSPICION["question"], content.SUSPICION["body"])
    with st.form("suspicion_form", border=False):
        answer = st.text_area("Your answer", height=140, label_visibility="collapsed")
        submitted = st.form_submit_button("Finish", type="primary")
    if submitted:
        if not (answer or "").strip():
            st.warning("Please write a short answer. One sentence is enough.")
            return
        log(text_value=answer.strip())
        advance()


def render_end(sc: dict) -> None:
    if not ss.completed:
        storage.complete_session(ss.code)
        ss.completed = True
    ui.steps(ss.sections, sc.get("section"), 1.0)
    st.title(content.END["title"])
    st.markdown(content.END["body"])


RENDERERS = {
    "consent": render_consent, "filter": render_filter, "email": render_email,
    "profile": render_profile, "experience": render_experience, "risk": render_risk,
    "warmup_intro": render_warmup_intro, "practice_choice": render_practice_choice,
    "practice_range": render_practice_range, "setup": render_setup,
    "starting_situation": render_starting_situation, "block_intro": render_block_intro,
    "choice": render_choice, "multi": render_multi, "contest": render_contest,
    "interval": render_interval, "report": render_report,
    "suspicion": render_suspicion, "end": render_end,
}

# ---------------------------------------------------------------------------

if st.query_params.get("view") == "admin":
    from sim import admin
    admin.render()
elif ss.get("declined"):
    st.title(content.CONSENT["title"])
    st.markdown(content.DECLINED)
elif ss.get("not_founder"):
    st.title(content.CONSENT["title"])
    st.markdown(content.THANK_YOU_NOT_FOUNDER)
else:
    sc = screen()
    RENDERERS[sc["kind"]](sc)
