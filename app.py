"""Founder decision simulation.

Run with:  streamlit run app.py

The session never names confidence, calibration or overconfidence before the
debrief, and never shows a reference value or a realised outcome until then.
"""

from __future__ import annotations

import random
import time

import streamlit as st

from sim import codebook, content, flow, state as game, storage

st.set_page_config(page_title="Decisions in founding", page_icon="•",
                   layout="centered", initial_sidebar_state="collapsed")

STYLE = """
<style>
  .block-container {max-width: 46rem; padding-top: 2.5rem; padding-bottom: 4rem;}
  h1, h2, h3 {letter-spacing: -0.015em;}
  div[data-testid="stMarkdownContainer"] p {font-size: 1.02rem; line-height: 1.65;}
  /* Answer options as one column of equal-width cards. */
  div[data-testid="stRadio"], div[data-testid="stRadio"] > div {width: 100%;}
  div[role="radiogroup"] {
      gap: 0.4rem; width: 100% !important; align-items: stretch;
  }
  label[data-testid="stRadioOption"] {
      display: flex; align-items: center; box-sizing: border-box;
      width: 100%; padding: 0.7rem 0.95rem; margin: 0; border-radius: 10px;
      border: 1px solid rgba(26,29,33,0.16); background: #fff;
      transition: border-color 120ms ease, background 120ms ease;
  }
  label[data-testid="stRadioOption"]:hover {
      border-color: rgba(31,58,95,0.55); background: rgba(31,58,95,0.03);
  }
  /* Horizontal groups (profile, experience) stay inline and unboxed. */
  div[role="radiogroup"][aria-orientation="horizontal"] label[data-testid="stRadioOption"] {
      width: auto; border: none; background: none; padding: 0.3rem 0.9rem 0.3rem 0;
  }
  .stButton button {padding: 0.5rem 1.6rem; border-radius: 10px; font-weight: 500;}
  /* Nothing in the chrome should distract a participant. */
  div[data-testid="stToolbar"], #MainMenu, header[data-testid="stHeader"],
  footer {visibility: hidden; height: 0;}
  .q {font-size: 1.22rem; font-weight: 600; line-height: 1.45; margin-bottom: 0.6rem;}
  .sit {color: rgba(128,128,128,0.95); font-size: 0.9rem; letter-spacing: 0.04em;
        text-transform: uppercase; margin-bottom: 0.25rem;}
  .hint {color: rgba(128,128,128,0.95); font-size: 0.92rem;}
  div[data-testid="stMetricValue"] {font-size: 1.25rem;}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session bootstrap
# ---------------------------------------------------------------------------

def init() -> None:
    if "code" in st.session_state:
        return
    seed = random.randrange(1, 2**31 - 1)
    rng = random.Random(seed)
    st.session_state.seed = seed
    st.session_state.rng = rng
    st.session_state.track = flow.assign_track(rng)
    st.session_state.code = flow.make_code(rng)
    st.session_state.screens = flow.build(st.session_state.track, seed)
    st.session_state.index = 0
    st.session_state.solo = False
    st.session_state.state = game.new_state(solo=False)
    st.session_state.started = False
    st.session_state.screen_entered = time.monotonic()
    st.session_state.answers = {}


init()


def screen() -> dict:
    return st.session_state.screens[st.session_state.index]


def elapsed() -> float:
    return round(time.monotonic() - st.session_state.screen_entered, 3)


def advance() -> None:
    st.session_state.index += 1
    st.session_state.screen_entered = time.monotonic()
    st.rerun()


def log(**kwargs) -> None:
    storage.save_response(
        st.session_state.code, screen(), st.session_state.index,
        response_seconds=elapsed(), state=game.snapshot(st.session_state.state),
        **kwargs)


def apply_effects(effects: dict) -> None:
    st.session_state.state = game.apply(st.session_state.state, effects)


def text(value: str) -> str:
    """Fill the placeholders a question reads from the situation."""
    s = st.session_state.state
    return value.format(
        runway=s["runway"],
        launch_budget=f'{game.launch_budget(s):,.0f} euros'.replace(",", "."),
        cash=f'{s["cash"]:,.0f}'.replace(",", "."),
        team_size=s["team_size"],
    )


def solo_variant(block: dict, key: str) -> str:
    if st.session_state.solo and f"{key}_solo" in block:
        return block[f"{key}_solo"]
    return block[key]


def header() -> None:
    done, total = flow.progress(st.session_state.screens, st.session_state.index)
    st.progress(done / total)


def euros(value: float) -> str:
    return f"{value:,.0f} euros".replace(",", ".")


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

def render_consent(sc: dict) -> None:
    st.title(content.CONSENT["title"])
    st.markdown(content.CONSENT["body"])
    col1, col2 = st.columns([1, 1])
    if col1.button(content.CONSENT["agree"], type="primary"):
        storage.start_session(st.session_state.code, st.session_state.track,
                              st.session_state.seed, content.APP_VERSION,
                              codebook.version())
        st.session_state.started = True
        storage.update_session(st.session_state.code, consent=1)
        log(option_key="agree")
        advance()
    if col2.button(content.CONSENT["decline"]):
        st.session_state.declined = True
        st.rerun()


def render_filter(sc: dict) -> None:
    header()
    st.markdown(f'<div class="q">{content.FILTER["question"]}</div>',
                unsafe_allow_html=True)
    st.caption(content.FILTER["help"])
    choice = st.radio("Answer", content.FILTER["options"], index=None,
                      label_visibility="collapsed", key="filter_choice")
    if st.button("Continue", type="primary", disabled=choice is None):
        is_founder = choice == "Yes"
        storage.update_session(st.session_state.code, is_founder=int(is_founder))
        log(option_key=choice)
        if not is_founder:
            st.session_state.not_founder = True
            st.rerun()
        advance()


def render_setup(sc: dict) -> None:
    header()
    st.markdown('<div class="q">Let us set up your start-up.</div>',
                unsafe_allow_html=True)
    with st.form("setup"):
        name = st.text_input(content.SETUP["name_label"],
                             placeholder=content.SETUP["name_placeholder"])
        industry = st.selectbox(content.SETUP["industry_label"], content.INDUSTRIES)
        solo = st.radio(content.SETUP["solo_label"], content.SETUP["solo_options"],
                        horizontal=True)
        if st.form_submit_button("Continue", type="primary"):
            is_solo = solo == "Alone"
            st.session_state.solo = is_solo
            st.session_state.state = game.new_state(solo=is_solo)
            st.session_state.startup_name = name.strip() or "your start-up"
            storage.update_session(st.session_state.code, solo=int(is_solo),
                                   startup_name=name.strip(), industry=industry)
            log(text_value=f"{name.strip()} | {industry} | {solo}")
            advance()


def render_code(sc: dict) -> None:
    header()
    st.markdown('<div class="q">Your code</div>', unsafe_allow_html=True)
    st.markdown(
        "Everything you enter is stored under this code and nothing else identifies you. "
        "Note it down if you might want your data removed later."
    )
    st.code(st.session_state.code, language=None)
    if st.button("Continue", type="primary"):
        log(text_value=st.session_state.code)
        advance()


def render_practice_name(sc: dict) -> None:
    header()
    st.caption(content.PRACTICE_NAME["question"])
    with st.form("practice_name"):
        product = st.text_input(content.PRACTICE_NAME["product_label"])
        colour = st.selectbox(content.PRACTICE_NAME["colour_label"],
                              content.PRACTICE_NAME["colours"])
        if st.form_submit_button("Continue", type="primary"):
            log(text_value=f"{product} | {colour}")
            advance()


def render_practice_range(sc: dict) -> None:
    header()
    half = sc["half"]
    spec = content.PRACTICE_RANGE[half]
    if half == "low":
        st.caption(content.PRACTICE_RANGE["intro"])
    st.markdown(f'<div class="q">{spec["question"]}</div>', unsafe_allow_html=True)
    st.markdown(spec["prompt"])
    with st.form(f"practice_{half}"):
        value = st.number_input("cups", min_value=0, max_value=5000, step=1, value=None,
                                label_visibility="collapsed")
        if st.form_submit_button("Continue", type="primary"):
            if value is None:
                st.warning("Please enter a number.")
            else:
                log(numeric_value=float(value))
                advance()


def render_block_intro(sc: dict) -> None:
    header()
    block = content.BLOCKS[sc["domain"]]
    st.markdown(f'<div class="sit">{st.session_state.get("startup_name", "")}</div>',
                unsafe_allow_html=True)
    st.subheader(block["title"])
    st.markdown(solo_variant(block, "intro"))
    if st.button("Continue", type="primary"):
        advance()


def render_choice(sc: dict) -> None:
    header()
    node_id = sc["node"]
    spec = content.SCREENS[node_id]
    question = text(spec.get("question_solo") if st.session_state.solo
                    and "question_solo" in spec else spec["question"])
    st.markdown(f'<div class="q">{question}</div>', unsafe_allow_html=True)
    if spec.get("body"):
        st.markdown(text(spec["body"]))

    labels, keys = [], []
    for opt in spec["options"]:
        label = opt.get("label_solo") if st.session_state.solo and "label_solo" in opt \
            else opt["label"]
        if opt.get("extra"):
            label = f'{label}  ·  {opt["extra"]}'
        labels.append(label)
        keys.append(opt["key"])

    choice = st.radio("Options", labels, index=None, label_visibility="collapsed",
                      key=f"choice_{node_id}")
    if st.button("Continue", type="primary", disabled=choice is None):
        idx = labels.index(choice)
        opt = spec["options"][idx]
        log(option_key=keys[idx], option_index=idx)
        apply_effects(opt.get("effects", {}))
        advance()


def render_contest(sc: dict) -> None:
    header()
    node_id = sc["node"]
    spec = content.SCREENS[node_id]
    params = codebook.contest_params(node_id)

    question = spec["question"].format(prize=euros(params["prize"]))
    body = spec["body"].format(prize=euros(params["prize"]),
                               base_cost=euros(params["base_cost"]))
    st.markdown(f'<div class="q">{question}</div>', unsafe_allow_html=True)
    st.markdown(body)

    labels, keys = [], []
    for opt in spec["options"]:
        key = opt["key"]
        cost = params["options"][key]["cost"]
        label = opt["label"]
        if cost:
            label = f"{label}  ·  {euros(cost)}"
        if opt.get("extra"):
            label = f'{label}  ·  {opt["extra"]}'
        labels.append(label)
        keys.append(key)

    choice = st.radio("Options", labels, index=None, label_visibility="collapsed",
                      key=f"contest_{node_id}")
    if st.button("Continue", type="primary", disabled=choice is None):
        idx = labels.index(choice)
        key = keys[idx]
        log(option_key=key, option_index=idx)
        apply_effects(game.contest_effects(params["options"][key]["cost"]))
        advance()


def render_interval(sc: dict) -> None:
    header()
    node_id = sc["node"]
    spec = content.SCREENS[node_id]
    half = sc["half"]
    st.markdown(f'<div class="q">{text(spec["question"])}</div>',
                unsafe_allow_html=True)
    st.markdown(spec[f"{half}_prompt"])

    with st.form(f"interval_{sc['id']}"):
        value = st.number_input(
            spec["unit"], min_value=float(spec["min_value"]),
            max_value=float(spec["max_value"]), step=1.0, value=None,
            label_visibility="collapsed", format="%g")
        st.caption(f'in {spec["unit"]}')
        if st.form_submit_button("Continue", type="primary"):
            if value is None:
                st.warning("Please enter a number.")
            else:
                log(numeric_value=float(value))
                advance()


def render_report(sc: dict) -> None:
    header()
    st.session_state.state = game.close_block(st.session_state.state)
    st.markdown('<div class="sit">Where things stand</div>', unsafe_allow_html=True)
    rows = game.report_rows(st.session_state.state)
    for i in range(0, len(rows), 3):
        cols = st.columns(3)
        for col, (label, value) in zip(cols, rows[i:i + 3]):
            col.metric(label, value)
    if st.button("Continue", type="primary"):
        advance()


def render_suspicion(sc: dict) -> None:
    header()
    st.markdown(f'<div class="q">{content.SUSPICION["question"]}</div>',
                unsafe_allow_html=True)
    st.caption(content.SUSPICION["prompt"])
    with st.form("suspicion"):
        answer = st.text_area("Your answer", height=140, label_visibility="collapsed")
        if st.form_submit_button("Continue", type="primary"):
            log(text_value=answer.strip())
            advance()


def render_profile(sc: dict) -> None:
    header()
    st.markdown('<div class="q">A few things about you</div>', unsafe_allow_html=True)
    with st.form("profile"):
        values = {}
        for field in content.PROFILE_FIELDS:
            if field["kind"] == "number":
                values[field["key"]] = st.number_input(
                    field["label"], min_value=field["min"], max_value=field["max"],
                    step=1, value=None)
            elif field["kind"] == "select":
                values[field["key"]] = st.selectbox(field["label"], field["options"],
                                                    index=None)
            else:
                values[field["key"]] = st.text_input(field["label"])
        if st.form_submit_button("Continue", type="primary"):
            log(text_value="; ".join(f"{k}={v}" for k, v in values.items()))
            advance()


def render_experience(sc: dict) -> None:
    header()
    st.markdown('<div class="q">How much of this have you done before?</div>',
                unsafe_allow_html=True)
    with st.form("experience"):
        values = {}
        for field in content.EXPERIENCE_FIELDS:
            values[field["key"]] = st.radio(
                field["label"], content.EXPERIENCE_OPTIONS, horizontal=True, index=None)
        if st.form_submit_button("Continue", type="primary"):
            log(text_value="; ".join(f"{k}={v}" for k, v in values.items()))
            advance()


def render_risk(sc: dict) -> None:
    header()
    st.markdown('<div class="q">Two last questions about how you decide</div>',
                unsafe_allow_html=True)
    with st.form("risk"):
        values = {}
        for item in content.RISK_ITEMS:
            st.markdown(item["label"])
            values[item["key"]] = st.slider(
                f'{item["low"]} — {item["high"]}', 0, 10, 5, key=f'risk_{item["key"]}')
        if st.form_submit_button("Continue", type="primary"):
            log(text_value="; ".join(f"{k}={v}" for k, v in values.items()))
            advance()


def render_debrief_purpose(sc: dict) -> None:
    st.title(content.DEBRIEF_PURPOSE["title"])
    st.markdown(content.DEBRIEF_PURPOSE["body"])
    if st.button("Continue", type="primary"):
        log(option_key="seen")
        advance()


def render_debrief_data(sc: dict) -> None:
    st.subheader(content.DEBRIEF_DATA["title"])
    st.markdown(content.DEBRIEF_DATA["body"].format(code=st.session_state.code))
    email = st.text_input(
        "Mail address for the questionnaire in a week (optional)",
        placeholder="you@example.com")
    col1, col2 = st.columns([1, 1])
    if col1.button("My data can be used", type="primary"):
        if email.strip():
            storage.save_followup(st.session_state.code, email)
        log(option_key="keep")
        advance()
    if col2.button("Please do not use my data"):
        storage.withdraw(st.session_state.code)
        log(option_key="withdraw")
        st.session_state.withdrawn = True
        advance()


def render_debrief_results(sc: dict) -> None:
    from sim import scoring

    st.subheader(content.DEBRIEF_RESULTS["title"])
    st.markdown(content.DEBRIEF_RESULTS["intro"])

    rows = storage.fetch_responses(st.session_state.code)
    scored = scoring.score_participant(rows, seed=st.session_state.seed)

    st.markdown(f'#### {content.DEBRIEF_RESULTS["intervals_header"]}')
    st.caption(content.DEBRIEF_RESULTS["intervals_note"])
    labels = {"T3": "Weeks to the MVP", "F3": "Monthly revenue in 12 months",
              "H3": "Weeks to a signed contract", "G3": "New customers in six months"}
    any_interval = False
    for node_id, label in labels.items():
        entry = scored.get(node_id)
        if not entry or entry.get("incomplete"):
            continue
        any_interval = True
        mark = "inside your range" if entry["hit"] else "outside your range"
        st.markdown(
            f'**{label}** — you said {entry["lower"]:,.0f} to {entry["upper"]:,.0f} '
            f'{entry["unit"]}. The value we drew was **{entry["drawn_value"]:,.0f}**, '
            f'{mark}.'.replace(",", "."))
    if not any_interval:
        st.caption("No ranges recorded.")

    st.markdown(f'#### {content.DEBRIEF_RESULTS["contests_header"]}')
    st.caption(content.DEBRIEF_RESULTS["contests_note"])
    contest_labels = {"T2": "Pitch contest", "F2": "Founders' network contest",
                      "H2": "The senior developer", "G2": "The lead customer tender"}
    total = 0
    for node_id, label in contest_labels.items():
        entry = scored.get(node_id)
        if not entry:
            continue
        out = entry["outcome"]
        if not out["entered"]:
            st.markdown(f"**{label}** — you stayed out. Nothing spent.")
            continue
        result = "you won" if out["won"] else "you did not win"
        total += out["net"]
        st.markdown(
            f'**{label}** — you put in {euros(out["cost"])} at a '
            f'{out["win_probability"]:.0%} chance, and {result}. '
            f'Net: {euros(out["net"])}.')
    if total:
        st.markdown(f"**Across the four contests: {euros(total)}.**")

    if st.button("Continue", type="primary"):
        log(option_key="seen")
        advance()


def render_end(sc: dict) -> None:
    storage.complete_session(st.session_state.code)
    st.markdown(content.THANK_YOU_END.format(code=st.session_state.code))
    if st.session_state.get("withdrawn"):
        st.info("Your data has been marked as withdrawn and will not be used.")
    st.balloons()


RENDERERS = {
    "consent": render_consent, "filter": render_filter, "setup": render_setup,
    "code": render_code, "practice_name": render_practice_name,
    "practice_range": render_practice_range, "block_intro": render_block_intro,
    "choice": render_choice, "contest": render_contest, "interval": render_interval,
    "report": render_report, "suspicion": render_suspicion, "profile": render_profile,
    "experience": render_experience, "risk": render_risk,
    "debrief_purpose": render_debrief_purpose, "debrief_data": render_debrief_data,
    "debrief_results": render_debrief_results, "end": render_end,
}


# ---------------------------------------------------------------------------

if st.query_params.get("view") == "admin":
    from sim import admin
    admin.render()
elif st.session_state.get("declined"):
    st.title(content.CONSENT["title"])
    st.markdown("No problem. Nothing has been stored. You can close this page.")
elif st.session_state.get("not_founder"):
    st.markdown(content.THANK_YOU_NOT_FOUNDER)
else:
    sc = screen()
    RENDERERS[sc["kind"]](sc)
