# Response to the simulator check, round 4

**Release:** 0.14.0 (codebook 0.14.0) · **Date:** 25 October 2026

All items of Part A are in. Part B needs no code; B1 has an optional helper.

## Tests

| Check | Result |
|---|---|
| `tests/walkthrough.py`, all three tracks, solo and co-founder | end to end ok, 22 scored nodes per session |
| A1, interrupted at a random screen (6 sessions, all tracks, from "About you" to the final report) | stored answers identical to the uninterrupted run, apart from the `resume` row |
| A1, the same check against Postgres 16 (12 sessions) | identical; no failed writes |
| A1, resume through the email step | offered, restores the earlier session, the new one is deleted |
| A1, link of a completed session | closing page |
| A1, live in Chromium (local server) | reload, a new tab with the same link and the plain link plus the same email all continue on the same screen; `?r=` stays in the URL |
| `tests/simulate_participants.py` | r = 0.920 / 0.947 / 0.885 |
| Laptop 1366 × 640, Continue bottom | F3 621 px, G3 633 px, K1 636 px, H5 575 px, H2 561 px (unchanged) |

Still to do on the public link (Streamlit Cloud wraps the app, which cannot be
tested from here): the four A1 checks from the list.

## A1. Resume after an interruption

**Step 1.** `.streamlit/config.toml` has `[server] disconnectedSessionTTL = 3600`.

**Step 2.**
- **Table `progress`** (`code` primary key, `token` unique, `data` JSON text,
  `updated_at`), in both schemas. `delete()` and `withdraw()` remove it; it is
  not in `TABLES`, so the CSV downloads leave it out.
- **`sim/storage.py`:** `save_progress` (upsert, `@_deferred`, runs after the
  response rows of the same screen), `load_progress(token)` (flush first;
  returns the data with `completed` and `withdrawn` of its session),
  `open_progress_for_email(email, exclude)` (flush first; the latest session
  with this email that is neither completed nor withdrawn and has progress;
  `exclude` leaves out the session that asks).
- **Consent:** after `start_session`, `ss.resume_token = secrets.token_urlsafe(12)`
  and `st.query_params["r"]`. The first save is the one in `advance()` right after.
- **`advance()` and `go_back()`** save the progress before `st.rerun()`.
- **Snapshot:** the keys of the list plus `resumes` (count). `closed` as a list;
  every answer that holds an email is removed; `screens` and `sections` are
  rebuilt with `flow.build` and `flow.sections`.
- **Restore** runs before `init()`. A completed session shows the `CLOSE` page; a
  withdrawn or unknown token starts normally. One row `screen_id = "resume"`:
  `numeric_value` = seconds since the last save, `text_value` = the screen index,
  `option_index` = number of resumes. It is an upsert, so with several resumes
  the row keeps the last one and the count.
- **Email step:** after the A16 check, "Welcome back · You started this study
  earlier with this email address. Do you want to continue where you stopped?"
  with "Continue where I stopped" (deletes the new session, restores, sets
  `?r=`) and "Start again" (as before; the email row then has
  `text_value = "start_again"`).
- Area reports and the final report are computed when they are shown, from the
  state saved before them, so a reload on a report recomputes the same numbers
  and the same contest draws (seed).
- `not_founder` and "already taken part" remove `?r=` from the URL.

## A2. Theme file

Not a code change: upload `.streamlit/config.toml` (now with the `[server]` lines).

## A3. Text fixes

1. **F1 once:** in the final report, a "final" event without a change is dropped
   when the settled list has an event with the same label (`render_report`).
   "planned" stays only when F1 has no held-back effect.
2. **"Planned hires"** with "People you plan to hire. They join at the end of the
   Team area." (`STATUS_FIELDS`, `ui.hud`).
3. **F3:** 7,320 / 7,470 (+2 %) / 7,770 (+4 %) / 8,000 (+3 %), last bar "When you
   took over", caption "Monthly revenue in the months before you took over".
   Codebook `basis` sentence replaced; a note on the new series added.
4. **Follow-up wording:** consent fact "One short follow-up · A single email in
   about a week, with a 5‑minute questionnaire" (non-breaking hyphen, so "5-" does
   not end a line on phones); end page paragraph as given.
5. **Digital:** `SETUP` body and `industry_help` as given, the help filled with
   `fill()`.
6. **Contact emails:** `ui.mail_links()` turns each address into a `mailto` link
   with `white-space: nowrap`, bound to the word before by a non-breaking space.
   Used on the "already taken part" screen and in the consent sections ("Taking
   part is voluntary", "Questions?", the three student addresses). Checked in
   Chromium at 375 px and 1366 px; Safari could not be tested here.

## A4. Head of Product

`MESSAGES["H5"]`, `SCREENS["H5"]["question"]`, `SCREENS["H2"]` question and event,
`CONTEST_STORY["H2"]` and the `FS_DEV` label as given. Codebook H2 `basis` has the
note; H5 and the other basis texts never named the role.

## A5. Normal figures in running text

`tabular-nums` removed from both app-wide rules; set only on `.fs-top`, the
status card values and changes, the report change lines and the rolling numbers.
Checked on F3, G3 and H2.

## B. Before the link goes out

1. **Keep awake:** optional `.github/workflows/keep-awake.yml` opens the app every
   6 hours and clicks "Yes, get this app back up!" if it sleeps. Opening the
   welcome page stores nothing.
2. **No pushes** during fieldwork (adding the workflow is a push: do it before).
3. **Delete the test sessions** on the data page, so they do not count in
   `track_load`.

## Changed files (lines added or removed against 0.13.3)

| File | Lines | What |
|---|---|---|
| `app.py` | 131 | A1 resume block before `init()`, saves in `advance()`/`go_back()`, token at consent, email offer, resume row, closing page; A3.1, A3.5, A3.6, A4 label, version |
| `sim/storage.py` | 74 | A1 table `progress`, three new functions, `delete()`/`withdraw()` |
| `sim/content.py` | 60 | A3.2 to A3.6, A4, `RESUME_OFFER`, version |
| `sim/ui.py` | 26 | A3.2 label, A3.6 `mail_links()`, A5 |
| `sim/codebook.json` | 6 | version, F3 and H2 basis |
| `.streamlit/config.toml` | 5 | A1 step 1 |
| `tests/walkthrough.py` | 118 | A1 tests |
| `.github/workflows/keep-awake.yml` | new | B1, optional |
