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

from pathlib import Path  # noqa: E402

_ICON = Path(__file__).parent / "assets" / "favicon.png"
st.set_page_config(page_title="Decisions in founding",
                   page_icon=str(_ICON) if _ICON.exists() else "◆",
                   layout="centered", initial_sidebar_state="collapsed")
ui.inject_css()

# app.py and the files in sim/ must come from the same release. A mixed upload
# (for example a new app.py with an old sim/content.py) stops here with a clear
# message instead of failing halfway through a session.
APP_RELEASE = "0.9.0"
if getattr(content, "APP_VERSION", None) != APP_RELEASE:
    st.error(
        f"Version mismatch: app.py is {APP_RELEASE}, sim/content.py is "
        f"{getattr(content, 'APP_VERSION', 'unknown')}. Upload all files of the same "
        "release (app.py and every file in sim/), then reboot the app.")
    st.stop()

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
    ss.journey = []            # every decision, for the timeline at the end
    ss.product = None          # what Lumora does, from the industry
    ss.block_start = {}        # area -> situation when the area began
    ss.closed = set()          # areas whose month of burn has been paid
    ss.completed = False
    ss.startup_name = content.STARTUP_NAME


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
        ss.industry_label = "software"
        ss.product = content.INDUSTRY_PRODUCTS["Software and SaaS"]
        ss.solo = st.query_params.get("solo") == "1"
        ss.state = game.new_state(solo=ss.solo)
        ss.jumped = True
        if target == "end":
            ss.journey = [
                {"id": "T1", "domain": "team", "event": "MVP development",
                 "choice": "About half to external developers"},
                {"id": "T2", "domain": "team", "event": "Pitch contest", "choice": "Take part"},
                {"id": "F1", "domain": "finance", "event": "Fundraising starts",
                 "choice": "In 3 months"},
                {"id": "K1", "domain": "final", "event": "Grant raffle",
                 "choice": "Do not enter"}]
        if target.startswith("report_"):
            dom = target.split("_", 1)[1]
            ss.block_start[dom] = copy.deepcopy(ss.state)
            ss.state = game.apply(ss.state, {"cash": -12_000})
            ss.events.append({"domain": dom, "label": "MVP development: About half "
                              "to external developers", "delta": {"cash": -12_000}})
            if dom == "hiring":
                ss.state = game.apply(ss.state, {"pending_hires": 2, "pending_hires_extra": 1,
                                                 "pending_cost_extra": 7_000})


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
        snap["revenue_shown"] = area_start()["revenue"]
    storage.save_response(ss.code, sc, ss.index, response_seconds=kwargs.pop(
        "response_seconds", elapsed()), state=snap, entered_at=ss.screen_entered_at,
        **kwargs)


def remember(**values) -> None:
    ss.answers[screen()["id"]] = values


def recalled(key: str, default=None):
    return ss.answers.get(screen()["id"], {}).get(key, default)


def apply_effects(effects: dict, label: str | None, note: str | None = None) -> None:
    """Apply effects and record what changed. A `note` records a decision that
    changes no number yet (for example a planned fundraising start)."""
    before = ss.state
    ss.state = game.apply(ss.state, effects)
    delta = game.diff(before, ss.state)
    if label and (delta or note):
        ss.events.append({"domain": screen().get("domain"), "label": label,
                          "delta": delta, "note": note})


def startup_name() -> str:
    return content.STARTUP_NAME


def month_of(domain: str | None) -> int:
    """Each area is one month of Lumora's life; the final round is the month after."""
    order = content.TRACKS[ss.track]
    return order.index(domain) + 1 if domain in order else len(order) + 1


def month_label(domain: str | None) -> str:
    return content.MONTH.format(n=month_of(domain))


def panel() -> None:
    """The numbers panel above every simulation question."""
    sc = screen()
    ui.hud(area_start(), caption=f"{month_label(sc.get('domain'))} · at the start of this area"
           if sc.get("domain") in content.TRACKS[ss.track] else month_label(sc.get("domain")),
           brand=startup_name())


def decision_eyebrow() -> None:
    """'Finance · Decision 2 of 5' above each decision inside an area."""
    sc = screen()
    dom = sc.get("domain")
    if dom not in content.BLOCKS:
        ui.eyebrow(content.SECTION_FINAL)
        return
    nodes = [s["id"] for s in ss.screens if s.get("domain") == dom and s.get("node")]
    ui.eyebrow(f"{content.BLOCKS[dom]['title']} · Decision {nodes.index(sc['id']) + 1} "
               f"of {len(nodes)}")


def note_decision(spec: dict, choice_label: str) -> None:
    """Remember a decision for the timeline on the end screen."""
    if spec.get("event"):
        ss.journey = [j for j in ss.journey if j["id"] != screen()["id"]]
        ss.journey.append({"id": screen()["id"], "domain": screen().get("domain"),
                           "event": spec["event"], "choice": choice_label})


def pick(spec: dict, key: str):
    """The sole-founder version of a text (key + "_solo") if the participant runs
    the startup alone and one exists, otherwise the version with the co-founder."""
    if ss.get("solo") and f"{key}_solo" in spec:
        return spec[f"{key}_solo"]
    return spec.get(key)


def fill(text: str, **extra) -> str:
    """Fill the placeholders a text may use. Numbers come from the start of the
    area, so the text always matches the status strip."""
    s = area_start()
    values = {"name": startup_name(), "industry": ss.get("industry_label", "early-stage"),
              "runway": s["runway"],
              "launch_budget": game.money(game.launch_budget(s))}
    values.update(extra)
    return text.format(**values)


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
    ui.about_mode(content.ABOUT_NOTE, content.ABOUT_BANNER)


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
    """One profile field. Where "Other" is chosen, a text field appears below."""
    key, label, kind = field["key"], field["label"], field["kind"]
    saved = recalled(key)
    wkey = f"profile_{key}"
    if kind == "number":
        value = st.number_input(label, min_value=field["min"], max_value=field["max"],
                                step=1, value=saved, key=wkey,
                                placeholder=f"{field['min']} or more" if field["min"]
                                else "Type a number")
    elif kind == "select":
        opts = field["options"]
        value = st.selectbox(label, opts, index=opts.index(saved) if saved in opts else None,
                             placeholder="Select", key=wkey)
    elif kind == "pills":
        value = st.pills(label, field["options"], default=saved, key=wkey)
    elif kind == "multi":
        value = st.pills(label, field["options"], selection_mode="multi",
                         default=saved or [], key=wkey)
    else:
        value = st.text_input(label, value=saved or "", key=wkey)
    chose_other = value == "Other" or (isinstance(value, list) and "Other" in value)
    other = None
    if chose_other:
        other = st.text_input(content.OTHER_LABEL, value=recalled(f"{key}_other", ""),
                              key=f"{wkey}_other", label_visibility="collapsed",
                              placeholder=f"{content.OTHER_LABEL}: {label.split(' (')[0].lower()}")
    return value, other


def render_profile(sc: dict) -> None:
    frame()
    about_header()
    ui.question(content.PROFILE["question"], content.PROFILE["body"])
    values: dict = {}
    others: dict = {}

    def put(field):
        values[field["key"]], others[field["key"]] = _profile_widget(field)

    fields = content.PROFILE_FIELDS
    i = 0
    while i < len(fields):
        f = fields[i]
        nxt = fields[i + 1] if i + 1 < len(fields) else None
        if "col" in f and nxt is not None and "col" in nxt:
            c1, c2 = st.columns(2)
            with c1:
                put(f)
            with c2:
                put(nxt)
            i += 2
        else:
            put(f)
            i += 1

    if continue_button("profile_continue"):
        missing = [f["label"].split(" (")[0] for f in fields
                   if values.get(f["key"]) in (None, "", [])]
        missing += [f'{f["label"].split(" (")[0]} (other)' for f in fields
                    if others.get(f["key"]) is not None and not others[f["key"]].strip()]
        if missing:
            st.warning("Please answer every question. Still open: "
                       + "; ".join(missing) + ".")
            return
        stored = dict(values)
        for k, o in others.items():
            if o is not None:
                stored[f"{k}_other"] = o.strip()
        remember(**stored)
        log(text_value="; ".join(
            f"{k}={'|'.join(v) if isinstance(v, list) else v}" for k, v in stored.items()))
        advance()


def render_experience(sc: dict) -> None:
    frame()
    about_header()
    ui.question(content.EXPERIENCE["question"], content.EXPERIENCE["body"])
    values = {}
    with st.form("experience_form", border=False):
        for field in content.EXPERIENCE_FIELDS:
            values[field["key"]] = st.pills(
                field["label"], field["options"],
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
            ui.html_block(f'<div class="fs-scale-ends"><span>0 = {item["low"]}</span>'
                          f'<span>10 = {item["high"]}</span></div>')
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
    ui.question(spec["question"], content.RANGE_INSTRUCTION)
    ui.range_diagram("lower", "higher")
    c1, c2 = st.columns(2)
    with c1:
        low = st.number_input("Low estimate", min_value=0, max_value=5000, step=1,
                              value=None, key="practice_low", placeholder=spec["unit"])
        st.caption(spec["low_help"])
    with c2:
        high = st.number_input("High estimate", min_value=0, max_value=5000, step=1,
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

def render_transition(sc: dict) -> None:
    t = content.TRANSITION
    ui.transition(t["eyebrow"], t["title"], t["body"])
    if continue_button("transition_continue", t["button"]):
        log(option_key="seen")
        advance()


def render_setup(sc: dict) -> None:
    frame()
    spec = content.SETUP
    ui.question(fill(spec["question"]), fill(spec["body"]))
    team_keys = [k for k, _ in spec["team_options"]]
    team_labels = [lab for _, lab in spec["team_options"]]
    saved_team = recalled("team")
    team_choice = st.radio(fill(spec["team_label"]), team_labels,
                           index=team_keys.index(saved_team) if saved_team in team_keys else None,
                           key="setup_team", help=spec["team_help"])
    own = ss.answers.get("profile", {})
    own_industry = own.get("industry_real")
    options = content.INDUSTRIES
    industry = st.selectbox(fill(spec["industry_label"]), options,
                            index=options.index(own_industry) if own_industry in options else None,
                            placeholder="Select", key="setup_industry",
                            help=spec["industry_help"])
    other = None
    if industry == "Other":
        other = st.text_input(content.OTHER_LABEL, key="setup_industry_other",
                              value=own.get("industry_real_other", ""),
                              label_visibility="collapsed",
                              placeholder=f"{content.OTHER_LABEL}: industry")
    if continue_button("setup_continue"):
        if team_choice is None:
            st.warning("Please choose whether you run the startup on your own or "
                       "with a co-founder.")
            return
        if industry is None or (industry == "Other" and not (other or "").strip()):
            st.warning("Please choose the industry.")
            return
        team = team_keys[team_labels.index(team_choice)]
        remember(team=team)
        ss.solo = team == "solo"
        ss.state = game.new_state(solo=ss.solo)     # no decision has been made yet
        label = other.strip() if industry == "Other" else industry
        ss.industry_label = content.INDUSTRY_LABELS.get(industry, label.lower())
        ss.product = content.INDUSTRY_PRODUCTS.get(
            industry, content.PRODUCT_OTHER.format(label=label.lower()))
        storage.update_session(ss.code, startup_name=content.STARTUP_NAME, industry=label,
                               solo=int(ss.solo))
        log(option_key=team,
            text_value=f"{content.STARTUP_NAME} | {label} | "
                       f"{'solo' if ss.solo else 'co-founder'}")
        advance()


def render_starting_situation(sc: dict) -> None:
    frame()
    ui.eyebrow(month_label(content.TRACKS[ss.track][0]))
    st.subheader(content.STARTING_SITUATION["title"])
    c = content.COMPANY
    product = ss.get("product") or content.PRODUCT_OTHER.format(label="its field")
    ui.company_card(startup_name(), c["founded"],
                    fill(c["product"], product=product),
                    [c["run_solo"] if ss.solo else c["run_team"],
                     ss.get("industry_label", "early-stage").capitalize()])
    st.markdown(fill(pick(content.STARTING_SITUATION, "body")))
    ui.status_cards(ss.state, solo=ss.solo)
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
    ui.eyebrow(f"{content.MONTH.format(n=n)} · Area {n} of 4")
    st.subheader(block["title"])
    st.markdown(fill(pick(block, "intro")))
    st.markdown("**Where you start this area**")
    ui.status_cards(ss.state, solo=ss.solo)
    if continue_button(f"intro_{domain}_continue"):
        advance()


def _option_label(opt: dict, cost_override: int | None = None) -> str:
    label = pick(opt, "label")
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
    panel()
    decision_eyebrow()
    body = pick(spec, "body")
    ui.question(fill(pick(spec, "question")), fill(body) if body else None,
                sources=spec.get("background"))

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
        note_decision(spec, pick(opt, "label"))
        event = f'{spec["event"]}: {pick(opt, "label")}' if spec.get("event") else None
        effects = dict(opt.get("effects", {}))
        if effects.get("spend_launch_budget") is True:
            effects["spend_launch_budget"] = game.launch_budget(area_start())
        if "raise" in effects:
            # The running costs until the round starts are paid first (F1).
            months = ss.state.get("fundraise_delay", 0)
            if months:
                apply_effects({"cash": -game.delay_cost(ss.state)},
                              f"Running costs until fundraising starts ({months} months)")
                ss.state["fundraise_delay"] = 0
        note = "planned" if "fundraise_delay" in effects else None
        apply_effects(effects, event, note=note)
        advance()


def render_multi(sc: dict) -> None:
    frame()
    node_id = sc["node"]
    spec = content.SCREENS[node_id]
    panel()
    decision_eyebrow()
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
    panel()
    decision_eyebrow()
    if spec.get("message"):
        sender, subject = content.MESSAGES.get(node_id, ("", ""))
        ui.message(sender, subject, fill(spec["message"], prize=money(params["prize"])))
    ui.question(fill(spec["question"], prize=money(params["prize"])),
                fill(spec["body"], prize=money(params["prize"]),
                     base_cost=money(params["base_cost"])),
                sources=spec.get("background"))
    labels = []
    for opt in spec["options"]:
        cost = params["options"][opt["key"]]["cost"]
        labels.append(_option_label(opt, cost_override=cost if cost else None))
    choice = st.radio("Options", labels, index=None, label_visibility="collapsed",
                      key=f"contest_{node_id}")
    st.caption(content.CONTEST_NOTE)
    if continue_button(f"contest_{node_id}_continue"):
        if choice is None:
            st.warning("Please choose one of the options.")
            return
        idx = labels.index(choice)
        key = spec["options"][idx]["key"]
        log(option_key=key, option_index=idx)
        note_decision(spec, spec["options"][idx]["label"])
        cost = params["options"][key]["cost"]
        apply_effects(game.contest_effects(cost),
                      f'{spec["event"]}: {spec["options"][idx]["label"]}' if cost else None)
        advance()


def _interval_input(spec: dict, which: str, node_id: str):
    is_money = spec["unit"] == "euros"
    val = st.number_input(f"{which.capitalize()} estimate", min_value=int(spec["min_value"]),
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
    panel()
    decision_eyebrow()
    revenue_now = area_start()["revenue"]
    if spec.get("chart") == "revenue":
        factor = revenue_now / 8_000
        series = [(lab, round(v * factor, -1), chg) for lab, v, chg in content.CHART_REVENUE]
        series[-1] = (series[-1][0], revenue_now, series[-1][2])
        ui.bar_chart(series, money, "Monthly revenue so far", "In 12 months")
    elif spec.get("chart") == "customers":
        ui.bar_chart(content.CHART_CUSTOMERS, lambda v: f"{v:,.0f}",
                     "New paying customers per month", "Total, months 4 to 9")
    ui.question(fill(spec["question"], revenue_now=money(revenue_now)),
                content.RANGE_INSTRUCTION, sources=spec.get("background"))
    ui.range_diagram("lower", "higher")

    c1, c2 = st.columns(2)            # always: low on the left, high on the right
    with c1:
        low = _interval_input(spec, "low", node_id)
    with c2:
        high = _interval_input(spec, "high", node_id)

    if continue_button(f"interval_{node_id}_continue"):
        if low is None or high is None:
            st.warning("Please enter both numbers.")
            return
        if low > high:
            st.warning("Your low estimate is higher than your high estimate. "
                       "Please check the two numbers.")
            return
        # Stored as the optimistic and the pessimistic value, as the scoring
        # expects. For durations the optimistic value is the low one.
        opt, pes = (high, low) if spec["optimistic_is_high"] else (low, high)
        t = elapsed()
        log({**sc, "id": f"{node_id}_opt"}, numeric_value=float(opt),
            text_value=f"low={low}; high={high}", response_seconds=t)
        log({**sc, "id": f"{node_id}_pes"}, numeric_value=float(pes),
            text_value=f"low={low}; high={high}", response_seconds=0.0)
        advance()


def render_rank(sc: dict) -> None:
    frame()
    node_id = sc["node"]
    spec = content.SCREENS[node_id]
    panel()
    decision_eyebrow()
    sender, subject = content.MESSAGES.get(node_id, ("", ""))
    ui.message(sender, subject, fill(spec["question"]))
    ui.question(fill(spec["body"]), sources=spec.get("background"))
    choice = st.pills("Rank", content.RANK_SCALE, label_visibility="collapsed",
                      key=f"rank_{node_id}")
    ui.html_block('<div class="fs-scale-ends"><span>' + content.RANK_ENDS[0]
                  + '</span><span>' + content.RANK_ENDS[1] + '</span></div>')
    if continue_button(f"rank_{node_id}_continue"):
        if choice is None:
            st.warning("Please choose a rank from 1 to 10.")
            return
        log(option_key=str(choice), option_index=int(choice) - 1)
        advance()


def render_hire(sc: dict) -> None:
    """H4. The order in which the two candidates are described is randomised.
    Key A is always the work-sample candidate, key B the gut-feeling one."""
    frame()
    node_id = sc["node"]
    spec = content.SCREENS[node_id]
    panel()
    decision_eyebrow()
    order = ["A", "B"] if sc.get("first", "A") == "A" else ["B", "A"]
    cands = pick(spec, "candidates")
    body = (f"Candidate 1 {cands[order[0]]}. "
            f"Candidate 2 {cands[order[1]]}. {spec['after']}")
    ui.question(fill(spec["question"]), body, sources=spec.get("background"))
    second = spec["options"][2]
    labels = ["Hire Candidate 1", "Hire Candidate 2", _option_label(second)]
    keys = [order[0], order[1], second["key"]]
    choice = st.radio("Options", labels, index=None, label_visibility="collapsed",
                      key=f"hire_{node_id}")
    if continue_button(f"hire_{node_id}_continue"):
        if choice is None:
            st.warning("Please choose one of the options.")
            return
        idx = labels.index(choice)
        key = keys[idx]
        opt = next(o for o in spec["options"] if o["key"] == key)
        log(option_key=key, option_index="ABC".index(key),
            text_value=f"first={order[0]}")
        note_decision(spec, "Second structured round" if key == "C"
                      else f"Hired Candidate {idx + 1}")
        if key == "C":
            apply_effects(opt["effects"], f'{spec["event"]}: second structured round')
        else:
            apply_effects(opt["effects"], f'{spec["event"]}: Candidate {idx + 1} hired',
                          note="starts at the end of this area")
        advance()


def render_report(sc: dict) -> None:
    frame()
    domain = sc["domain"]
    if domain not in ss.closed:
        ss.state, events = game.end_of_area(ss.state, domain)
        for ev in events:
            ss.events.append({"domain": domain, **ev})
        ss.closed.add(domain)
    n = month_of(domain)
    ui.month_end(content.MONTH_END["title"].format(n=n),
                 fill(content.MONTH_END["body"]))
    ui.eyebrow(f"{content.MONTH.format(n=n)} · Area {n} of 4 complete")
    st.subheader("Where things stand")
    ui.status_cards(ss.state, before=ss.block_start.get(domain), solo=ss.solo, animate=True)
    st.markdown("**What changed in this area**")
    ui.changes([e for e in ss.events if e["domain"] == domain], solo=ss.solo)
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
    j = content.JOURNEY
    months = []
    for dom in content.TRACKS[ss.track] + ["final"]:
        items = [(e["event"], e["choice"]) for e in ss.journey if e["domain"] == dom]
        if not items:
            continue
        title = content.BLOCKS[dom]["title"] if dom in content.BLOCKS else content.SECTION_FINAL
        months.append((month_label(dom), title, items))
    if months:
        st.subheader(fill(j["title"]))
        st.markdown(j["body"])
        ui.journey(months)
        st.markdown(f"**{fill(j['final'])}**")
        ui.status_cards(ss.state, solo=ss.solo)


def render_final_intro(sc: dict) -> None:
    frame()
    ui.eyebrow(content.SECTION_FINAL)
    st.subheader(content.FINAL_INTRO["title"])
    st.markdown(fill(content.FINAL_INTRO["body"]))
    if continue_button("final_intro_continue"):
        log(option_key="seen")
        advance()


RENDERERS = {
    "consent": render_consent, "filter": render_filter, "email": render_email,
    "profile": render_profile, "experience": render_experience, "risk": render_risk,
    "warmup_intro": render_warmup_intro, "practice_choice": render_practice_choice,
    "practice_range": render_practice_range, "setup": render_setup,
    "starting_situation": render_starting_situation, "block_intro": render_block_intro,
    "choice": render_choice, "multi": render_multi, "contest": render_contest,
    "interval": render_interval, "rank": render_rank, "hire": render_hire,
    "report": render_report,
    "transition": render_transition, "final_intro": render_final_intro,
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
    with st.container(key=f"screen_{ss.index}"):
        RENDERERS[sc["kind"]](sc)
