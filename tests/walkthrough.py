"""End to end check: play the whole session through, in all three tracks.

Uses Streamlit's own AppTest harness, so the real app code runs. Verifies that
every screen renders, that every answer is stored, that the email is stored
apart from the answers, that Back works where offered, and that the scoring
runs on the stored rows.

Run with:  python -m tests.walkthrough
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest  # noqa: E402

from sim import content, scoring, storage  # noqa: E402

APP = str(Path(__file__).resolve().parent.parent / "app.py")
MAX_STEPS = 120


def submit(at: AppTest) -> None:
    """Click the form's submit button (the one that is not Back)."""
    for btn in at.button:
        if not (btn.key or "").startswith("back_"):
            btn.click()
            return
    raise AssertionError("no submit button")


def answer(at: AppTest, rng: random.Random, email: str) -> str:
    sc = at.session_state.screens[at.session_state.index]
    kind = sc["kind"]

    if kind == "consent":
        at.button(key="consent_agree").click()
    elif kind == "filter":
        at.radio(key="filter_choice").set_value("Yes")
        at.button(key="filter_continue").click()
    elif kind == "email":
        at.text_input(key="email_value").set_value(email)
        submit(at)
    elif kind == "profile":
        for f in content.PROFILE_FIELDS:
            w = f"profile_{f['key']}"
            if f["kind"] == "number":
                at.number_input(key=w).set_value(34 if f["key"] == "age" else max(f["min"], 3))
            elif f["kind"] == "select":
                if f["key"] == "country":
                    at.selectbox(key=w).select(f["options"][-1])
                elif f["key"] == "team_composition":
                    at.selectbox(key=w).select(rng.choice(f["options"][:2]))  # solo or team
                else:
                    at.selectbox(key=w).select(f["options"][1])
            elif f["kind"] == "pills":
                at.pills(key=w).set_value(f["options"][1])
            elif f["kind"] == "slider":
                at.select_slider(key=w).set_value(f["options"][1])
            elif f["kind"] == "multi":
                at.pills(key=w).set_value([f["options"][1], "Other"])
        at.run()   # the "Other" text fields appear
        at.text_input(key="profile_country_other").set_value("Andorra")
        at.text_input(key="profile_funding_other").set_value("Crowdfunding")
        at.button(key="profile_continue").click()
    elif kind == "experience":
        for f in content.EXPERIENCE_FIELDS:
            at.select_slider(key=f"exp_{f['key']}").set_value(f["options"][2])
        submit(at)
    elif kind == "risk":
        for item in content.RISK_ITEMS:
            at.select_slider(key=f"risk_{item['key']}").set_value(str(rng.randint(0, 10)))
        submit(at)
    elif kind == "warmup_intro":
        at.button(key="warmup_continue").click()
    elif kind == "practice_choice":
        at.radio(key="practice_choice_value").set_value("Tea")
        at.button(key="practice_choice_continue").click()
    elif kind == "practice_range":
        at.number_input(key="practice_low").set_value(10)
        at.number_input(key="practice_high").set_value(40)
        at.button(key="practice_range_continue").click()
    elif kind == "transition":
        at.button(key="transition_continue").click()
    elif kind == "setup":
        # Solo or with a co-founder: alternates by seed so both variants run.
        labels = [lab for _, lab in content.SETUP["team_options"]]
        at.radio(key="setup_team").set_value(labels[0] if email.startswith("tester1")
                                             or int(email[6:].split("@")[0]) % 2 else labels[1])
        # Pre-selected from the participant's own industry; sometimes changed.
        if rng.random() < 0.5:
            at.selectbox(key="setup_industry").select("Other")
            at.run()
            at.text_input(key="setup_industry_other").set_value("Robotics")
        at.button(key="setup_continue").click()
    elif kind == "final_intro":
        at.button(key="final_intro_continue").click()
    elif kind == "starting_situation":
        at.button(key="starting_continue").click()
    elif kind == "block_intro":
        at.button(key=f"intro_{sc['domain']}_continue").click()
    elif kind == "choice":
        node = sc["node"]
        if content.SCREENS[node].get("display") == "pills":
            w = at.pills(key=f"choice_{node}")
        else:
            w = at.radio(key=f"choice_{node}")
        w.set_value(rng.choice(w.options))
        at.button(key=f"choice_{node}_continue").click()
    elif kind == "multi":
        node = sc["node"]
        w = at.pills(key=f"multi_{node}")
        w.set_value([w.options[4]] if rng.random() < 0.8 else [w.options[0], w.options[4]])
        at.button(key=f"multi_{node}_continue").click()
    elif kind == "contest":
        node = sc["node"]
        w = at.radio(key=f"contest_{node}")
        w.set_value(rng.choice(w.options))
        at.button(key=f"contest_{node}_continue").click()
    elif kind == "rank":
        node = sc["node"]
        at.pills(key=f"rank_{node}").set_value(str(rng.randint(1, 10)))
        at.button(key=f"rank_{node}_continue").click()
    elif kind == "hire":
        node = sc["node"]
        w = at.radio(key=f"hire_{node}")
        w.set_value(rng.choice(w.options))
        at.button(key=f"hire_{node}_continue").click()
    elif kind == "interval":
        node = sc["node"]
        low, high = sorted(rng.sample(range(5, 120), 2))
        at.number_input(key=f"interval_{node}_low").set_value(low)
        at.number_input(key=f"interval_{node}_high").set_value(high)
        at.button(key=f"interval_{node}_continue").click()
    elif kind == "report":
        at.button(key=f"report_{sc['domain']}_continue").click()
    elif kind == "suspicion":
        at.text_area[0].set_value("Something about how founders plan.")
        submit(at)
    elif kind == "end":
        at.button(key="end_continue").click()
        at.run()
        assert at.session_state.screens[at.session_state.index]["kind"] == "closed"
        return "end"
    else:
        raise AssertionError(f"no driver for screen kind {kind!r}")
    return kind


def play(seed: int, try_back: bool = False) -> dict:
    rng = random.Random(seed)
    email = f"tester{seed}@example.com"
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    went_back = False
    for _ in range(MAX_STEPS):
        if at.exception:
            raise AssertionError(f"app raised: {at.exception[0].value}")
        idx = at.session_state.index
        sc = at.session_state.screens[idx]
        # Once per session: go Back from the experience screen and return.
        if try_back and not went_back and sc["kind"] == "experience":
            at.button(key="back_experience").click()
            at.run()
            assert at.session_state.index == idx - 1, "Back did not go back"
            went_back = True
            continue
        if idx > 0:
            from sim import flow
            has_back = any((b.key or "").startswith("back_") for b in at.button)
            expected = flow.back_allowed(at.session_state.screens, idx)
            assert has_back == expected, f"Back shown={has_back} on {sc['id']}"
            if sc.get("node") and has_back:
                assert at.session_state.screens[idx - 1]["kind"] == "block_intro"
        kind = answer(at, rng, email)
        if kind == "end":
            break
        at.run()
        if at.session_state.index == idx:
            warn = [w.value for w in at.warning]
            raise AssertionError(f"stuck on {sc['id']}: {warn}")
    else:
        raise AssertionError("session did not reach the end")
    return {"code": at.session_state.code, "track": at.session_state.track,
            "seed": at.session_state.seed, "email": email,
            "final_state": at.session_state.state, "solo": at.session_state.solo,
            "events": at.session_state.events}


def main() -> int:
    results, tracks, seed = [], set(), 1
    while (len(tracks) < 3 or len(results) < 4) and seed < 30:
        r = play(seed, try_back=(seed == 1))
        results.append(r)
        tracks.add(r["track"])
        seed += 1
    print(f"Sessions played: {len(results)}   tracks covered: {sorted(tracks)}\n")

    # Balanced allocation: on a fresh database the first three completed
    # sessions must use three different tracks; and 300 sequential arrivals
    # (each completing before the next starts) must split exactly 100/100/100.
    from sim import flow
    first_three = [r["track"] for r in results[:3]]
    balanced_start = sorted(first_three) == [1, 2, 3]
    load = {t: 0 for t in content.TRACKS}
    rng = random.Random(5)
    for _ in range(300):
        load[flow.assign_track(rng, load)] += 1
    print(f"  first three sessions: tracks {first_three}   300 arrivals: {load}")
    ok_balance = balanced_start and set(load.values()) == {100}

    ok = True
    for r in results:
        rows = storage.fetch_responses(r["code"])
        nodes = [row for row in rows if row["node"]]
        scored = scoring.score_participant(rows, seed=r["seed"])
        forms = {e.get("form") for e in scored.values()}
        email_in_answers = any(r["email"] in (row["text_value"] or "") for row in rows)
        print(f"  track {r['track']}  solo={r['solo']}  {len(rows)} rows, "
              f"{len(nodes)} node rows, {len(scored)} scored nodes")
        fs = r["final_state"]
        print(f"      final: cash €{fs['cash']:,}, runway {fs['runway']} mo, "
              f"team {fs['team_size']}, open roles {fs['pending_hires']}, "
              f"customers {fs['customers']}")
        for ev in r["events"][:4]:
            print(f"      event: {ev['label']}  {ev['delta']}")
        checks = {
            "22 nodes scored": len(scored) == 22,
            "three forms present": {"overestimation", "overplacement",
                                    "overprecision"} <= forms,
            "email stored apart": storage.code_for_email(r["email"]) == r["code"],
            "email not in answers": not email_in_answers,
            "every row has a snapshot": all(row["state_json"] for row in nodes),
            "every row has entered_at": all(row["entered_at"] for row in rows),
            "attention checks passed or failed cleanly":
                all("passed" in scored[n] for n in ("AC1", "AC2")),
            "four rank beliefs": all(scored[n].get("rank") for n in ("T5", "F5", "H5", "G5")),
            "hires joined the team": r["final_state"]["pending_hires"] == 0,
            "raffle is a control, not overplacement": scored["K1"]["form"] == "control",
            "G4 answered": "G4" in scored,
            # Review of 20 October 2026
            "A1 F4, H4, G4 last in their area": all(
                [row["node"] for row in nodes if row["domain"] == dom
                 and not row["screen_id"].endswith("_opt")
                 and not row["screen_id"].endswith("_pes")][-1] == last
                for dom, last in (("finance", "F4"), ("hiring", "H4"), ("gtm", "G4"))),
            "A4 T3 before T1, H3 before H1": all(
                min(i for i, row in enumerate(nodes) if row["node"] == a)
                < min(i for i, row in enumerate(nodes) if row["node"] == b)
                for a, b in (("T3", "T1"), ("H3", "H1"))),
            "A9 no outcome feedback before the final report": all(
                json.loads(row["state_json"])["customers"] == 90
                and json.loads(row["state_json"])["revenue"] == 8000
                and json.loads(row["state_json"])["morale"] == 3
                and json.loads(row["state_json"])["market_confidence"] == 3
                for row in rows if row["state_json"] and row["screen_index"]
                < next(x["screen_index"] for x in rows if x["screen_id"] == "report_final")),
            "A5 revenue at F3 is 8,000": all(
                json.loads(row["state_json"]).get("revenue_shown") == 8000
                for row in nodes if row["node"] == "F3"),
            "final report applies the held-back customers": r["final_state"]["customers"] > 90,
            "setup choice stored": any(row["screen_id"] == "setup" and row["option_key"]
                                       == ("solo" if r["solo"] else "team") for row in rows),
        }
        for label, passed in checks.items():
            if not passed:
                ok = False
                print(f"      FAIL: {label}")
    if not ok_balance:
        ok = False
        print("  FAIL: balanced track allocation")
    print("\nRESULT:", "end to end ok" if ok else "checks failed")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
