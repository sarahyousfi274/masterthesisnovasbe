# Response to the follow-up build spec (version 3, 30 October 2026)

**Release:** 0.15.0 (codebook 0.15.0) · **Date:** 1 November 2026

Everything in the spec is built. The simulation itself is unchanged: no text,
screen, score or allocation rule of 0.14.2 changed.

## 0. Checks before building

| Assumption | Result |
|---|---|
| The `followup` table holds the email per session code | Correct: `followup(code PRIMARY KEY, email, created_at, sent_at)`, written at the email step. |
| The email step cannot be skipped | Correct: it is screen 3 in every track (after consent and the founder filter), and the session moves on only with a valid address. |
| Promises in the simulation texts (Section 9) | Only "the jury announces the winner later" (pending contests) and the end page ("it also explains what the study was about"). The debriefing answers both; nothing to report. |

**Dates set with Sarah:** `SIM_CLOSES` = 5 November 2026, `FOLLOWUP_CLOSES` = 19 November 2026 (14 days later). `{CONTACT_EMAIL}` = decisions-in-founding@outlook.com, as on the consent page.

## 1. What changed

| File | Change |
|---|---|
| `sim/followup.py` (new, 880 lines) | settings, the 17 items, texts, screens FU0 to FU10 and FU-D0, order, due list, invitation file, wide and long exports, codebook section |
| `sim/storage.py` (+170 lines) | table `followup_responses` (both backends), 8 new `followup` columns plus a unique index on `fu_token` (added at startup to existing databases), follow-up rows in `delete()` and `withdraw()`, 8 new functions |
| `sim/admin.py` (+61 lines) | new section "Follow-up" |
| `app.py` (+11 lines) | `followup` import and the hook for `?fu=` after the page config, theme and version check, before resume and `init()`; release 0.15.0 |
| `sim/codebook.json` | section `followup` (items with all fields of 5.4, construction rules of 6, dates, scale, sources); version 0.15.0 |
| `sim/content.py` | version only |
| `tests/followup_walkthrough.py` (new) | the 15 paths of Section 11 |
| `README.md`, `CHANGELOG.md` | follow-up documented |

**New functions in `sim/storage.py`:** `followup_by_token`, `update_followup`
(queued), `set_followup_once` (queued, first time only), `save_followup_answers`
(queued upsert on code and item), `followup_answers`, `followup_candidates`,
`assign_followup`, `mark_followup_invited`.

**Main functions in `sim/followup.py`:** `render` (entry from `app.py`),
`order` (seeded by the token), `plan_invitations` (due list), `invitations_csv`,
`status_counts`, `export_rows` (wide and long), `test_link`, `codebook_section`.

## 2. Decisions within the spec

- **Design:** the simulation's green top panel with the follow-up's own sections
  (Welcome, Your startup today, Statements, Forecasts, What it was about), its
  cards, type scale and buttons. The 1 to 7 scale uses the same pill buttons as
  the rank questions, with "1 · Not confident at all" and "Very confident · 7"
  below; it stays on one line down to 320 px phones. The follow-up CSS sits in
  `sim/followup.py`, so `sim/ui.py` is unchanged.
- **Continue** stays disabled until every row of the page is answered; nothing
  is preselected. Back is offered between the statement and forecast pages.
- **Times** are ISO text in UTC and flags are 0/1, like every other time and flag
  in this database. The exports write `true`/`false`.
- **`debrief_before_completion`** is also set when a *different* session of the
  same address was completed after that address's debriefing was opened (the
  person knew the purpose while playing). The email itself never leaves the
  admin page.
- **Wide export** contains every code that has a follow-up token or answers.
- **"Debriefing only"** on the data page counts invited `debrief_only` rows.
- **Test link:** the data page has "Test link for one session" for the go-live
  check with an `@example.com` address, which never appears in the due list.

## 3. Tests

| Test | Result |
|---|---|
| `tests/followup_walkthrough.py`, SQLite | all 15 paths pass |
| the same against Postgres 16, fresh database | all 15 paths pass |
| migration of an existing 0.14.2 Postgres database | the 8 columns and the index are added at startup |
| `tests/walkthrough.py` | end to end ok (all tracks, resume checks) |
| `tests/simulate_participants.py` | r = 0.920 / 0.947 / 0.885 |
| Browser: laptop 1366 × 768, phones 320 × 640, 360 × 740 and 375 × 740, light and dark | all pages; scale on one line, end labels readable, no horizontal scrolling |

Scores were checked by hand for one case: SR_OE 5.5, SR_OP 3.5, SR_PR 4.25,
SR_OEOP 4.5, SR_T 3.67, SR_F 5.0, SR_H 3.33, SR_G 5.67, ANCHOR_MEAN 4.5.

## 4. Go-live (still to do on the public link)

1. Upload the files (list in the reply), in the evening when few people play.
2. Open `https://decisions-in-founding.streamlit.app/` once: the welcome page must
   appear (no "Version mismatch").
3. Play one session with `test.claude.fu@example.com`. On the data page, under
   "Follow-up" → "Test link for one session", enter its code (from
   sessions.csv) and open the link on a phone and a laptop, light and dark.
4. Delete the test session on the data page.
5. From then on, every 2 to 3 days: data page → "Due now" → download → mail
   merge → "Mark these as invited".

## 5. Email templates (Section 10 of the spec)

**Follow-up (`fu_type = followup`)**

> **Subject:** Decisions in Founding: your 5-minute follow-up
>
> Hi,
>
> about a week ago you ran Lumora in our simulation Decisions in Founding. Thank you!
>
> Here is the short follow-up we mentioned. It takes about 5 minutes, and at the end we explain what the study was about:
> {link}
>
> This is the only email you will get from us.
>
> Best wishes,
> The Decisions in Founding team, Nova SBE
>
> P.S. If you would rather not answer the questions, you can read what the study was about here: {debrief_link}

**Debriefing only (`fu_type = debrief_only`)**

> **Subject:** Decisions in Founding: what the study was about
>
> Hi,
>
> you recently started our simulation Decisions in Founding. Thank you for your time! Here you can read what the study was about, and withdraw your data if you wish:
> {debrief_link}
>
> This is the only email you will get from us.
>
> Best wishes,
> The Decisions in Founding team, Nova SBE
