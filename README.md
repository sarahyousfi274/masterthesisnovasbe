# Decisions in founding

A 20-minute simulation study for founders by master's students at Nova SBE.

<!-- The first paragraph above is what link previews show (Streamlit Community
Cloud takes the description from this README). Keep it neutral: it must not
name the purpose of the study. Everything below is for the research team and
the examiners only. This repository must stay private (see "Confidentiality"). -->

| | |
|---|---|
| **Release** | 0.15.0 (codebook 0.15.0), 1 November 2026 |
| **Live app** | https://decisions-in-founding.streamlit.app |
| **Stack** | Python 3.10+ (tested with 3.13), Streamlit 1.65.0 (pinned), Postgres (Neon, Frankfurt) or SQLite |
| **Institution** | Nova School of Business and Economics, Lisbon |
| **Supervisor** | Prof. João Castro |
| **Authors** | Eléonore Konsbruck, Amie Weidemann, Sarah Yousfi |
| **Contact** | decisions-in-founding@outlook.com |

---

## Contents

1. [Purpose](#1-purpose)
2. [Study design](#2-study-design)
3. [Measurement and scoring](#3-measurement-and-scoring)
4. [Data, privacy and confidentiality](#4-data-privacy-and-confidentiality)
5. [Repository structure](#5-repository-structure)
6. [Running the app locally](#6-running-the-app-locally)
7. [Deployment](#7-deployment)
8. [Fieldwork operations](#8-fieldwork-operations)
9. [Quality assurance](#9-quality-assurance)
10. [Known limitations](#10-known-limitations)
11. [Version history](#11-version-history)
12. [Authors, citation and licence](#12-authors-citation-and-licence)

---

## 1 Purpose

The app is the research instrument of our work project on **founder
overconfidence and startup performance** (Chapter 5 of the thesis). Founders
run a fictional startup, Lumora, through its first months and take 22
decisions. Each measured decision is scored against a hidden reference value
for one of the three forms of overconfidence distinguished by Moore and Healy
(2008):

| Form | What it captures | Item type |
|---|---|---|
| **Overestimation** | planning that is more aggressive than the reference (time, money, hires) | ladder of options |
| **Overplacement** | believing one's own startup is better than the others | rank belief and contest entry |
| **Overprecision** | ranges that are too narrow for the uncertainty involved | 80 % interval (low and high estimate) |

Participants are never told what is measured. The word "overconfidence" does
not appear anywhere in the app; the study is explained in the single follow-up
email a week after the session (cover story, requirement R5).

## 2 Study design

### 2.1 Session flow

About 20 minutes, 47 screens, the same in every track.

| Section | Screens |
|---|---|
| Welcome | information, consent |
| About you | founder filter, email, profile, experience, risk attitude (SOEP items, Dohmen et al. 2011) |
| How it works | overview, one example choice and one example range (not scored) |
| Your startup | solo founder or co-founders, industry, starting situation |
| First decision | F1: when fundraising starts (same position for everyone) |
| Four areas | per area: intro with the numbers, 4 to 6 decisions, end-of-area report |
| Final round | K1 (raffle), final report that settles all held-back effects and contests |
| Wrap-up | suspicion check ("What do you think this study was about?"), thank you, close |

The "About you" section has its own colour scheme (stone grey and terracotta),
clearly apart from the green simulation, as required by the supervisor.

### 2.1a Follow-up one week later

About 5 minutes, opened from a personal link (`?fu=<token>`) in the single
follow-up email, in the same design as the simulation. It is a self-report on
the participant's **own** startup and ends with the debriefing.

| Screen | Content |
|---|---|
| FU0 | welcome |
| FU1 | "Do you currently run a startup?" (current or former founder) |
| FU2 to FU5 | 13 statements rated 1 to 7, in random order: 8 new items (overestimation and overplacement), 4 unchanged anchors from Costa et al. (2026), 1 control row ("select 3"), never on the first page |
| FU6 to FU9 | current founders only: 4 forecasts (lowest and highest value, then confidence 1 to 7) |
| FU10 | debriefing: purpose, the three forms, what was fictional, data and withdrawal button |

Each new item mirrors one measured decision (`SR_T1` for T1 and so on), in the
format of Costa et al. (2026); matching item and decision follows Ajzen and
Fishbein (1977). The week between both parts weakens consistency and demand
effects (Podsakoff et al. 2003). Answers are stored apart, linked only by the
pseudonym code. Participants who did not finish get a debriefing-only email.
Opening the debriefing first shows a short interstitial; once the debriefing
has been read, the questionnaire closes for that link.

### 2.2 Areas and tracks

"Building the product" always comes first. The other three areas form a Latin
square, so each appears once in position 2, 3 and 4:

| Track | Area 1 | Area 2 | Area 3 | Area 4 |
|---|---|---|---|---|
| 1 | Building the product | Finance | Team | Go-to-market |
| 2 | Building the product | Go-to-market | Finance | Team |
| 3 | Building the product | Team | Go-to-market | Finance |

**Balanced allocation:** at consent, a new participant gets the track with the
fewest completed plus currently running sessions (running = started in the last
45 minutes); ties are broken at random. Withdrawn sessions and non-founders do
not count.

### 2.3 Decisions

| Area | Overestimation | Overprecision | Overplacement (rank, contest) | Outcome node |
|---|---|---|---|---|
| Building the product | T1 share built in-house | T3 weeks to MVP | T5, T2 pitch contest | |
| Finance | F1 start of fundraising (opening) | F3 revenue in 12 months | F5, F2 accelerator | F4 route to €300,000 |
| Team | H1 planned hires | H3 weeks to a signed contract | H5, H2 Head of Product | H4 Head of Sales |
| Go-to-market | G1 launch budget split | G3 new customers in month 9 | G5, G2 customer tender | G4 reaction to a weak first month |
| Final round | | | K1 raffle (control) | |

Plus two attention checks (AC1, AC2), placed in areas 2 and 3 of each track.

- **Order inside an area:** nodes that build on each other keep their order
  (T3 → T1, H3 → H1, G1 → G3); each rank question comes right before its
  contest; the outcome nodes F4, H4 and G4 are always last in their area.
- **Contests:** ten entrants, an independent jury, a 1 in 10 chance for an
  average entrant, an upgrade to 1 in 8. Entry costs `prize / 10 + 2,000` and
  the upgrade `prize / 8 + 4,500`, so every entry has an expected value of
  −€2,000 and every upgrade −€4,500.
- **K1** has the same numbers but is decided by lot. Entry there reflects risk
  attitude only, which separates it from the overplacement component of the
  skill contests (Camerer and Lovallo 1999).
- **Outcome nodes** (F4, H4, G4) are not overconfidence scores. They are
  coded decisions used as dependent variables.

### 2.4 How the story reacts

- Cash, costs, runway and team change at once; each area is one month of
  running costs, paid at the end of the area.
- Customers, revenue, morale and market confidence are **held back** until the
  final report, so no participant gets outcome feedback during the measured
  decisions.
- Contest results are drawn in the final report with the stated chance, from
  the session seed (a reload shows the same result).
- If the runway is below 6 months when Finance starts (only possible in Track
  3), existing investors bridge Lumora to 6 months, so the financing
  decisions start from the same position.
- All texts adapt to solo founders and co-founder teams.

## 3 Measurement and scoring

All reference values live in `sim/codebook.json`. Each node carries its
reference, `provenance` (empirical or derived), `basis`, `sources` and, where
relevant, `open` points. The written justification is the project document
*Codebook Reference Values*. G1 and G3 are model-based (`models/`).

| Form | Score |
|---|---|
| Overestimation | signed distance of the chosen option from the reference, in the node's own unit, positive = more aggressive, z-standardised across the sample |
| Overplacement | 5.5 minus the stated rank (rank questions); entry into a contest with a negative expected value, plus the size of the stake |
| Overprecision | width of the stated range over the width of the reference range (below 1 = too narrow), plus the expected coverage of the reference distribution |

`sim/scoring.py` scores one participant from the stored rows
(`score_participant`) and is used by the data page for group-level results.
Each stored row carries a snapshot of the situation at that moment
(`state_json`, including the numbers shown) as a control variable.

## 4 Data, privacy and confidentiality

### 4.1 What is stored

| Table | Content | In the analysis export |
|---|---|---|
| `sessions` | one row per participant: pseudonym code, track, seed, solo or team, industry, consent, founder filter, start and end time, duration, app and codebook version, withdrawn flag | yes |
| `responses` | one row per screen: answer, response time, timestamps, situation snapshot | yes |
| `followup` | email address, linked only by the pseudonym code; follow-up token, type, due, invited, opened, completed and debriefing times, current founder | no (separate download) |
| `progress` | where a running session stands, so it can be resumed; never the email | no |
| `followup_responses` | one row per follow-up item: rating, forecast range, options, page, position, time on page | yes, as the follow-up wide and long files |

Rows with `screen_id = "resume"` in `responses` mark a resumed session
(seconds since the last save, screen index, number of resumes). They carry no
node and are not scored; report the share of resumed sessions as a
data-quality note.

### 4.2 Privacy

- The email address is stored only in `followup` and never in the answers.
- Answers are analysed in aggregate only.
- Resuming uses a random token in the URL (`?r=…`), never the code or email.
  After a break of more than 30 minutes the app asks for the email address
  before it continues, so a forwarded link cannot open someone else's session.
- One complete run per email address; a second attempt ends on a thank-you
  screen and nothing of it is kept.
- Withdrawal within 4 weeks by email: the data page deletes every session
  linked to that address, including its progress and contact.

### 4.3 Confidentiality

**The repository must stay private.** `sim/codebook.json` holds every reference
value and the full measurement logic, and this README names the purpose of the
study. On Streamlit Community Cloud, apps from a public repository show a
GitHub and a Fork button that cannot be hidden. The app itself is set to public
in the Streamlit sharing settings, independently of the repository.

## 5 Repository structure

```
app.py                     screens, routing and resume; nothing is scored here
requirements.txt           pinned dependencies (Streamlit 1.65.0, psycopg 3)
sim/
  content.py               every text a participant sees, tracks, effects, charts
  codebook.json            hidden reference values with provenance and sources
  codebook.py              access to the codebook, quantiles, coverage
  state.py                 the company: cash, burn, runway, team, held-back effects
  flow.py                  screen order per track, randomisation, allocation
  scoring.py               scores per form and per domain
  storage.py               SQLite or Postgres, background writes, resume, export
  followup.py              follow-up one week later: items, screens, due list, exports
  admin.py                 data page at ?view=admin
  ui.py                    design system (CSS) and screen components
models/                    G1 launch model and G3 Bass model with variants
tests/                     walkthroughs (simulation and follow-up), simulated participants
assets/favicon.png         browser tab icon
.streamlit/config.toml     theme and server settings (session kept for 1 hour)
.streamlit/secrets.toml.example   template for DATABASE_URL and ADMIN_PASSWORD
.github/workflows/keep-awake.yml  opens the app every 6 hours so it never sleeps
DEPLOY.md                  hosting options and setup in detail
CHANGELOG.md               version history
REVIEW_RESPONSE_*.md       responses to the review rounds
```

The split is deliberate: `content.py` is the story participants experience;
`codebook.json` holds the reference values they never see. The story reacts
only to the effect table in `content.py`, never to a measurement result.

## 6 Running the app locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501` and writes to `data/sessions.db`
(SQLite). For the data page, copy `.streamlit/secrets.toml.example` to
`.streamlit/secrets.toml`, set `ADMIN_PASSWORD` and open `?view=admin`.

For design reviews, `FS_DEV=1 streamlit run app.py` and open
`?jump=<screen id>`, for example `?jump=F3`. Without that environment variable
the parameter does nothing.

## 7 Deployment

The study runs on **Streamlit Community Cloud** with a **Neon Postgres**
database in Frankfurt. Full instructions and alternatives are in `DEPLOY.md`.

| Setting | Where | Value |
|---|---|---|
| Main file | Streamlit app settings | `app.py` |
| `DATABASE_URL` | Streamlit secrets | Neon connection string (without it, data is lost on restart) |
| `ADMIN_PASSWORD` | Streamlit secrets | long passphrase for the data page |
| Sharing | Streamlit app settings | "This app is public and searchable" |
| Theme, session TTL | `.streamlit/config.toml` | must be at exactly this path |
| Keep awake | `.github/workflows/keep-awake.yml` | runs every 6 hours |

`app.py` and the files in `sim/` must come from the same release; a mixed
upload stops with a "Version mismatch" message instead of failing halfway
through a session. Upload hidden folders (`.streamlit`, `.github`) through
"Add file → Create new file" on GitHub, because a Mac drops them in uploads.

## 8 Fieldwork operations

**Before the link goes out**

1. Repository private, app public; check in a private browser window.
2. Delete all test sessions on the data page ("Sessions started" = 0).
3. Run the keep-awake workflow once under "Actions" (green check).
4. Send the plain link, without `?r=…`.

**While participants are active**

- **No commits to GitHub.** Every commit restarts the app; running sessions
  can resume, but they are interrupted.
- Download the CSV files from the data page once a day as a backup.
- Withdrawals: delete by email address on the data page.

**Follow-up one week later** (data page, section "Follow-up")

1. Every 2 to 3 days, open the data page. "Due now" lists every address whose
   session was completed (or last active) at least 7 days ago and that has not
   been invited yet: one row per address, never `@example.com`.
2. "Download invitations (CSV)" gives `email`, `fu_type`, `link` and
   `debrief_link` for a mail merge from the team mailbox. Use the template for
   `followup` or `debrief_only` (in `REVIEW_RESPONSE_FOLLOWUP_0.15.0.md`).
3. After sending, click "Mark these as invited". Each address gets exactly one
   email, no reminders.
4. New people can play until 5 November 2026 (`SIM_CLOSES`); questionnaire
   links close after 19 November 2026 (`FOLLOWUP_CLOSES`) and then show the
   debriefing only. Both dates are in `sim/followup.py`.
5. "Download follow-up data, wide/long (CSV)" gives the analysis files, without
   email, with all scores and flags (`control_passed`, `fast_pages`,
   `debrief_before_scale`, `debrief_before_completion`, `lag_days`).

## 9 Quality assurance

```bash
python -m tests.walkthrough             # full sessions through the real app
python -m tests.simulate_participants   # does the scoring recover known biases?
python -m tests.followup_walkthrough    # the follow-up: 15 paths of the build spec
```

| Check | Result (0.15.0) |
|---|---|
| Walkthrough, all three tracks, solo and co-founder | end to end ok, 22 scored nodes per session, email never in the answers |
| Resume after an interruption (6 sessions, random screen) | stored answers identical to an uninterrupted run |
| Resume via email, forwarded link, completed link | all pass |
| Simulated participants (n = 300) | parameter recovery r = 0.92 / 0.95 / 0.89; cross-correlations below 0.07 |
| Browser run (laptop 1366 × 768, phones 320 to 375 px, dark mode) | all 47 screens, no horizontal scrolling, no text below 12.5 px |
| Live run on the public link (0.14.2) | complete session, reload, completed link and second-run block confirmed |
| Follow-up walkthrough (SQLite and Postgres 16, including the migration of an existing database) | all 15 paths pass: pages, saving, order, scores checked by hand, options, validation, interruption, debriefing first, debriefing-only, withdrawal, closed links, isolation, codebook fields, one email per address, fast pages |
| Follow-up in the browser (laptop, phones 320 to 375 px, light and dark) | all pages; the 1 to 7 scale stays on one line with readable end labels |

The instrument went through four review rounds by the team (see the
`REVIEW_RESPONSE_*.md` files).

## 10 Known limitations

- **One item per form per area.** Domain-level scores rest on few decisions;
  the overall form scores are more reliable than the domain scores.
- **Overplacement and risk.** Contest entry also reflects risk attitude. The
  rank questions and the K1 control are designed to separate the two, but the
  separation is statistical, not experimental.
- **Overprecision noise.** With one interval per node, the hit against a single
  drawn value is noisy; the analysis uses expected coverage instead.
- **Range format.** Low and high estimate are asked on one screen. Soll and
  Klayman (2004) found higher hit rates when the two points are asked on
  separate screens; the choice is named in Chapter 5.
- **Reference conventions.** The nine-month buffer in F1 and the G1 test share
  rest on stated assumptions; the codebook lists the robustness checks.
- **Industry is a label.** The product is digital in every industry; the
  reference values assume a digital product.

- **Follow-up items.** The 12 new items are not a validated scale and were not
  pretested; the 4 Costa anchors show how far they can be trusted. All items
  run in the same direction (higher = more confident), and the target (one's own
  startup) differs from the simulation on purpose, so only modest correlations
  with the behavioural scores are expected.

## 11 Version history

See `CHANGELOG.md`. Each release records the app version and the codebook
version in every session row, so the analysis can tell which version a
participant saw.

## 12 Authors, citation and licence

Eléonore Konsbruck, Amie Weidemann and Sarah Yousfi, master's students at Nova
School of Business and Economics, supervised by Prof. João Castro.

> Konsbruck, E., Weidemann, A. and Yousfi, S. (2026). *Decisions in founding:
> a simulation instrument for measuring founder overconfidence* (version
> 0.15.0). Work project, Nova School of Business and Economics.

© 2026 the authors. All rights reserved. The code is shared for academic
assessment at Nova SBE; any other use requires the authors' permission.

### References

- Benoît, J.-P., Dubra, J. and Moore, D. A. (2015). Does the better-than-average effect show that people are overconfident? *Journal of the European Economic Association*, 13(2), 293–329.
- Camerer, C. and Lovallo, D. (1999). Overconfidence and excess entry: an experimental approach. *American Economic Review*, 89(1), 306–318.
- Dohmen, T., Falk, A., Huffman, D., Sunde, U., Schupp, J. and Wagner, G. G. (2011). Individual risk attitudes: measurement, determinants, and behavioral consequences. *Journal of the European Economic Association*, 9(3), 522–550.
- Moore, D. A. and Healy, P. J. (2008). The trouble with overconfidence. *Psychological Review*, 115(2), 502–517.
- Soll, J. B. and Klayman, J. (2004). Overconfidence in interval estimates. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 30(2), 299–314.

Further sources for each reference value are listed in `sim/codebook.json`.
