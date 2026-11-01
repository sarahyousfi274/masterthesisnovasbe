"""Follow-up questionnaire one week after the session (release 0.15.0).

A short self-report, opened from a personal link (`?fu=<token>`), followed by
the debriefing. It runs inside the same app and looks like the simulation, but
it never creates a session, never touches the track allocation and never
writes to the simulation's answer rows. Its answers go to `followup_responses`,
linked only by the pseudonym code.

Contents (spec of 30 October 2026, version 3):
- 12 new items, one per measured decision of the simulation (`SR_<node>`),
  in the format of Costa et al. (2026);
- 4 unchanged items of Costa et al. (2026) as anchors;
- 1 control row ("please select 3").

Screens: FU0 welcome, FU1 current founder, FU2 to FU5 statements, FU6 to FU9
forecasts (current founders only), FU-D0 interstitial, FU10 debriefing.
"""

from __future__ import annotations

import csv
import io
import random
import secrets
import statistics
import time
from datetime import date, datetime, timedelta, timezone

import streamlit as st

from . import content, storage, ui

# ---------------------------------------------------------------------------
# Settings (the team sets the two dates before release)
# ---------------------------------------------------------------------------

BASE_URL = "https://decisions-in-founding.streamlit.app/"
SIM_CLOSES = date(2026, 11, 5)          # last day on which new people can play
FOLLOWUP_CLOSES = date(2026, 11, 19)    # after this day every link shows the debriefing
DUE_DAYS = 7                            # invitation due 7 days after completion
FAST_SECONDS_PER_ITEM = 2.0             # insufficient effort flag (Huang et al. 2012)
TEST_DOMAIN = "@example.com"            # never invited
SCALE = ["1", "2", "3", "4", "5", "6", "7"]
SCALE_ENDS = ("1 · Not confident at all", "Very confident · 7")


def closes_text(d: date) -> str:
    return f"{d.day} {d.strftime('%B %Y')}"


# ---------------------------------------------------------------------------
# Items (mirrored in sim/codebook.json under "followup"; a test keeps them equal)
# ---------------------------------------------------------------------------

def _item(item_id, item_type, node, sim_area, form, template, wording, matches=None,
          unit=None, **extra):
    return {"id": item_id, "item_type": item_type, "node": node, "sim_area": sim_area,
            "form": form, "template": template, "matches": matches, "wording": wording,
            "unit": unit, **extra}


STATEMENTS = [
    # 5.1 Overestimation: confidence in reaching what was planned
    _item("SR_T1", "new", "T1", "T", "overestimation", "OESTI06",
          "My startup can build a new version of its product within the time I plan for it."),
    _item("SR_F1", "new", "F1", "F", "overestimation", "OESTI07",
          "My startup can close a funding round within the time I plan for it."),
    _item("SR_H1", "new", "H1", "H", "overestimation", "OESTI01",
          "My startup can fill an open position within the time I plan for it."),
    _item("SR_G1", "new", "G1", "G", "overestimation", "OESTI04",
          "My startup knows its customers well enough to pick the right sales channel "
          "without much testing."),
    # 5.1 Overplacement: confidence in doing better than other startups
    _item("SR_T2", "new", "T2", "T", "overplacement", "OPLAC09",
          "When my startup competes with other startups for a prize at a pitch event, "
          "it does better than most of them."),
    _item("SR_F2", "new", "F2", "F", "overplacement", "OPLAC12",
          "When my startup competes with other startups for funding, for example from an "
          "accelerator, it does better than most of them."),
    _item("SR_H2", "new", "H2", "H", "overplacement", "OPLAC01",
          "When my startup competes with other startups for a strong candidate, it does "
          "better than most of them."),
    _item("SR_G2", "new", "G2", "G", "overplacement", "OPLAC10",
          "When my startup competes with other startups for a large customer, it does "
          "better than most of them."),
    # 5.3 Anchors: Costa et al. (2026, 1500), word for word
    _item("OESTI01", "anchor", None, "H", "overestimation", "OESTI01",
          "What is your level of confidence in your ability to control hiring and firing "
          "decisions?", matches="SR_H1"),
    _item("OPLAC07", "anchor", None, "F", "overplacement", "OPLAC07",
          "I believe that the management of my working capital (cash, inventory, and "
          "accounts receivable) is better than that of my competitors.", matches="SR_F2"),
    _item("OESTI04", "anchor", None, "G", "overestimation", "OESTI04",
          "I have extensive knowledge about my customers, which helps me make decisions "
          "regarding new sales opportunities.", matches="SR_G1"),
    _item("OPLAC10", "anchor", None, "G", "overplacement", "OPLAC10",
          "I have better knowledge of the market and business expansion opportunities "
          "compared to my competitors.", matches="SR_G2"),
    # Control row (Costa et al. 2026, 1488)
    _item("CTRL3", "control", None, None, None, "control",
          "To show that you are reading carefully, please select 3 for this row."),
]

FORECASTS = [
    _item("SR_T3", "new", "T3", "T", "overprecision", "format_only",
          "How many weeks will your startup need for its next major product release, "
          "for example a new version or a major feature?", unit="weeks",
          min=0, max=260, option="na",
          option_label="No major release planned in the next 12 months"),
    _item("SR_F3", "new", "F3", "F", "overprecision", "OPREC04",
          "What will your startup's monthly revenue be in 12 months, in euros?", unit="eur",
          min=0, max=10_000_000, option="withheld",
          option_label="I prefer not to give numbers"),
    _item("SR_H3", "new", "H3", "H", "overprecision", "format_only",
          "How many weeks will it take to fill your startup's next open position, from the "
          "start of the search to a signed contract?", unit="weeks",
          min=0, max=104, option="na",
          option_label="No hire planned in the next 12 months"),
    _item("SR_G3", "new", "G3", "G", "overprecision", "OPREC14",
          "How many new paying customers will your startup win over the next 12 months?",
          unit="customers", min=0, max=10_000_000, option=None, option_label=None),
]

ITEMS = {i["id"]: i for i in STATEMENTS + FORECASTS}
NEW_ITEMS = [i for i in STATEMENTS + FORECASTS if i["item_type"] == "new"]
CODEBOOK_FIELDS = ("item_type", "node", "sim_area", "form", "template", "matches",
                   "wording", "unit")
UNIT_HINT = {"weeks": "weeks", "eur": "€", "customers": "customers"}
UNIT_TEXT = {"weeks": "in weeks", "eur": "in euros", "customers": "number of customers"}

CONSTRUCTION = [
    "One new item per measured decision: 4 areas x 3 forms = 12 items. The outcome "
    "nodes (F4, H4, G4) and K1 get no item, because they do not measure a form.",
    "Same action as the node, applied to the participant's own startup (Ajzen and "
    "Fishbein 1977). The target differs on purpose: questions about Lumora would bring "
    "back the consistency motive the time lag is meant to weaken.",
    "Format of Costa et al. (2026): statements rated for confidence from 1 to 7 (pp. 1488, "
    "1514); for overprecision a lowest and a highest estimate, followed by the confidence "
    "rating (p. 1514).",
    "Parallel wording within a form: every statement starts with 'My startup'; "
    "overestimation items name a plan or a first choice; overplacement items read 'When "
    "my startup competes with other startups for ..., it does better than most of them'.",
    "Units as in the simulation: weeks, euros and customers instead of Costa's "
    "percentages. The simulation asks in these units (T3, F3, H3, G3), and percentages are "
    "undefined for startups without revenue or customers.",
    "'Not applicable' only where a forecast cannot exist (no planned release, no planned "
    "hire). 'Prefer not to give numbers' only for revenue, where the confidence rating is "
    "still asked.",
    "4 anchors unchanged: they come from Costa's retained items, fit the areas H, F and G, "
    "and each has a matching new item.",
    "Former founders answer all statements for their most recent startup, as they saw it "
    "at the time, and skip the forecasts.",
]

# ---------------------------------------------------------------------------
# Texts (English, as in the simulation)
# ---------------------------------------------------------------------------

SECTIONS = ["Welcome", "Your startup today", "Statements", "Forecasts", "What it was about"]
SECTIONS_FORMER = ["Welcome", "Your startup today", "Statements", "What it was about"]

WELCOME = {
    "title": "Your follow-up",
    "body": "Thank you for running Lumora in Decisions in Founding about a week ago. This "
            "is the short follow-up we mentioned: about 16 questions about your own "
            "startup, which take about 5 minutes. At the end, we explain what the study "
            "was about.",
    "button": "Start",
}

FOUNDER = {
    "question": "Do you currently run a startup, as a founder or co-founder?",
    "options": ["Yes", "No, not at the moment"],
}

STATEMENT_HEAD = "How confident are you in each statement?"
STATEMENT_BODY = {
    True: "Think of your current startup (if you run more than one, the one you spend most "
          "time on). 1 = not confident at all, 7 = very confident.",
    False: "Think of the startup you ran most recently, as you saw it at the time. "
           "1 = not confident at all, 7 = very confident.",
}
FORECAST_INSTRUCTION = ("A forecast for your startup. Give the lowest and the highest value "
                        "you consider realistic. Then say how confident you are in your "
                        "forecast.")
FORECAST_CONF = "What is your level of confidence in the forecast provided?"
LOW_LABEL, HIGH_LABEL = "Lowest realistic value", "Highest realistic value"
LOW_HIGH_ERROR = "The lowest value cannot be higher than the highest."

INTERSTITIAL = {
    "title": "Your follow-up",
    "body": "Before you read the explanation: would you answer the 5-minute questionnaire "
            "first? Once you have read the explanation, we can no longer use answers to it.",
    "first": "Answer the questionnaire first",
    "now": "Read the explanation now",
}

INACTIVE = ("This link is no longer active. If you have questions, write to "
            f"{content.CONTACT_EMAIL}.")
DELETED = "Your data has been deleted."

DEBRIEF_TITLE = "What the study was about"


def debrief_sections() -> list[tuple[str, str]]:
    """Section 9 of the spec. HTML is built here, so every text is escaped."""
    h = ui._h
    forms = ("<ul class='fs-fu-forms'>"
             "<li><b>Overestimation:</b> expecting to do better than you actually do.</li>"
             "<li><b>Overplacement:</b> believing you are better than others.</li>"
             "<li><b>Overprecision:</b> being too sure that your forecasts are accurate.</li>"
             "</ul>")
    return [
        ("", h("Thank you for taking part in Decisions in Founding. The simulation looked at "
               "one question: how confident founders are in their own judgments, and whether "
               "this confidence shows in their decisions. Research distinguishes three forms "
               "of overconfidence:") + forms
         + h("Several decisions in the game measured one of these forms. Examples are "
             "whether to enter a contest against other startups, or how wide to make a low "
             "and a high estimate.")),
        ("Why we did not tell you at the start",
         h("People who know that a study is about confidence often decide differently. That "
           "is why we left the topic out at the start.")),
        ("What was fictional",
         h("Lumora, its numbers and its story were invented. The contests, the tender and "
           "the raffle had no real prizes. Wherever the game showed a result, it was drawn "
           "at random and did not reflect the quality of your startup or of your "
           "decisions.")),
        ("Why the questionnaire",
         h("Most research measures overconfidence with questionnaires in which people rate "
           "their own confidence. Our follow-up asks such questions so that we can see "
           "whether what founders say about their confidence matches what they do. A bold "
           "decision is not automatically a mistake, and our results describe patterns "
           "across many founders, not any single person.")),
        ("Your data",
         ui.mail_links("Your answers are stored under a code, not your name. Your email "
                       "address is stored separately from your answers and is used only for "
                       "this follow-up and to make sure nobody plays twice. You can withdraw "
                       "all your data with the button below, or later by writing to "
                       f"{content.CONTACT_EMAIL}.")),
        ("One request",
         h("Please do not tell other founders what the study is about before "
           f"{closes_text(SIM_CLOSES)}, because it would change how they play. You are still "
           "very welcome to forward the link to the simulation.")),
    ]


WITHDRAW = {
    "confirm": "I want to withdraw all my data from this study.",
    "button": "Withdraw all my data",
}

# ---------------------------------------------------------------------------
# Order (seeded by the token, so it is the same when someone comes back)
# ---------------------------------------------------------------------------

PAGE_SIZES = (4, 3, 3, 3)
STATEMENT_PAGES = (2, 3, 4, 5)
FORECAST_PAGES = (6, 7, 8, 9)


def order(token: str) -> dict:
    """Statement pages (control never on the first page) and forecast order."""
    rng = random.Random(token)
    rows = [i["id"] for i in STATEMENTS if i["id"] != "CTRL3"]
    rng.shuffle(rows)
    rows.insert(rng.randint(PAGE_SIZES[0], len(rows)), "CTRL3")
    pages, start = [], 0
    for size in PAGE_SIZES:
        pages.append(rows[start:start + size])
        start += size
    forecasts = [i["id"] for i in FORECASTS]
    rng.shuffle(forecasts)
    return {"statements": pages, "forecasts": forecasts,
            "position": {item: n + 1 for n, item in enumerate(rows)},
            "forecast_position": {item: n + 1 for n, item in enumerate(forecasts)}}


def page_items(page: int, plan: dict) -> list[str]:
    if page in STATEMENT_PAGES:
        return plan["statements"][STATEMENT_PAGES.index(page)]
    if page in FORECAST_PAGES:
        return [plan["forecasts"][FORECAST_PAGES.index(page)]]
    return []


def questionnaire_pages(current_founder: bool | None) -> list:
    pages = ["FU0", "FU1", *STATEMENT_PAGES]
    if current_founder:
        pages += list(FORECAST_PAGES)
    return pages


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).isoformat(timespec="seconds")


def _parse(value) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def followup_closed(today: date | None = None) -> bool:
    return (today or _now().date()) > FOLLOWUP_CLOSES


def link(token: str, debrief: bool = False) -> str:
    return f"{BASE_URL}?fu={token}" + ("&view=debrief" if debrief else "")


def _ss():
    return st.session_state


# Follow-up pieces in the simulation's design system (cards, type scale, colors).
CSS = f"""
<style>
div[class*="st-key-fu_row_"] {{ background: {ui.CARD}; border: 1px solid {ui.LINE};
  border-radius: 14px; padding: 0.85rem 1rem 0.55rem 1rem; gap: 0.35rem; }}
.fs-fu-st {{ font-size: 1rem; font-weight: 500; color: {ui.INK}; line-height: 1.45;
  padding-bottom: 0.6rem; }}
.fs-fu-conf {{ font-size: 0.875rem; font-weight: 500; color: {ui.INK_2}; margin-top: 0.4rem;
  padding-bottom: 0.45rem; }}
/* The 1 to 7 scale stays on one line, down to 320 px phones. */
div[class*="st-key-fu_row_"] div[data-testid="stButtonGroup"] > div[role="radiogroup"],
div[class*="st-key-fu_row_"] div[data-testid="stButtonGroup"] > div[role="group"] {{
  flex-wrap: nowrap !important; gap: 0.4rem !important; }}
div[class*="st-key-fu_row_"] div[data-testid="stButtonGroup"] button {{
  flex: 1 1 0 !important; min-width: 0 !important; padding-left: 0 !important;
  padding-right: 0 !important; justify-content: center !important; }}
@media (max-width: 400px) {{
  div[class*="st-key-fu_row_"] {{ padding: 0.75rem 0.7rem 0.5rem 0.7rem; }}
  div[class*="st-key-fu_row_"] div[data-testid="stButtonGroup"] > div {{ gap: 0.25rem !important; }}
}}
.fs-fu-forms {{ margin: 0.5rem 0 0.7rem 1.1rem; padding: 0; }}
.fs-fu-forms li {{ margin: 0.25rem 0; }}
.fs-fu-debrief .row:first-child .b {{ font-size: 1rem; }}
</style>
"""


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render(token: str, view: str | None = None) -> None:
    """Entry point from app.py for `?fu=<token>`."""
    ss = _ss()
    st.markdown(CSS, unsafe_allow_html=True)
    if ss.get("fu_deleted"):
        ui.eyebrow(content.CONSENT["title"])
        st.title(DELETED)
        return
    try:
        row = storage.followup_by_token(token)
    except Exception:
        row = None
    if not row or row.get("withdrawn"):
        _inactive()
        return
    code = row["code"]
    if ss.get("fu_code") != code:                 # first run of this browser session
        ss.fu_code = code
        ss.fu_answers = {r["item_id"]: r for r in storage.followup_answers(code)}
        ss.fu_founder = None if row.get("current_founder") is None else bool(row["current_founder"])
        ss.fu_page = None
        ss.fu_entered = {}
        if not row.get("opened_at"):
            storage.set_followup_once(code, "opened_at", _iso())
    open_for_questions = (row.get("fu_type") != "debrief_only" and row.get("completed_at")
                          and not row.get("fu_completed_at") and not row.get("debrief_viewed_at")
                          and not followup_closed() and not ss.get("fu_debrief"))
    if not open_for_questions:
        _debrief(code, with_bar=bool(ss.get("fu_finished")))
        return
    if view == "debrief" and not ss.get("fu_answer_first"):
        _interstitial()
        return
    _questionnaire(code, token)


def _inactive() -> None:
    ui.eyebrow(content.CONSENT["title"])
    st.title("Follow-up")
    ui.html_block(f'<p class="fs-plain">{ui.mail_links(INACTIVE)}</p>')


def _bar(current: str, progress: float) -> None:
    """The simulation's dark green top panel (same classes as ui.steps), without
    its rule that folds the simulation's intro sections into one chip."""
    sections = SECTIONS if _ss().get("fu_founder") is not False else SECTIONS_FORMER
    idx = sections.index(current)
    chips = []
    for i, sec in enumerate(sections):
        cls = "done" if i < idx else "now" if i == idx else ""
        pos = (f'<span class="pos"> · {i + 1} of {len(sections)}</span>'
               if cls == "now" else "")
        chips.append(f'<div class="fs-step {cls}">{ui._h(sec)}{pos}</div>')
    pct = max(2, min(100, round(progress * 100)))
    ui.html_block(f'<div class="fs-top"><div class="fs-steps">{"".join(chips)}</div>'
                  f'<div class="fs-bar"><div style="width:{pct}%"></div></div></div>')


def _interstitial() -> None:
    t = INTERSTITIAL
    ui.eyebrow(content.CONSENT["title"])
    st.title(t["title"])
    st.markdown(t["body"])
    c1, c2 = st.columns([1.2, 1])
    if c1.button(t["first"], type="primary", key="fu_first", use_container_width=True):
        _ss().fu_answer_first = True
        st.query_params.pop("view", None)
        st.rerun()
    if c2.button(t["now"], key="fu_now", use_container_width=True):
        _ss().fu_debrief = True
        st.rerun()


def _start_page(plan: dict) -> object:
    """Where a (re)opened questionnaire starts: the first page without saved answers."""
    ss = _ss()
    answers, founder = ss.fu_answers, ss.fu_founder
    if founder is None:
        return "FU0" if not answers else "FU1"
    for page in questionnaire_pages(founder)[2:]:
        if any(item not in answers for item in page_items(page, plan)):
            return page
    return "DONE"


def _questionnaire(code: str, token: str) -> None:
    ss = _ss()
    plan = order(token)
    if ss.fu_page is None:
        ss.fu_page = _start_page(plan)
    page = ss.fu_page
    if page == "DONE":
        _finish(code)
        return
    pages = questionnaire_pages(ss.fu_founder if ss.fu_founder is not None else True)
    progress = pages.index(page) / len(pages) if page in pages else 0
    ss.fu_entered.setdefault(page, time.monotonic())
    with st.container(key=f"screen_fu_{page}"):
        if page == "FU0":
            _bar("Welcome", 0.02)
            _welcome()
        elif page == "FU1":
            _bar("Your startup today", progress)
            _founder_page(code)
        elif page in STATEMENT_PAGES:
            _bar("Statements", progress)
            _statement_page(code, page, plan)
        else:
            _bar("Forecasts", progress)
            _forecast_page(code, page, plan)


def _go(page) -> None:
    ss = _ss()
    ss.fu_page = page
    ss.fu_entered.pop(page, None)
    st.rerun()


def _next(page) -> None:
    pages = questionnaire_pages(_ss().fu_founder)
    i = pages.index(page)
    _go(pages[i + 1] if i + 1 < len(pages) else "DONE")


def _back(page) -> None:
    """Back between the statement and forecast pages only."""
    pages = questionnaire_pages(_ss().fu_founder)
    i = pages.index(page)
    if i > 2 and st.button("← Back", key=f"fu_back_{page}", type="tertiary"):
        _go(pages[i - 1])


def _finish(code: str) -> None:
    ss = _ss()
    storage.update_followup(code, fu_completed_at=_iso())
    ss.fu_finished = True
    ss.fu_debrief = True
    st.rerun()


def _welcome() -> None:
    ui.eyebrow(content.CONSENT["title"])
    st.title(WELCOME["title"])
    st.markdown(WELCOME["body"])
    if st.button(WELCOME["button"], type="primary", key="fu_start"):
        _go("FU1")


def _founder_page(code: str) -> None:
    ss = _ss()
    ui.question(FOUNDER["question"])
    saved = ss.fu_founder
    choice = st.radio("Current founder", FOUNDER["options"], label_visibility="collapsed",
                      index=None if saved is None else (0 if saved else 1), key="fu_founder_choice")
    if st.button("Continue", type="primary", key="fu_founder_continue", disabled=choice is None):
        founder = choice == FOUNDER["options"][0]
        ss.fu_founder = founder
        storage.update_followup(code, current_founder=int(founder))
        _next("FU1")


def _seed_widget(key: str, value) -> None:
    """Put a saved answer back into a widget before it is drawn (Back, reopen)."""
    if key not in _ss() and value is not None:
        _ss()[key] = value


def _scale(item_id: str, label: str) -> str | None:
    saved = _ss().fu_answers.get(item_id, {}).get("confidence")
    _seed_widget(f"fu_{item_id}", str(int(saved)) if saved is not None else None)
    choice = st.pills(label, SCALE, key=f"fu_{item_id}", label_visibility="collapsed")
    ui.html_block(f'<div class="fs-scale-ends"><span>{SCALE_ENDS[0]}</span>'
                  f'<span>{SCALE_ENDS[1]}</span></div>')
    return choice


def _statement_page(code: str, page: int, plan: dict) -> None:
    ss = _ss()
    _back(page)
    n = STATEMENT_PAGES.index(page) + 1
    ui.eyebrow(f"Statements · Page {n} of {len(STATEMENT_PAGES)}")
    ui.question(STATEMENT_HEAD, STATEMENT_BODY[bool(ss.fu_founder)])
    items = page_items(page, plan)
    values = {}
    for item_id in items:
        with st.container(key=f"fu_row_{item_id}"):
            ui.html_block(f'<div class="fs-fu-st">{ui._h(ITEMS[item_id]["wording"])}</div>')
            values[item_id] = _scale(item_id, ITEMS[item_id]["wording"])
    ready = all(v is not None for v in values.values())
    if st.button("Continue", type="primary", key=f"fu_continue_{page}", disabled=not ready):
        secs = round(time.monotonic() - ss.fu_entered.get(page, time.monotonic()), 1)
        rows = [{"item_id": i, "page": page, "position": plan["position"][i],
                 "confidence": int(values[i]), "answered_at": _iso(),
                 "seconds_on_page": secs} for i in items]
        storage.save_followup_answers(code, rows)
        ss.fu_answers.update({r["item_id"]: r for r in rows})
        _next(page)


def _forecast_page(code: str, page: int, plan: dict) -> None:
    ss = _ss()
    _back(page)
    item_id = page_items(page, plan)[0]
    item = ITEMS[item_id]
    saved = ss.fu_answers.get(item_id, {})
    n = FORECAST_PAGES.index(page) + 1
    ui.eyebrow(f"Forecasts · {n} of {len(FORECAST_PAGES)}")
    ui.html_block(f'<div class="fs-body">{ui._h(FORECAST_INSTRUCTION)}</div>')
    with st.container(key=f"fu_row_{item_id}"):
        ui.html_block(f'<div class="fs-fu-st">{ui._h(item["wording"])}</div>')
        flag = False
        if item.get("option"):
            _seed_widget(f"fu_{item_id}_opt", bool(saved.get("not_applicable")
                                                  or saved.get("numbers_withheld")) or None)
            flag = st.checkbox(item["option_label"], key=f"fu_{item_id}_opt")
        na = flag and item["option"] == "na"
        withheld = flag and item["option"] == "withheld"
        for end in ("low", "high"):
            v = saved.get(f"est_{end}")
            _seed_widget(f"fu_{item_id}_{end}", int(v) if v is not None else None)
        c1, c2 = st.columns(2)
        hint = UNIT_HINT[item["unit"]]
        low = c1.number_input(LOW_LABEL, min_value=item["min"], max_value=item["max"], step=1,
                              value=None, placeholder=hint, key=f"fu_{item_id}_low",
                              disabled=na or withheld)
        high = c2.number_input(HIGH_LABEL, min_value=item["min"], max_value=item["max"], step=1,
                               value=None, placeholder=hint, key=f"fu_{item_id}_high",
                               disabled=na or withheld)
        st.caption(f"{UNIT_TEXT[item['unit']].capitalize()}, from {item['min']:,} to "
                   f"{item['max']:,}.")
        bad = (low is not None and high is not None and low > high) and not (na or withheld)
        if bad:
            st.warning(LOW_HIGH_ERROR)
        conf = None
        if not na:
            ui.html_block(f'<div class="fs-fu-conf">{ui._h(FORECAST_CONF)}</div>')
            conf = _scale(item_id, FORECAST_CONF)
    if na:
        ready = True
    elif withheld:
        ready = conf is not None
    else:
        ready = conf is not None and low is not None and high is not None and not bad
    if st.button("Continue", type="primary", key=f"fu_continue_{page}", disabled=not ready):
        secs = round(time.monotonic() - ss.fu_entered.get(page, time.monotonic()), 1)
        row = {"item_id": item_id, "page": page, "position": plan["forecast_position"][item_id],
               "confidence": None if na else int(conf),
               "est_low": None if (na or withheld) else float(low),
               "est_high": None if (na or withheld) else float(high),
               "not_applicable": na, "numbers_withheld": withheld,
               "answered_at": _iso(), "seconds_on_page": secs}
        storage.save_followup_answers(code, [row])
        ss.fu_answers[item_id] = row
        _next(page)


def _debrief(code: str, with_bar: bool = False) -> None:
    ss = _ss()
    if not ss.get("fu_debrief_logged"):
        storage.set_followup_once(code, "debrief_viewed_at", _iso())
        ss.fu_debrief_logged = True
    with st.container(key="screen_fu_debrief"):
        if with_bar:
            _bar("What it was about", 1.0)
        ui.eyebrow(content.CONSENT["title"])
        st.title(DEBRIEF_TITLE)
        rows = "".join(
            f'<div class="row">{f"<div class=h>{ui._h(t)}</div>" if t else ""}'
            f'<div class="b">{body}</div></div>' for t, body in debrief_sections())
        ui.html_block(f'<div class="fs-terms fs-fu-debrief">{rows}</div>')
        st.markdown("Thank you very much for your time.\n\n"
                    "*The Decisions in Founding team, Nova SBE*")
        st.divider()
        confirm = st.checkbox(WITHDRAW["confirm"], key="fu_withdraw_confirm")
        if st.button(WITHDRAW["button"], key="fu_withdraw", disabled=not confirm):
            storage.delete(code)
            ss.fu_deleted = True
            st.rerun()


# ---------------------------------------------------------------------------
# Admin: due list, invitations and exports (no email in the data exports)
# ---------------------------------------------------------------------------

def _last_activity(r: dict) -> datetime | None:
    times = [t for t in (_parse(r.get("progress_at")), _parse(r.get("last_answer")),
                         _parse(r.get("started_at"))) if t]
    return max(times) if times else None


def plan_invitations(now: datetime | None = None, assign: bool = True) -> list[dict]:
    """The due list (spec, Section 2): one email per address, never test
    addresses, never someone already invited. With `assign`, the chosen
    sessions get their type, due date and token."""
    now = now or _now()
    by_email: dict[str, list[dict]] = {}
    for r in storage.followup_candidates():
        email = (r.get("email") or "").strip().lower()
        if not email or email.endswith(TEST_DOMAIN):
            continue
        by_email.setdefault(email, []).append(r)
    due = []
    for email, group in by_email.items():
        if any(r.get("invited_at") for r in group):
            continue
        live = [r for r in group if not r.get("withdrawn")]
        if not live:
            continue
        done = [r for r in live if r.get("completed_at")]
        if done:
            chosen = min(done, key=lambda r: _parse(r["completed_at"]))
            fu_type, base = "followup", _parse(chosen["completed_at"])
        else:
            chosen = max(live, key=lambda r: _last_activity(r) or now)
            fu_type, base = "debrief_only", _last_activity(chosen)
        if base is None:
            continue
        due_at = base + timedelta(days=DUE_DAYS)
        if due_at > now:
            continue
        token = chosen.get("fu_token") or secrets.token_urlsafe(16)
        if assign:
            token = storage.assign_followup(chosen["code"], token, fu_type, _iso(due_at))
        due.append({"code": chosen["code"], "email": email, "fu_type": fu_type,
                    "due_at": _iso(due_at), "token": token})
    return sorted(due, key=lambda r: r["due_at"])


def test_link(code: str) -> dict | None:
    """A link for one session code, for the go-live check with a test address."""
    for r in storage.followup_candidates():
        if r["code"] == code:
            fu_type = "followup" if r.get("completed_at") else "debrief_only"
            token = storage.assign_followup(code, r.get("fu_token") or secrets.token_urlsafe(16),
                                            fu_type, _iso())
            return {"code": code, "fu_type": fu_type,
                    "link": link(token) if fu_type == "followup" else "",
                    "debrief_link": link(token, debrief=True)}
    return None


def invitations_csv(due: list[dict]) -> str:
    rows = [{"email": d["email"], "fu_type": d["fu_type"],
             "link": link(d["token"]) if d["fu_type"] == "followup" else "",
             "debrief_link": link(d["token"], debrief=True)} for d in due]
    return _csv(rows, ["email", "fu_type", "link", "debrief_link"])


def status_counts(now: datetime | None = None) -> dict:
    rows = storage.followup_candidates()
    invited = [r for r in rows if r.get("invited_at")]
    return {
        "Due": len(plan_invitations(now, assign=False)),
        "Invited": len(invited),
        "Opened": sum(1 for r in rows if r.get("opened_at")),
        "Questionnaire completed": sum(1 for r in rows if r.get("fu_completed_at")),
        "Debriefing only": sum(1 for r in invited if r.get("fu_type") == "debrief_only"),
        "Withdrawn": storage.counts()["withdrawn"],
    }


def _mean(values: list) -> float | None:
    values = [v for v in values if v is not None]
    return round(statistics.mean(values), 4) if values else None


def _b(value) -> str:
    return "" if value is None else ("true" if value else "false")


def _relwidth(low, high) -> float | None:
    if low is None or high is None or (high + low) == 0:
        return None
    return round((high - low) / ((high + low) / 2), 4)


def export_rows() -> tuple[list[dict], list[dict]]:
    """(wide, long): the two follow-up data files, joined to the simulation on
    `code` (and `node`). Neither contains an email address."""
    cands = storage.followup_candidates()
    answers = storage.followup_answers()
    by_code: dict[str, dict[str, dict]] = {}
    for a in answers:
        by_code.setdefault(a["code"], {})[a["item_id"]] = a
    # Debriefing seen before a session of the same address was completed: the
    # person knew the purpose while playing (spec, Section 2).
    debrief_by_email: dict[str, list[datetime]] = {}
    for r in cands:
        if r.get("debrief_viewed_at"):
            debrief_by_email.setdefault((r.get("email") or "").lower(), []).append(
                _parse(r["debrief_viewed_at"]))
    wide = []
    for r in cands:
        if not r.get("fu_token") and r["code"] not in by_code:
            continue
        a = by_code.get(r["code"], {})
        completed = _parse(r.get("completed_at"))
        fu_done = _parse(r.get("fu_completed_at"))
        viewed = _parse(r.get("debrief_viewed_at"))
        seen = debrief_by_email.get((r.get("email") or "").lower(), [])
        conf = {i: (a[i]["confidence"] if i in a else None) for i in ITEMS}
        row = {
            "code": r["code"], "fu_type": r.get("fu_type") or "",
            "current_founder": _b(None if r.get("current_founder") is None
                                  else bool(r["current_founder"])),
            "invited_at": r.get("invited_at") or "", "opened_at": r.get("opened_at") or "",
            "fu_completed_at": r.get("fu_completed_at") or "",
            "debrief_viewed_at": r.get("debrief_viewed_at") or "",
            "lag_days": (round((fu_done - completed).total_seconds() / 86400, 2)
                         if fu_done and completed else ""),
            "debrief_before_scale": _b(bool(viewed and fu_done and viewed < fu_done)),
            "debrief_before_completion": _b(bool(completed and any(v and v < completed
                                                                      for v in seen))),
            "control_passed": _b(None if conf["CTRL3"] is None else conf["CTRL3"] == 3),
            "fast_pages": _fast_pages(a),
        }
        for item in STATEMENTS:
            row[f"{item['id']}_conf"] = conf[item["id"]]
        for item in FORECASTS:
            x = a.get(item["id"], {})
            row[f"{item['id']}_conf"] = x.get("confidence")
            row[f"{item['id']}_low"] = x.get("est_low")
            row[f"{item['id']}_high"] = x.get("est_high")
            row[f"{item['id']}_na"] = _b(bool(x.get("not_applicable")) if x else None)
            row[f"{item['id']}_withheld"] = _b(bool(x.get("numbers_withheld")) if x else None)
            row[f"{item['id']}_relwidth"] = _relwidth(x.get("est_low"), x.get("est_high"))
        new = {i["id"]: conf[i["id"]] for i in NEW_ITEMS}
        row["SR_OE"] = _mean([new[f"SR_{n}"] for n in ("T1", "F1", "H1", "G1")])
        row["SR_OP"] = _mean([new[f"SR_{n}"] for n in ("T2", "F2", "H2", "G2")])
        row["SR_PR"] = _mean([new[f"SR_{n}"] for n in ("T3", "F3", "H3", "G3")])
        row["SR_OEOP"] = _mean([new[f"SR_{n}"] for n in ("T1", "F1", "H1", "G1",
                                                        "T2", "F2", "H2", "G2")])
        for area in ("T", "F", "H", "G"):
            vals = [v for i, v in new.items() if ITEMS[i]["sim_area"] == area and v is not None]
            row[f"SR_{area}"] = _mean(vals)
        for area in ("T", "F", "H", "G"):
            row[f"n_{area}"] = sum(1 for i, v in new.items()
                                   if ITEMS[i]["sim_area"] == area and v is not None)
        row["ANCHOR_MEAN"] = _mean([conf[i["id"]] for i in STATEMENTS
                                    if i["item_type"] == "anchor"])
        row["n_answered"] = sum(1 for i, v in conf.items()
                                if ITEMS[i]["item_type"] != "control" and v is not None)
        wide.append(row)
    long = []
    for a in answers:
        item = ITEMS.get(a["item_id"])
        if not item:
            continue
        long.append({"code": a["code"], "item_id": a["item_id"],
                     **{f: item.get(f) for f in CODEBOOK_FIELDS},
                     "page": a["page"], "position": a["position"],
                     "confidence": a["confidence"], "est_low": a["est_low"],
                     "est_high": a["est_high"],
                     "not_applicable": _b(bool(a["not_applicable"])),
                     "numbers_withheld": _b(bool(a["numbers_withheld"])),
                     "seconds_on_page": a["seconds_on_page"]})
    return wide, long


def _fast_pages(a: dict[str, dict]) -> int:
    pages: dict[int, list[dict]] = {}
    for row in a.values():
        pages.setdefault(row["page"], []).append(row)
    fast = 0
    for rows in pages.values():
        secs = rows[0].get("seconds_on_page")
        if secs is not None and secs < FAST_SECONDS_PER_ITEM * len(rows):
            fast += 1
    return fast


LONG_COLUMNS = ["code", "item_id", *CODEBOOK_FIELDS, "page", "position", "confidence",
                "est_low", "est_high", "not_applicable", "numbers_withheld",
                "seconds_on_page"]


def _csv(rows: list[dict], columns: list[str] | None = None) -> str:
    if not rows and not columns:
        return ""
    columns = columns or list(rows[0].keys())
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        writer.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in columns})
    return buffer.getvalue()


def wide_csv() -> str:
    wide, _ = export_rows()
    return _csv(wide)


def long_csv() -> str:
    _, long = export_rows()
    return _csv(long, LONG_COLUMNS)


def codebook_section() -> dict:
    """The `followup` section of sim/codebook.json, built from the items above."""
    return {
        "added_in": "0.15.0",
        "scale": {"min": 1, "max": 7, "ends": ["Not confident at all", "Very confident"]},
        "sim_closes": SIM_CLOSES.isoformat(), "followup_closes": FOLLOWUP_CLOSES.isoformat(),
        "due_days": DUE_DAYS, "fast_seconds_per_item": FAST_SECONDS_PER_ITEM,
        "items": {i["id"]: {f: i.get(f) for f in CODEBOOK_FIELDS} | (
            {"min": i["min"], "max": i["max"], "option": i["option"],
             "option_label": i["option_label"]} if i["id"] in {f["id"] for f in FORECASTS}
            else {}) for i in STATEMENTS + FORECASTS},
        "construction": CONSTRUCTION,
        "sources": [
            "Costa, Garcia, Tonelli and Moreira (2026), Journal of the International Council "
            "for Small Business 7(5): 1480-1518, doi 10.1080/26437015.2025.2562189",
            "Ajzen and Fishbein (1977), Psychological Bulletin 84(5): 888-918, "
            "doi 10.1037/0033-2909.84.5.888",
            "Podsakoff, MacKenzie, Lee and Podsakoff (2003), Journal of Applied Psychology "
            "88(5): 879-903",
            "Huang, Curran, Keeney, Poposki and DeShon (2012), Journal of Business and "
            "Psychology 27(1): 99-114, doi 10.1007/s10869-011-9231-8",
            "Hertwig and Ortmann (2008), Ethics & Behavior 18(1): 59-92",
            "Moore and Healy (2008), Psychological Review 115(2): 502-517",
        ],
    }
