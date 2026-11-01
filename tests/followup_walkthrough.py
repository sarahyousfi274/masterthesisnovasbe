"""End-to-end check of the follow-up one week later (release 0.15.0).

Plays simulation sessions through the real app, then opens their follow-up
links with Streamlit's AppTest harness and checks the 15 paths of the build
spec (Section 11): pages, saving, order, scores, options, validation,
interruption, debriefing first, debriefing-only links, withdrawal, closed
links, isolation from the simulation, codebook fields, debriefing before
completion, one email per address, fast pages and the page config order.

Run with:  python -m tests.followup_walkthrough   (on a fresh local database)
"""

from __future__ import annotations

import json
import random
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest  # noqa: E402

from sim import content, followup, storage  # noqa: E402
from tests import walkthrough as w  # noqa: E402

APP = w.APP
RESULTS: list[tuple[str, bool, str]] = []

# The values given in the hand-checked case (path 1).
GIVEN = {"SR_T1": 5, "SR_F1": 6, "SR_H1": 4, "SR_G1": 7,
         "SR_T2": 2, "SR_F2": 3, "SR_H2": 4, "SR_G2": 5,
         "OESTI01": 6, "OPLAC07": 4, "OESTI04": 5, "OPLAC10": 3, "CTRL3": 3,
         "SR_T3": 4, "SR_F3": 6, "SR_H3": 2, "SR_G3": 5}
NUMBERS = {"SR_T3": (8, 16), "SR_F3": (9000, 15000), "SR_H3": (6, 12), "SR_G3": (10, 30)}

# Section 5.3 of the spec, character by character.
ANCHOR_TEXT = {
    "OESTI01": "What is your level of confidence in your ability to control hiring and "
               "firing decisions?",
    "OPLAC07": "I believe that the management of my working capital (cash, inventory, and "
               "accounts receivable) is better than that of my competitors.",
    "OESTI04": "I have extensive knowledge about my customers, which helps me make "
               "decisions regarding new sales opportunities.",
    "OPLAC10": "I have better knowledge of the market and business expansion opportunities "
               "compared to my competitors.",
}


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sim_session(seed: int, stop_at: int | None = None) -> tuple[str, str, str]:
    """Play a simulation session (to the end, or up to a screen index).
    Emails follow the walkthrough pattern, on a domain that is invited."""
    email = f"tester{seed}@founders-test.org"
    rng = random.Random(seed)
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    w._drive(at, rng, email, stop_at=stop_at)
    return at.session_state.code, at.session_state.resume_token, email


def open_fu(token: str, view: str | None = None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=30)
    at.query_params["fu"] = token
    if view:
        at.query_params["view"] = view
    at.run()
    return at


def token_of(code: str) -> str:
    made = followup.test_link(code)
    return made["link"].split("fu=")[1] if made["link"] else \
        made["debrief_link"].split("fu=")[1].split("&")[0]


def page(at: AppTest):
    return at.session_state.fu_page


def titles(at: AppTest) -> list[str]:
    return [t.value for t in at.title]


def answer_statement_page(at: AppTest, values: dict | None = None) -> list[str]:
    plan = followup.order(at.query_params["fu"][0] if isinstance(at.query_params["fu"], list)
                          else at.query_params["fu"])
    items = followup.page_items(page(at), plan)
    for item in items:
        v = (values or GIVEN).get(item, 4)
        at.pills(key=f"fu_{item}").set_value(str(v))
        at.run()
    at.button(key=f"fu_continue_{page(at)}").click()
    at.run()
    return items


def answer_forecast_page(at: AppTest, option: bool = False) -> str:
    token = at.query_params["fu"]
    token = token[0] if isinstance(token, list) else token
    item = followup.page_items(page(at), followup.order(token))[0]
    if option:
        at.checkbox(key=f"fu_{item}_opt").check()
        at.run()
    spec = followup.ITEMS[item]
    if not (option and spec["option"] == "withheld") and not (option and spec["option"] == "na"):
        low, high = NUMBERS[item]
        at.number_input(key=f"fu_{item}_low").set_value(low)
        at.number_input(key=f"fu_{item}_high").set_value(high)
        at.run()
    if not (option and spec["option"] == "na"):
        at.pills(key=f"fu_{item}").set_value(str(GIVEN[item]))
        at.run()
    at.button(key=f"fu_continue_{page(at)}").click()
    at.run()
    return item


def start(at: AppTest, founder: bool) -> None:
    at.button(key="fu_start").click()
    at.run()
    at.radio(key="fu_founder_choice").set_value("Yes" if founder else "No, not at the moment")
    at.run()
    at.button(key="fu_founder_continue").click()
    at.run()


def wide_row(code: str) -> dict:
    wide, _ = followup.export_rows()
    return next(r for r in wide if r["code"] == code)


def table_rows(code: str) -> dict:
    out = {}
    with storage.connect() as conn:
        for table in ("sessions", "responses", "followup", "progress", "followup_responses"):
            out[table] = len(storage._fetch(conn, f"SELECT code FROM {table} WHERE code = ?",
                                            (code,)))
    return out


# ---------------------------------------------------------------------------
# The paths
# ---------------------------------------------------------------------------

def main() -> int:

    # 1 Current founder ------------------------------------------------------
    code, _, email = sim_session(301)
    sessions_before = len(storage.fetch_all("sessions"))
    token = token_of(code)
    at = open_fu(token)
    load_fu_start = storage.track_load(content.TRACKS)
    check("15 set_page_config stays first with ?fu=", not at.exception,
          str(at.exception[0].value) if at.exception else "")
    seen = [page(at)]
    start(at, founder=True)
    stmt_pages = []
    while page(at) in followup.STATEMENT_PAGES:
        seen.append(page(at))
        stmt_pages.append(answer_statement_page(at))
    while page(at) in followup.FORECAST_PAGES:
        seen.append(page(at))
        answer_forecast_page(at)
    check("1 all pages appear (current founder)", seen == ["FU0", 2, 3, 4, 5, 6, 7, 8, 9],
          str(seen))
    check("1 debriefing after the last page", followup.DEBRIEF_TITLE in titles(at))
    rows = storage.followup_answers(code)
    check("1 every item saved once", len(rows) == 17 and len({r["item_id"] for r in rows}) == 17,
          f"{len(rows)} rows")
    check("1 control row never on the first page",
          all("CTRL3" not in followup.order(f"t{n}")["statements"][0] for n in range(2000)))
    check("1 control row not on this participant's first page", "CTRL3" not in stmt_pages[0])
    reopened = open_fu(token)
    check("1 order the same after reopening",
          followup.order(token)["statements"] == stmt_pages
          and followup.DEBRIEF_TITLE in titles(reopened))
    check("10 track_load unchanged by a whole follow-up",
          storage.track_load(content.TRACKS) == load_fu_start)
    r = wide_row(code)
    expected = {"SR_OE": 5.5, "SR_OP": 3.5, "SR_PR": 4.25, "SR_OEOP": 4.5,
                "SR_T": round((5 + 2 + 4) / 3, 4), "SR_F": 5.0,
                "SR_H": round((4 + 4 + 2) / 3, 4), "SR_G": round((7 + 5 + 5) / 3, 4),
                "ANCHOR_MEAN": 4.5, "n_answered": 16, "control_passed": "true",
                "SR_G3_relwidth": 1.0, "current_founder": "true"}
    got = {k: r[k] for k in expected}
    check("1 scores correct (hand-checked case)", got == expected, str(got))

    # 2 Former founder -------------------------------------------------------
    code2, _, _ = sim_session(302)
    at = open_fu(token_of(code2))
    start(at, founder=False)
    pages2 = []
    while page(at) in followup.STATEMENT_PAGES:
        pages2.append(page(at))
        answer_statement_page(at)
    r2 = wide_row(code2)
    check("2 former founder skips the forecasts",
          pages2 == [2, 3, 4, 5] and followup.DEBRIEF_TITLE in titles(at), str(pages2))
    check("2 SR_PR empty, n per area = 2",
          r2["SR_PR"] is None and all(r2[f"n_{a}"] == 2 for a in "TFHG"),
          str({k: r2[k] for k in ("SR_PR", "n_T", "n_F", "n_H", "n_G")}))

    # 3 Options ----------------------------------------------------------------
    code3, _, _ = sim_session(303)
    token3 = token_of(code3)
    at = open_fu(token3)
    start(at, founder=True)
    while page(at) in followup.STATEMENT_PAGES:
        answer_statement_page(at)
    while page(at) in followup.FORECAST_PAGES:
        item = followup.page_items(page(at), followup.order(token3))[0]
        answer_forecast_page(at, option=item in ("SR_T3", "SR_H3", "SR_F3"))
    r3 = wide_row(code3)
    f3 = next(x for x in storage.followup_answers(code3) if x["item_id"] == "SR_F3")
    check("3 not applicable: SR_PR from 2 ratings, n_T = n_H = 2",
          r3["SR_PR"] == round((6 + 5) / 2, 4) and r3["n_T"] == 2 and r3["n_H"] == 2
          and r3["SR_T3_na"] == "true" and r3["SR_H3_na"] == "true",
          str({k: r3[k] for k in ("SR_PR", "n_T", "n_H", "SR_T3_na", "SR_H3_na")}))
    check("3 prefer not to give numbers: no numbers, rating kept",
          f3["est_low"] is None and f3["est_high"] is None and f3["confidence"] == 6
          and bool(f3["numbers_withheld"]) and r3["n_F"] == 3)

    # 4 Validation -------------------------------------------------------------
    code4, _, _ = sim_session(304)
    token4 = token_of(code4)
    at = open_fu(token4)
    start(at, founder=True)
    while page(at) in followup.STATEMENT_PAGES:
        answer_statement_page(at)
    item = followup.page_items(page(at), followup.order(token4))[0]
    spec = followup.ITEMS[item]
    at.number_input(key=f"fu_{item}_low").set_value(20)
    at.number_input(key=f"fu_{item}_high").set_value(10)
    at.pills(key=f"fu_{item}").set_value("4")
    at.run()
    refused = (at.button(key=f"fu_continue_{page(at)}").disabled
               and any(followup.LOW_HIGH_ERROR in x.value for x in at.warning))
    at.number_input(key=f"fu_{item}_high").set_value(20)
    at.run()
    equal_ok = not at.button(key=f"fu_continue_{page(at)}").disabled
    limits = (at.number_input(key=f"fu_{item}_low").min == spec["min"]
              and at.number_input(key=f"fu_{item}_high").max == spec["max"])
    check("4 lowest > highest refused", refused)
    check("4 lowest = highest accepted", equal_ok)
    check("4 limits per unit", limits and {i["id"]: (i["min"], i["max"])
                                            for i in followup.FORECASTS}
          == {"SR_T3": (0, 260), "SR_F3": (0, 10_000_000), "SR_H3": (0, 104),
              "SR_G3": (0, 10_000_000)})

    # 5 Interruption -----------------------------------------------------------
    code5, _, _ = sim_session(305)
    token5 = token_of(code5)
    at = open_fu(token5)
    start(at, founder=True)
    answer_statement_page(at)      # FU2
    answer_statement_page(at)      # FU3
    at = open_fu(token5)           # tab closed, link opened again
    check("5 interruption after FU3 continues at FU4", page(at) == 4, str(page(at)))

    # 6 Debriefing first -------------------------------------------------------
    code6, _, _ = sim_session(306)
    token6 = token_of(code6)
    at = open_fu(token6, view="debrief")
    inter = any(b.key == "fu_now" for b in at.button)
    at.button(key="fu_now").click()
    at.run()
    shown = followup.DEBRIEF_TITLE in titles(at)
    later = open_fu(token6)
    check("6 interstitial appears", inter)
    check("6 after 'Read the explanation now' only the debriefing",
          shown and followup.DEBRIEF_TITLE in titles(later)
          and not any(b.key == "fu_start" for b in later.button))
    at = open_fu(token_of(sim_session(316)[0]), view="debrief")
    at.button(key="fu_first").click()
    at.run()
    check("6 'Answer the questionnaire first' starts the questionnaire",
          page(at) == "FU0" and any(b.key == "fu_start" for b in at.button))

    # 7 Debriefing-only link for an incomplete session ---------------------------
    code7, rtoken7, email7 = sim_session(307, stop_at=15)
    made7 = followup.test_link(code7)
    token7 = made7["debrief_link"].split("fu=")[1].split("&")[0]
    at = open_fu(token7)
    check("7 debriefing-only link: no questionnaire",
          made7["fu_type"] == "debrief_only" and not made7["link"]
          and followup.DEBRIEF_TITLE in titles(at)
          and not any(b.key in ("fu_start", "fu_now") for b in at.button))

    # 12 Debriefing before completion (continues the session of path 7) ---------
    at = AppTest.from_file(APP, default_timeout=30)
    at.query_params["r"] = rtoken7
    at.run()
    w._drive(at, random.Random(9307), email7)
    r12 = wide_row(code7)
    check("12 debrief_before_completion flagged",
          r12["debrief_before_completion"] == "true", str(r12["debrief_before_completion"]))

    # 8 Withdrawal on FU10 -------------------------------------------------------
    at = open_fu(token6)
    at.checkbox(key="fu_withdraw_confirm").check()
    at.run()
    at.button(key="fu_withdraw").click()
    at.run()
    left = table_rows(code6)
    check("8 withdrawal removes every row of the code",
          not any(left.values()) and followup.DELETED in titles(at), str(left))

    # 9 Unknown token and closed follow-up ---------------------------------------
    at = open_fu("not-a-real-token")
    check("9 unknown token message", any(followup.INACTIVE[:30] in m.value
                                         for m in at.markdown))
    code9, _, _ = sim_session(309)
    token9 = token_of(code9)
    saved = followup.FOLLOWUP_CLOSES
    followup.FOLLOWUP_CLOSES = date(2020, 1, 1)
    try:
        at = open_fu(token9)
        closed = followup.DEBRIEF_TITLE in titles(at) and not any(
            b.key == "fu_start" for b in at.button)
    finally:
        followup.FOLLOWUP_CLOSES = saved
    check("9 after FOLLOWUP_CLOSES only the debriefing", closed)

    # 13 One email per address --------------------------------------------------
    a_code, _, a_email = sim_session(313)
    b_code, _, _ = sim_session(314, stop_at=15)
    with storage.connect() as conn:
        storage._execute(conn, "UPDATE followup SET email = ? WHERE code = ?", (a_email, b_code))
    due = followup.plan_invitations(datetime.now(timezone.utc) + timedelta(days=8),
                                    assign=False)
    mine = [d for d in due if d["email"] == a_email]
    check("13 one row per address, for the completed session",
          len(mine) == 1 and mine[0]["code"] == a_code and mine[0]["fu_type"] == "followup",
          str(mine))
    check("13 test addresses never invited",
          not any(d["email"].endswith("@example.com") for d in due))
    csv_text = followup.invitations_csv(mine)
    check("13 invitation file has link and debriefing link",
          csv_text.splitlines()[0] == "email,fu_type,link,debrief_link"
          and "?fu=" in csv_text and "&view=debrief" in csv_text)

    # 14 Fast pages ----------------------------------------------------------------
    r1 = wide_row(code)
    with storage.connect() as conn:
        storage._execute(conn, "UPDATE followup_responses SET seconds_on_page = 60 "
                               "WHERE code = ? AND page <> 2", (code,))
        storage._execute(conn, "UPDATE followup_responses SET seconds_on_page = 7.9 "
                               "WHERE code = ? AND page = 2", (code,))
    r14 = wide_row(code)
    check("14 a page under 2 seconds per row counts as fast",
          r1["fast_pages"] == 8 and r14["fast_pages"] == 1,
          f"instant run {r1['fast_pages']}, one fast page {r14['fast_pages']}")

    # 10 Isolation -----------------------------------------------------------------
    sessions_after = len(storage.fetch_all("sessions"))
    # Simulation sessions this test started after path 1: 302 to 307, 309, 313,
    # 314 and 316 (ten); one of them (306) was withdrawn in path 8.
    wide_csv, long_csv = followup.wide_csv(), followup.long_csv()
    check("10 follow-up creates no session", sessions_after - sessions_before == 9,
          f"{sessions_before} -> {sessions_after}")
    check("10 follow-up CSVs carry no email column",
          "email" not in wide_csv.splitlines()[0] and "email" not in long_csv.splitlines()[0]
          and "@" not in wide_csv + long_csv)

    # 11 Codebook fields -------------------------------------------------------------
    _, long = followup.export_rows()
    fields_ok = all(all(row[f] == followup.ITEMS[row["item_id"]].get(f)
                        for f in followup.CODEBOOK_FIELDS) for row in long)
    nodes = [i["node"] for i in followup.ITEMS.values() if i["item_type"] == "new"]
    book = json.loads((Path(__file__).resolve().parent.parent / "sim" / "codebook.json")
                      .read_text(encoding="utf-8"))["followup"]["items"]
    same_book = all(book[i][f] == followup.ITEMS[i].get(f)
                    for i in followup.ITEMS for f in followup.CODEBOOK_FIELDS)
    check("11 long export carries the codebook fields", bool(long) and fields_ok)
    check("11 exactly one SR_ item per node T1 to G3",
          sorted(nodes) == sorted(f"{a}{n}" for a in "TFHG" for n in (1, 2, 3))
          and all(i == f"SR_{followup.ITEMS[i]['node']}" for i in followup.ITEMS
                  if followup.ITEMS[i]["item_type"] == "new"))
    check("11 anchors word for word", all(followup.ITEMS[k]["wording"] == v
                                          for k, v in ANCHOR_TEXT.items()))
    check("11 codebook.json matches the items", same_book)

    width = max(len(n) for n, _, _ in RESULTS)
    ok = True
    for name, passed, detail in RESULTS:
        ok &= passed
        print(f"  {'ok  ' if passed else 'FAIL'}  {name.ljust(width)}  {'' if passed else detail}")
    print("\nRESULT:", "follow-up ok" if ok else "checks failed")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
