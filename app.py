"""Founder decision simulation.

Run with:  streamlit run app.py

The session never names confidence, calibration or overconfidence. Reference
values are never shown to the participant: they live only in the backend and
are used only for the analysis. The full debrief is delivered through the
follow-up a week later, opened with the pseudonym code.
"""

from __future__ import annotations

import random
import time

import streamlit as st

from sim import codebook, content, flow, state as game, storage

st.set_page_config(page_title="Decisions in founding", page_icon="•",
                   layout="centered", initial_sidebar_state="collapsed")

# ---------------------------------------------------------------------------
# Styles. Light theme is enforced via config and here: both themes render the
# same so answer cards are always legible, regardless of the viewer's OS.
# ---------------------------------------------------------------------------

STYLE = """
<style>
  :root, [data-theme="dark"] {
      color-scheme: light;
      --fg: #1A1D21;
      --fg-muted: #5F6672;
      --bg: #FFFFFF;
      --bg-soft: #F4F6F8;
      --accent: #1F3A5F;
      --accent-soft: rgba(31,58,95,0.08);
      --border: rgba(26,29,33,0.16);
      --border-hover: rgba(31,58,95,0.55);
      --warning-bg: #FFF4E5;
      --warning-fg: #7A4A00;
  }
  html, body, .stApp {background: var(--bg) !important; color: var(--fg) !important;}
  .block-container {max-width: 46rem; padding-top: 2.5rem; padding-bottom: 4rem;}
  h1, h2, h3, h4 {letter-spacing: -0.015em; color: var(--fg) !important;}
  p, li, label, span, div {color: var(--fg);}
  div[data-testid="stMarkdownContainer"] p {font-size: 1.02rem; line-height: 1.65;}

  /* Answer options as one column of equal-width cards, legible in dark mode. */
  div[data-testid="stRadio"], div[data-testid="stRadio"] > div {width: 100%;}
  div[role="radiogroup"] {
      gap: 0.4rem; width: 100% !important; align-items: stretch;
  }
  label[data-testid="stRadioOption"] {
      display: flex; align-items: center; box-sizing: border-box;
      width: 100%; padding: 0.75rem 1rem; margin: 0; border-radius: 10px;
      border: 1px solid var(--border) !important;
      background: var(--bg) !important; color: var(--fg) !important;
      transition: border-color 120ms ease, background 120ms ease;
  }
  label[data-testid="stRadioOption"] * {color: var(--fg) !important;}
  label[data-testid="stRadioOption"]:hover {
      border-color: var(--border-hover) !important;
      background: var(--accent-soft) !important;
  }
  /* Horizontal radio groups (likert, inline choices) stay compact. */
  div[role="radiogroup"][aria-orientation="horizontal"] label[data-testid="stRadioOption"] {
      width: auto; border: none !important; background: none !important;
      padding: 0.3rem 0.9rem 0.3rem 0;
  }

  .stButton button, .stDownloadButton button, .stFormSubmitButton button {
      padding: 0.55rem 1.6rem; border-radius: 10px; font-weight: 500;
  }
  button[kind="primary"], .stButton button[kind="primary"] {
      background: var(--accent) !important; color: #fff !important;
      border: 1px solid var(--accent) !important;
  }
  button[kind="secondary"], .stButton button[kind="secondary"] {
      background: var(--bg) !important; color: var(--fg) !important;
      border: 1px solid var(--border) !important;
  }

  /* Numeric inputs legible in both themes. */
  input, textarea, [data-baseweb="input"] input, [data-baseweb="textarea"] textarea,
  [data-baseweb="select"] div {color: var(--fg) !important; background: var(--bg) !important;}

  /* Hide app chrome: participants should see the question, nothing else. */
  div[data-testid="stToolbar"], #MainMenu, header[data-testid="stHeader"],
  footer, div[data-testid="stDecoration"] {visibility: hidden; height: 0;}

  .q {font-size: 1.22rem; font-weight: 600; line-height: 1.45;
      margin-bottom: 0.6rem; color: var(--fg) !important;}
  .sit {color: var(--fg-muted); font-size: 0.9rem; letter-spacing: 0.04em;
        text-transform: uppercase; margin-bottom: 0.25rem;}
  .hint {color: var(--fg-muted); font-size: 0.92rem;}
  .mand {color: #B23A48; font-weight: 500;}

  div[data-testid="stMetricValue"] {font-size: 1.25rem; color: var(--fg) !important;}
  div[data-testid="stMetricLabel"] {color: var(--fg-muted) !important;}

  /* Progress bar in accent colour. */
  div[data-testid="stProgress"] div[role="progressbar"] > div {background: var(--accent);}
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


def go_back() -> None:
    if st.session_state.index > 0:
        st.session_state.index -= 1
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
        launch_budget=f'{game.launch_budget(s):,.0f} euros',
        cash=f'{s["cash"]:,.0f}',
        team_size=s["team_size"],
    )


def solo_variant(block: dict, key: str) -> str:
    if st.session_state.solo and f"{key}_solo" in block:
        return block[f"{key}_solo"]
    return block[key]


def header() -> None:
    done, total = flow.progress(st.session_state.screens, st.session_state.index)
    st.progress(done / total)
    sc = screen()
    if sc["kind"] in flow.BACK_ALLOWED and st.session_state.index > 0:
        if st.button("← Back", key=f"back_{sc['id']}"):
            go_back()


def euros(value: float) -> str:
    return f"{value:,.0f} euros"


def scenario_popover(spec: dict) -> None:
    """Small info popover attached to a measurement question, showing the
    *scenario* context and sources. Never discloses the measurement reference.
    """
    if not spec.get("scenario") and not spec.get("sources"):
        return
    with st.popover("About this scenario", use_container_width=False):
        if spec.get("scenario"):
            st.markdown(spec["scenario"])
        if spec.get("sources"):
            st.markdown("**Related reading**")
            for src in spec["sources"]:
                st.markdown(f"- {src}")


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

def render_consent(sc: dict) -> None:
    st.title(content.CONSENT["title"])
    st.markdown(content.CONSENT["body"])
    col1, col2 = st.columns([1, 1])
    if col1.button(content.CONSENT["agree"], type="primary", key="consent_agree"):
        storage.start_session(st.session_state.code, st.session_state.track,
                              st.session_state.seed, content.APP_VERSION,
                              codebook.version())
        st.session_state.started = True
        storage.update_session(st.session_state.code, consent=1)
        log(option_key="agree")
        advance()
    if col2.button(content.CONSENT["decline"], key="consent_decline"):
        st.session_state.declined = True
        st.rerun()


def render_filter(sc: dict) -> None:
    header()
    st.markdown(f'<div class="q">{content.FILTER["question"]}</div>',
                unsafe_allow_html=True)
    st.caption(content.FILTER["help"])
    choice = st.radio("Answer", content.FILTER["options"], index=None,
                      label_visibility="collapsed", key="filter_choice")
    if st.button("Continue", type="primary", key="filter_continue"):
        if choice is None:
            st.warning("Please select Yes or No.")
            return
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
    with st.form("setup", clear_on_submit=False):
        name = st.text_input(content.SETUP["name_label"],
                             placeholder=content.SETUP["name_placeholder"])
        industry = st.selectbox(content.SETUP["industry_label"],
                                content.INDUSTRIES, index=None,
                                placeholder="Pick one")
        solo = st.radio(content.SETUP["solo_label"],
                        content.SETUP["solo_options"], index=None,
                        horizontal=True)
        submitted = st.form_submit_button("Continue", type="primary")
    if submitted:
        missing = []
        if not name.strip():
            missing.append("a name for your start-up")
        if industry is None:
            missing.append("the industry")
        if solo is None:
            missing.append("whether you run it alone or with co-founders")
        if missing:
            st.warning("Please fill in: " + ", ".join(missing) + ".")
            return
        is_solo = solo == "Alone"
        st.session_state.solo = is_solo
        st.session_state.state = game.new_state(solo=is_solo)
        st.session_state.startup_name = name.strip()
        storage.update_session(st.session_state.code, solo=int(is_solo),
                               startup_name=name.strip(), industry=industry)
        log(text_value=f"{name.strip()} | {industry} | {solo}")
        advance()


def render_code(sc: dict) -> None:
    header()
    st.markdown('<div class="q">Your code</div>', unsafe_allow_html=True)
    st.markdown(
        "Everything you enter is stored under this code. It is the only link "
        "to your session. In one week we will share a short follow-up through "
        "the same channel you received this invitation on; you will open it "
        "with this code. Please **note it down now**."
    )
    st.code(st.session_state.code, language=None)
    if st.button("Continue", type="primary", key="code_continue"):
        log(text_value=st.session_state.code)
        advance()


def render_profile(sc: dict) -> None:
    header()
    st.markdown('<div class="q">About you and your start-up</div>',
                unsafe_allow_html=True)
    st.caption(content.DEMOGRAPHICS_INTRO)
    with st.form("profile", clear_on_submit=False):
        values = {}
        for field in content.PROFILE_FIELDS:
            if field["kind"] == "number":
                values[field["key"]] = st.number_input(
                    field["label"], min_value=field["min"],
                    max_value=field["max"], step=1, value=None)
            elif field["kind"] == "select":
                values[field["key"]] = st.selectbox(
                    field["label"], field["options"], index=None,
                    placeholder="Pick one")
            else:
                values[field["key"]] = st.text_input(field["label"])
        submitted = st.form_submit_button("Continue", type="primary")
    if submitted:
        missing = [f["label"] for f in content.PROFILE_FIELDS
                   if values.get(f["key"]) in (None, "")]
        if missing:
            st.warning("Please answer: " + "; ".join(missing) + ".")
            return
        log(text_value="; ".join(f"{k}={v}" for k, v in values.items()))
        advance()


def render_experience(sc: dict) -> None:
    header()
    st.markdown('<div class="q">How much of this have you done before?</div>',
                unsafe_allow_html=True)
    with st.form("experience", clear_on_submit=False):
        values = {}
        for field in content.EXPERIENCE_FIELDS:
            values[field["key"]] = st.radio(
                field["label"], content.EXPERIENCE_OPTIONS,
                horizontal=True, index=None)
        submitted = st.form_submit_button("Continue", type="primary")
    if submitted:
        missing = [f["label"] for f in content.EXPERIENCE_FIELDS
                   if values.get(f["key"]) is None]
        if missing:
            st.warning("Please answer: " + "; ".join(missing) + ".")
            return
        log(text_value="; ".join(f"{k}={v}" for k, v in values.items()))
        advance()


def render_risk(sc: dict) -> None:
    header()
    st.markdown('<div class="q">Three last questions about how you decide</div>',
                unsafe_allow_html=True)
    with st.form("risk", clear_on_submit=False):
        values = {}
        scale = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        for item in content.RISK_ITEMS:
            st.markdown(item["label"])
            st.caption(f'0 = {item["low"]} · 10 = {item["high"]}')
            values[item["key"]] = st.radio(
                item["label"], scale, index=None, horizontal=True,
                label_visibility="collapsed", key=f'risk_{item["key"]}')
        submitted = st.form_submit_button("Continue", type="primary")
    if submitted:
        missing = [item["label"] for item in content.RISK_ITEMS
                   if values.get(item["key"]) is None]
        if missing:
            st.warning("Please answer each of the three questions.")
            return
        log(text_value="; ".join(f"{k}={v}" for k, v in values.items()))
        advance()


def render_warmup_intro(sc: dict) -> None:
    header()
    st.subheader(content.WARMUP_INTRO["title"])
    st.markdown(content.WARMUP_INTRO["body"])
    if st.button("Continue", type="primary", key="warmup_continue"):
        advance()


def render_practice_name(sc: dict) -> None:
    header()
    st.caption(content.PRACTICE_NAME["intro"])
    st.markdown(f'<div class="q">{content.PRACTICE_NAME["question"]}</div>',
                unsafe_allow_html=True)
    st.markdown(content.PRACTICE_NAME["options_label"])
    choice = st.radio(content.PRACTICE_NAME["product_label"],
                      content.PRACTICE_NAME["options"], index=None,
                      key="practice_name_choice")
    if st.button("Continue", type="primary", key="practice_name_continue"):
        if choice is None:
            st.warning("Please pick one.")
            return
        log(text_value=choice)
        advance()


def render_practice_range(sc: dict) -> None:
    header()
    half = sc["half"]
    spec = content.PRACTICE_RANGE[half]
    if half == "low":
        st.caption(content.PRACTICE_RANGE["intro"])
    st.markdown(f'<div class="q">{spec["question"]}</div>',
                unsafe_allow_html=True)
    st.markdown(spec["prompt"])
    value = st.number_input("cups", min_value=0, max_value=5000, step=1,
                            value=None, label_visibility="collapsed",
                            key=f"practice_{half}_value")
    if st.button("Continue", type="primary", key=f"practice_{half}_continue"):
        if value is None:
            st.warning("Please enter a number.")
            return
        log(numeric_value=float(value))
        advance()


def render_starting_situation(sc: dict) -> None:
    header()
    st.subheader(content.STARTING_SITUATION["title"])
    st.markdown(content.STARTING_SITUATION["intro"])
    rows = game.report_rows(st.session_state.state)
    for i in range(0, len(rows), 3):
        cols = st.columns(3)
        for col, (label, value, help_text) in zip(cols, rows[i:i + 3]):
            col.metric(label, value, help=help_text)
    st.caption(content.STARTING_SITUATION["footer"])
    if st.button("Start the first area", type="primary",
                 key="starting_continue"):
        advance()


def render_block_intro(sc: dict) -> None:
    header()
    block = content.BLOCKS[sc["domain"]]
    st.markdown(f'<div class="sit">{st.session_state.get("startup_name", "")}</div>',
                unsafe_allow_html=True)
    st.subheader(block["title"])
    st.markdown(solo_variant(block, "intro"))
    if st.button("Continue", type="primary", key=f"intro_{sc['domain']}_continue"):
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
    scenario_popover(spec)

    labels, keys = [], []
    for opt in spec["options"]:
        label = opt.get("label_solo") if st.session_state.solo \
            and "label_solo" in opt else opt["label"]
        if opt.get("extra"):
            label = f'{label}  ·  {opt["extra"]}'
        labels.append(label)
        keys.append(opt["key"])

    choice = st.radio("Options", labels, index=None,
                      label_visibility="collapsed", key=f"choice_{node_id}")
    if st.button("Continue", type="primary", key=f"choice_{node_id}_continue"):
        if choice is None:
            st.warning("Please select one of the options.")
            return
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
    scenario_popover(spec)

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

    choice = st.radio("Options", labels, index=None,
                      label_visibility="collapsed", key=f"contest_{node_id}")
    if st.button("Continue", type="primary", key=f"contest_{node_id}_continue"):
        if choice is None:
            st.warning("Please select one of the options.")
            return
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
    scenario_popover(spec)

    value = st.number_input(
        spec["unit"], min_value=float(spec["min_value"]),
        max_value=float(spec["max_value"]), step=1.0, value=None,
        label_visibility="collapsed", format="%g",
        key=f"interval_{sc['id']}_value")
    st.caption(f'in {spec["unit"]}')

    # Check for reversed order: the second half can see the first half's value
    # and warn if the new value makes the pair implausible.
    sibling_half = "pessimistic" if half == "optimistic" else "optimistic"
    sibling_suffix = "pes" if sibling_half == "pessimistic" else "opt"
    sibling_id = f"{node_id}_{sibling_suffix}"
    sibling_rows = [r for r in storage.fetch_responses(st.session_state.code)
                    if r["screen_id"] == sibling_id]
    sibling_value = sibling_rows[0]["numeric_value"] if sibling_rows else None

    if value is not None and sibling_value is not None:
        opt_value = value if half == "optimistic" else sibling_value
        pes_value = value if half == "pessimistic" else sibling_value
        if abs(opt_value - pes_value) < 1e-9:
            st.info("You entered the same value for both. If you meant to give "
                    "a range, change one of them.")

    if st.button("Continue", type="primary", key=f"interval_{sc['id']}_continue"):
        if value is None:
            st.warning("Please enter a number.")
            return
        log(numeric_value=float(value))
        advance()


def render_report(sc: dict) -> None:
    header()
    st.session_state.state = game.advance_block(st.session_state.state)
    st.markdown('<div class="sit">Where things stand</div>',
                unsafe_allow_html=True)
    rows = game.report_rows(st.session_state.state)
    for i in range(0, len(rows), 3):
        cols = st.columns(3)
        for col, (label, value, help_text) in zip(cols, rows[i:i + 3]):
            col.metric(label, value, help=help_text)
    if st.button("Continue", type="primary", key=f"report_{sc['domain']}_continue"):
        advance()


def render_suspicion(sc: dict) -> None:
    header()
    st.markdown(content.SUSPICION["intro"])
    st.markdown(f'<div class="q">{content.SUSPICION["question"]}</div>',
                unsafe_allow_html=True)
    st.caption(content.SUSPICION["prompt"])
    with st.form("suspicion", clear_on_submit=False):
        answer = st.text_area("Your answer", height=140,
                              label_visibility="collapsed")
        submitted = st.form_submit_button("Continue", type="primary")
    if submitted:
        if not answer.strip():
            st.warning("Please write a short answer, even one sentence is fine.")
            return
        log(text_value=answer.strip())
        advance()


def render_end(sc: dict) -> None:
    storage.complete_session(st.session_state.code)
    st.title(content.END["title"])
    st.markdown(content.END["body"].format(
        code=st.session_state.code,
        contact=content.END["contact"],
        weeks=content.END["weeks"],
    ))
    st.balloons()


RENDERERS = {
    "consent": render_consent, "filter": render_filter, "setup": render_setup,
    "code": render_code,
    "profile": render_profile, "experience": render_experience,
    "risk": render_risk,
    "warmup_intro": render_warmup_intro,
    "practice_name": render_practice_name,
    "practice_range": render_practice_range,
    "starting_situation": render_starting_situation,
    "block_intro": render_block_intro,
    "choice": render_choice, "contest": render_contest,
    "interval": render_interval,
    "report": render_report,
    "suspicion": render_suspicion,
    "end": render_end,
}


# ---------------------------------------------------------------------------

if st.query_params.get("view") == "admin":
    from sim import admin
    admin.render()
elif st.session_state.get("declined"):
    st.title(content.CONSENT["title"])
    st.markdown(content.DECLINED)
elif st.session_state.get("not_founder"):
    st.markdown(content.THANK_YOU_NOT_FOUNDER)
else:
    sc = screen()
    RENDERERS[sc["kind"]](sc)
