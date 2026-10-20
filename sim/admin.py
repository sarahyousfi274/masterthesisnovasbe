"""Admin view: download the data and handle withdrawals.

Reached at ?view=admin and protected by ADMIN_PASSWORD in Streamlit secrets.
Participants never see it and never see a link to it. If no password is set,
the page refuses to open, so a deployed app is never accidentally public.
"""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from . import codebook, content, scoring, storage


def _password() -> str | None:
    try:
        value = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        return None
    return str(value) if value else None


def render() -> None:
    st.title("Study data")

    expected = _password()
    if not expected:
        st.error(
            "No ADMIN_PASSWORD is set, so this page stays closed. Add one to "
            "`.streamlit/secrets.toml` locally, or under Settings and Secrets in "
            "Streamlit Cloud."
        )
        return

    if not st.session_state.get("admin_ok"):
        given = st.text_input("Password", type="password")
        if st.button("Open", type="primary"):
            if given == expected:
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("Wrong password.")
        return

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    numbers = storage.counts()

    st.caption(f"Storage: {storage.describe()}")
    if storage.backend() == "sqlite":
        st.warning(
            "This app is writing to a local SQLite file. On a hosted Streamlit app "
            "that file is lost whenever the app restarts. Set DATABASE_URL in "
            "secrets before collecting real data, and download often until then."
        )

    cols = st.columns(4)
    cols[0].metric("Sessions started", numbers["started"])
    cols[1].metric("Completed", numbers["completed"])
    cols[2].metric("Withdrawn", numbers["withdrawn"])
    cols[3].metric("Answers stored", numbers["answers"])

    from . import content
    sessions = storage.fetch_all("sessions")
    done = [s for s in sessions if s.get("completed_at") and not s.get("withdrawn")]
    st.caption("Completed sessions per track (balanced allocation; the area order of "
               "each track is shown below the number)")
    tcols = st.columns(len(content.TRACKS))
    for col, (t, order) in zip(tcols, content.TRACKS.items()):
        col.metric(f"Track {t}", sum(1 for s in done if s.get("track") == t))
        col.caption(" → ".join(content.BLOCKS[d]["title"] for d in order))

    st.divider()
    st.subheader("Download")
    st.caption(
        "Sessions and responses are the analysis files. followup.csv holds the "
        "email addresses with the internal session id: personal data, keep it "
        "separate and send the follow-up from it only."
    )
    for table, label in (("sessions", "sessions.csv"),
                         ("responses", "responses.csv"),
                         ("followup", "followup.csv")):
        data = storage.table_csv(table)
        st.download_button(
            f"{label}  ({len(data.splitlines()) - 1 if data else 0} rows)",
            data=data or "", file_name=f"{stamp}-{label}", mime="text/csv",
            disabled=not data, key=f"dl_{table}")

    st.divider()
    st.subheader("Time")
    st.caption(
        "Participants never see a timer. Every answer row stores when the screen "
        "was opened (entered_at), when it was answered (answered_at) and the "
        "seconds in between (response_seconds). Sessions store their total "
        "duration once completed."
    )
    if st.button("Show time per screen"):
        import statistics
        sessions = [s for s in storage.fetch_all("sessions") if s.get("duration_seconds")]
        if sessions:
            mins = [s["duration_seconds"] / 60 for s in sessions]
            c1, c2, c3 = st.columns(3)
            c1.metric("Completed sessions", len(mins))
            c2.metric("Median duration", f"{statistics.median(mins):.1f} min")
            c3.metric("Range", f"{min(mins):.0f} to {max(mins):.0f} min")
        per_screen: dict[str, list[float]] = {}
        for row in storage.fetch_all("responses"):
            if row.get("response_seconds"):
                per_screen.setdefault(row["screen_id"], []).append(row["response_seconds"])
        if per_screen:
            table = [{"screen": k, "answers": len(v),
                      "median seconds": round(statistics.median(v), 1),
                      "max seconds": round(max(v), 1)}
                     for k, v in sorted(per_screen.items())]
            st.dataframe(table, use_container_width=True, hide_index=True)
        else:
            st.info("No answers yet.")

    st.divider()
    st.subheader("Group results so far")
    st.caption(
        "Descriptive only, and the design supports group level reading, not "
        "individual diagnosis. Withdrawn participants are left out."
    )
    if st.button("Compute"):
        sessions = [s for s in storage.fetch_all("sessions")
                    if not s.get("withdrawn") and s.get("completed_at")]
        if not sessions:
            st.info("No completed sessions yet.")
        else:
            scored = {s["code"]: scoring.score_participant(
                storage.fetch_responses(s["code"]), seed=s.get("seed") or 0)
                for s in sessions}
            summary = scoring.sample_summary(scoring.standardise(scored))
            rows = []
            for node_id in sorted(summary):
                row = summary[node_id]
                detail = ""
                if row["form"] == "overestimation":
                    detail = (f"mean distance {row['mean_distance']:+.2f}, "
                              f"{row['share_above_reference']:.0%} above reference")
                elif row["form"] == "control":
                    detail = (f"raffle entry {row['entry_rate']:.0%} "
                              f"(compare with entry in the four skill contests)")
                elif row["form"] == "overplacement" and "mean_rank" in row:
                    detail = (f"mean rank {row['mean_rank']:.1f} (average 5.5), "
                              f"{row['share_top_half']:.0%} expect the top half")
                elif row["form"] == "overplacement":
                    detail = (f"entry {row['entry_rate']:.0%} "
                              f"(break-even {row['break_even_entry_rate']:.0%})")
                elif row["form"] == "overprecision" and "median_width_ratio" in row:
                    detail = (f"width ratio {row['median_width_ratio']:.2f}, "
                              f"coverage {row['mean_expected_coverage']:.0%} "
                              f"of a {row['target_coverage']:.0%} target")
                elif "pass_rate" in row:
                    detail = f"passed by {row['pass_rate']:.0%}"
                elif "choices" in row:
                    detail = str(row["choices"])
                rows.append({"node": node_id, "form": row["form"],
                             "domain": row["domain"], "n": row["n"],
                             "result": detail})
            st.dataframe(rows, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Withdraw a participant")
    st.caption(
        "For a withdrawal by mail. Enter the email address the person wrote from "
        "(or an internal session id). Deleting removes the session, every answer and "
        "the address, and cannot be undone."
    )
    given = st.text_input("Email address or session id",
                          placeholder="name@company.com")
    col1, col2 = st.columns([1, 3])
    if col1.button("Delete", type="primary", disabled=not given.strip()):
        value = given.strip()
        code = storage.code_for_email(value) if "@" in value else value.upper()
        removed = storage.delete(code) if code else 0
        if removed:
            st.success(f"Deleted the session for {value}.")
        else:
            st.warning("No session found for that address or id.")

    st.divider()
    st.caption(f"App {content.APP_VERSION} · codebook {codebook.version()}")
