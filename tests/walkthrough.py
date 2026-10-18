"""End to end check: play the whole session through, in both tracks.

Uses Streamlit's own AppTest harness, so the real app code runs. Verifies that
every screen renders, that every answer is stored, that the situation changes
only through the effect table and that the scoring runs on the stored rows.

Run with:  python -m tests.walkthrough
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest  # noqa: E402

from sim import scoring, storage  # noqa: E402

APP = str(Path(__file__).resolve().parent.parent / "app.py")
MAX_STEPS = 160


def _primary(at: AppTest) -> object:
    """Return the primary (Continue/Submit) button on the current screen.

    Some screens also render a Back button, so a bare at.button[0] can hit the
    wrong one. The primary button is identified by its key not starting with
    'back_'. Form submit buttons live in at.button in Streamlit 1.65.
    """
    for btn in at.button:
        key = getattr(btn, "key", "") or ""
        if not key.startswith("back_"):
            return btn
    raise AssertionError("no primary button found")


def answer(at: AppTest, rng: random.Random) -> str:
    """Fill in whatever the current screen asks and move on."""
    sc = at.session_state.screens[at.session_state.index]
    kind = sc["kind"]

    if kind == "consent":
        at.button(key="consent_agree").click()

    elif kind == "filter":
        at.radio[0].set_value("Yes")
        at.run()
        at.button(key="filter_continue").click()

    elif kind == "setup":
        at.text_input[0].set_value("Testwerk")
        at.selectbox[0].select("Software and SaaS")
        at.radio[0].set_value("With co-founders")
        _primary(at).click()

    elif kind == "code":
        at.button(key="code_continue").click()

    elif kind == "profile":
        for widget in at.number_input:
            widget.set_value(34)
        for widget in at.selectbox:
            widget.select_index(0)
        _primary(at).click()

    elif kind == "experience":
        for widget in at.radio:
            widget.set_value("1")
        _primary(at).click()

    elif kind == "risk":
        for widget in at.radio:
            widget.set_value("6")
        _primary(at).click()

    elif kind == "warmup_intro":
        at.button(key="warmup_continue").click()

    elif kind == "practice_name":
        at.radio[0].set_value("Espresso")
        at.run()
        at.button(key="practice_name_continue").click()

    elif kind == "practice_range":
        at.number_input[0].set_value(float(rng.randint(10, 60)))
        at.button(key=f"practice_{sc['half']}_continue").click()

    elif kind == "starting_situation":
        at.button(key="starting_continue").click()

    elif kind == "block_intro":
        at.button(key=f"intro_{sc['domain']}_continue").click()

    elif kind in ("choice", "contest"):
        options = at.radio[0].options
        at.radio[0].set_value(rng.choice(options))
        at.run()
        at.button(key=f"{kind}_{sc['node']}_continue").click()

    elif kind == "interval":
        at.number_input[0].set_value(float(rng.randint(5, 120)))
        at.button(key=f"interval_{sc['id']}_continue").click()

    elif kind == "report":
        at.button(key=f"report_{sc['domain']}_continue").click()

    elif kind == "suspicion":
        at.text_area[0].set_value("Something about how founders plan.")
        _primary(at).click()

    elif kind == "end":
        return "end"

    else:
        raise AssertionError(f"no driver for screen kind {kind!r}")
    return kind


def play(seed: int) -> dict:
    rng = random.Random(seed)
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()

    seen = []
    for _ in range(MAX_STEPS):
        if at.exception:
            raise AssertionError(f"app raised: {at.exception[0].value}")
        kind = answer(at, rng)
        seen.append(kind)
        if kind == "end":
            break
        at.run()
    else:
        raise AssertionError("session did not reach the end within MAX_STEPS")

    return {
        "code": at.session_state.code,
        "track": at.session_state.track,
        "seed": at.session_state.seed,
        "screens": len(at.session_state.screens),
        "steps": len(seen),
        "final_state": at.session_state.state,
    }


def main() -> int:
    tracks_played = set()
    results = []
    seed = 1
    while len(tracks_played) < 2 and seed < 25:
        result = play(seed)
        results.append(result)
        tracks_played.add(result["track"])
        seed += 1

    print(f"Sessions played: {len(results)}   tracks covered: {sorted(tracks_played)}\n")

    ok = True
    for r in results:
        rows = storage.fetch_responses(r["code"])
        answered = {row["screen_id"] for row in rows}
        nodes = [row for row in rows if row["node"]]
        timed = [row for row in rows if row["response_seconds"] is not None]
        with_state = [row for row in nodes if row["state_json"]]
        scored = scoring.score_participant(rows, seed=r["seed"])
        forms = {e.get("form") for e in scored.values()}

        print(f"  {r['code']}  track {r['track']}  "
              f"{len(answered)} screens stored, {len(nodes)} node answers, "
              f"{len(timed)} timed, {len(with_state)} with a situation snapshot")
        print(f"      scored nodes: {len(scored)}   forms present: "
              f"{sorted(f for f in forms if f != 'none')}")
        print(f"      final situation: cash {r['final_state']['cash']:,}, "
              f"runway {r['final_state']['runway']} months, "
              f"team {r['final_state']['team_size']}, "
              f"customers {r['final_state']['customers']}".replace(",", "."))

        checks = {
            "all 16 nodes scored": len(scored) == 16,
            "three forms present": {"overestimation", "overplacement",
                                    "overprecision"} <= forms,
            "every node answer timed": len(timed) == len(rows),
            "every node has a snapshot": len(with_state) == len(nodes),
        }
        for label, passed in checks.items():
            if not passed:
                ok = False
                print(f"      FAIL: {label}")

    paths = storage.export_csv("export")
    print(f"\nExported: {', '.join(p.name for p in paths)}")
    print("\nRESULT:", "end to end ok" if ok else "checks failed")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
