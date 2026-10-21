# Founder decision simulation

The instrument for Chapter 5 of the work project *Founder Overconfidence and
Startup Performance*. It runs a session of about 20 minutes: four domain
blocks of four decisions each, a short post-game question, and an end screen
with the pseudonym code that opens the follow-up a week later.

**Version 0.11.0** applies the team feedback of 21 October: dark green and
beige only (no blue anywhere), a dark green top panel with the sections, a
progress bar with a gradient and the numbers line, one font everywhere,
"This section is about you." in About you, sliders without a preselected
answer for experience, risk attitude and earlier startups, answer rows that
span the full width, more vertical space (decision screens still fit a
1366 x 768 laptop), "Your startup: Lumora", the email icon rings like a push
notification, longer and smoother transitions, a closing screen after the
thank-you page and the team's text on the welcome page.

**Version 0.10.0** applies the simulator review of 20 October 2026 (Amie):
F4, H4 and G4 are always the last decision of their area; T3 comes before T1
and H3 before H1; no outcome feedback before a final report after K1 (customers,
revenue, morale and market confidence are held back, the morale and market
tiles are hidden until then); G1 and G4 give every option the same effect; F1
asks in remaining runway, offers only feasible options, charges no running
costs twice and applies worse terms to a start with fewer than 6 months left
in the final report; G3 shows 9, 16, 21 and asks for month 9; G1 and G3 take
their reference values from the models in `models/`; K1 says "premium entry";
no contest results are promised; "solo founder", "based in Europe", no month
labels, one type scale, every decision screen fits a 1366 x 768 laptop, the
invitations read as emails, and the selection color holds even without
`.streamlit/config.toml`.

**Version 0.9.1** uses three tracks instead of two. Building the product
always comes first; the other three areas form a Latin square, so each of them
appears once in position 2, 3 and 4. Allocation is balanced: at consent, a new
participant gets the track with the fewest completed plus currently running
sessions (ties at random). The data page shows completed sessions per track.

**Version 0.9.0** gives the simulation its own look and feel: a warm
"boardroom" palette (paper white, navy, deep teal), Lumora as a company with a
logo and a one-line product per industry, simulated time (each area is one
month), a numbers panel on every question, contest invitations as messages,
a short "End of month" curtain with rolling numbers in each monthly report, a
timeline of the participant's decisions on the end screen, a sticky Continue
button on phones, a fade between screens and a favicon (`assets/favicon.png`).
No measured question, option or reference value changed.

**Version 0.8.1** brings back the choice at setup: participants run Lumora
on their own or with one co-founder. Every text that mentions the founder
adapts ("you" or "you and your co-founder"), as do the status labels. The
team composition in the demographics describes the real company only.

**Version 0.8.0** shows the scientific background per question on hover over a
link icon (author and year only), removes the scenario dropdown, gives "About you"
its own form look, adds an animated transition into the simulation, lets every
participant run the same startup (Lumora), adds G4 (reaction to the first month)
and K1 (a raffle as random-outcome control) and sets the study contact address.
The session has 22 decisions (20 measured, 2 attention checks).

**Version 0.7.0** adds four rank-belief items (one per area, asked before each
contest), states the 1-in-10 base rate in every contest, removes every benchmark
from the scenario popovers (fictional + author and year only), switches all range
questions to Low/High at 80%, adds net burn with a revenue tile, an ownership
tile, hires joining at the end of the Team area, a full morale and market
confidence rule set, consequences for fundraising timing, a randomized candidate
order in H4, attention checks in areas 2 and 3, and the SOEP risk items. The
session has 20 decisions (18 measured, 2 attention checks).

**Version 0.6.0** applies the notes of 18 October (V3): Streamlit pinned to
1.65.0 so the cloud runs the exact tested version, accent color indigo instead
of red for every selection, light mode enforced, Back only once per area (from
the first decision to the area's starting situation), the status strip fixed at
each area's starting numbers, a new welcome page, a general screening question,
timestamps per screen (entered_at, answered_at) and total duration per session,
and a full copy edit in American English ("startup").

**Version 0.5.0** applies the team notes of 18 October: a new light-only design
system (`sim/ui.py`), a section bar at the top, the email address instead of a
pseudonym code, the questions about the person first, a logical order inside
each area, one screen per range question, status cards that explain every
change, and attention checks written into the question text.

**Before inviting anyone:** set `CONTACT_EMAIL` at the top of `sim/content.py`
to the team's study address, and make sure `.streamlit/config.toml` is in the
repository at exactly that path.

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. Data goes to `data/sessions.db`.

For putting it online, see **DEPLOY.md**. The short version: a hosted
Streamlit app has no permanent disk, so set `DATABASE_URL` to a Postgres
database before collecting real data, or it will be lost on the next restart.

## The data page

`?view=admin`, for example `http://localhost:8501/?view=admin`. It shows how
many sessions have been started and completed, offers one CSV download per
table, computes the group level results so far, and deletes a participant by
pseudonym code for a withdrawal by mail.

It needs `ADMIN_PASSWORD` in `.streamlit/secrets.toml` (copy
`secrets.toml.example`). Without a password the page refuses to open, so a
deployed app is never accidentally public. Participants never see a link to it.

From a script instead:

```python
from sim import storage
storage.export_csv("export")   # sessions.csv, responses.csv
storage.delete("ABC-1234")     # a withdrawal by mail
```

## Tests

```bash
python -m tests.simulate_participants   # does the scoring recover known biases?
python -m tests.walkthrough             # does a whole session run and store correctly?
```

`simulate_participants` is evaluation episode 1 from Section 4.3: 300
synthetic participants with known bias parameters, scored by the real scoring
module. It reports how well each form score recovers the parameter that
produced it and whether the three form scores stay independent. Current
result: r = 0.93 / 0.84 / 0.83 with cross correlations below 0.09.

`walkthrough` drives the real app through all three tracks with Streamlit's
AppTest harness and checks that every screen is stored, timed and carries a
snapshot of the situation.

## Layout

```
app.py                      screens and routing, nothing scored
DEPLOY.md                   putting it online, and what that costs you
sim/content.py              every word a participant sees, plus the effect table
sim/codebook.json           the hidden reference values, with provenance and sources
sim/codebook.py             access to them, quantile and coverage functions
sim/state.py                the situation: cash, burn, runway, team, morale, customers
sim/flow.py                 tracks, randomisation inside a block, pseudonym codes
sim/storage.py              SQLite locally, Postgres when DATABASE_URL is set
sim/admin.py                the data page at ?view=admin
sim/scoring.py              scoring per form and per domain
tests/                      the two checks above
```

**`sim/codebook.json` is why the repository has to stay private.** It holds
every reference value and the whole measurement logic. A participant who could
read it would know what is being measured and what counts as an aggressive
answer, which is exactly what R5 keeps from them.

The split matters for the design: `content.py` is the story, which
participants experience, and `codebook.json` holds the reference values,
which they never see. The story reacts only to the effect table in
`content.py`, never to a measurement result.

## Flow (0.5.0)

```
welcome and consent
About you        founder filter → email → profile → experience → risk attitude
How it works     overview → example choice → example range (not part of the study)
Your startup     Lumora: on your own or with a co-founder, industry → starting situation
4 areas          intro with status → 4 decisions → status with "what changed"
Wrap-up          "what do you think this study was about?" → thank you
```

Inside an area, nodes that build on each other keep their order (F1 → F3 → F4,
H1 → H3 → H4, T1 → T3, G1 → G3); the others, including the attention checks,
are inserted at random positions. Back is offered in "About you" and on any
screen that follows an information-only screen. Range questions show the best
and worst case on one screen, in random order, and are stored as the two rows
`<node>_opt` and `<node>_pes` that the scoring expects.

The email address is stored only in the `followup` table with the internal
session id. It never appears in `responses`. The full debrief goes out with the
follow-up email.

For a local design review, `FS_DEV=1 streamlit run app.py` and open
`?jump=<screen id>`, for example `?jump=F3`. Without that environment variable
the parameter does nothing.

## Changing the reference values

Everything scored sits in `sim/codebook.json`. Each node carries a `provenance`
tag:

- `empirical` — a published figure is used directly (F3, H1, H3, G1)
- `derived` — computed from published figures plus a stated assumption (T1,
  T3, F1, and the four contests)
- `placeholder` — needs the team's own interview or pilot data before fielding
  (G3)

Every entry also carries `basis`, `sources` and, where something is still
open, an `open` field. Changing a number means editing this file; nothing
else needs touching.

## The contests

`contest_variant` at the top of the codebook switches between two sets of
numbers.

`harmonised` (default) applies one rule to all four contests: ten
competitors, a one in ten chance, an upgrade to one in eight, entry costing
`prize / 10 + 2000` and the upgrade `prize / 8 + 4500`. Every contest then
has an expected value of −2,000 euros for entry and −4,500 for the upgrade,
so entry rates are comparable across domains.

`walkthrough` restores the numbers from the draft of 5 October.

## Scoring

| Form | Score |
|---|---|
| Overestimation | signed distance of the chosen option from the reference value, in the node's own unit, positive meaning more aggressive, then z-standardised across the sample |
| Overplacement | entry into a contest with a negative expected value, plus the size of the stake |
| Overprecision | width of the stated range over the width of the reference range, below 1 meaning too narrow, plus the coverage of the reference distribution |

For overprecision the module reports both the binary hit against one drawn
value and `expected_coverage`, the share of the reference distribution
falling inside the stated range. The second is the expectation of the first
without the noise of a single draw, so with one decision per cell it is the
more efficient statistic for the analysis (Section 4.3 on reliability).

## Open points for the team

The 18 October review raised several points that need a team decision before
fielding, listed here so they do not get lost:

1. **Contest design.** All four contests use the same 10-competitor rank
   format. Overplacement cannot be cleanly separated from risk tolerance,
   because entering the contest also carries risk. A paired version with a
   random-outcome control (Camerer and Lovallo 1999) plus a rank question
   ("which of the 10 do you expect to finish?") would separate the two.
2. **H2 ("senior developer").** Winning depends on the candidate's choice,
   not on the founder's own ability, so this is not a pure overplacement
   item. Either replace with a contest where ability matters, or keep it and
   score it separately.
3. **Overprecision noise.** With one draw per interval, the hit rate is noisy.
   The scoring already prefers `expected_coverage` for the analysis. The
   drawn value is only shown in the follow-up, not during the session.
4. **Overestimation items.** The ladder format measures preference under
   known reference, not point estimates against ground truth. Consider adding
   a point-estimate variant for one node per block.
5. **One item per form per domain.** With 16 scored nodes, the Finance and
   GTM scores rest on three decisions each. Consider adding a second item per
   form per block for the fielding version.
6. **Attention checks** are now randomised within blocks (not always last).
   Keep them as a quality marker rather than a hard exclusion given the small
   sample.
7. **Validation block and market-entry game.** Still to be added.
8. **Team diversity** is now captured in demographics as a potential
   moderator variable.
9. **G3 reference distribution** comes from a Bass model since 0.10.0
   (`models/g3_model.py`), with prior variants B and C as robustness checks.
10. **H1 ladder (0, 1, 2, 3)** is censored on the aggressive side. A fifth
    option (4 or 5 roles) would balance it.
11. **F1 nine-month runway reference** is a convention; defend from
    interviews or report with both a six- and a nine-month reference.
12. **Contact and ethics placeholders** in the consent and end text need to
    be confirmed with Prof. Castro and the Nova SBE ethics board. The current
    placeholders are `founderstudy@novasbe.pt` and `ethics@novasbe.pt`.

## What changed in 0.4.0

- Demographics (profile, experience, risk) moved to the start.
- Attention check randomised within its block, no longer always last.
- Optimistic and pessimistic halves of each range screen appear in random order.
- Starting situation screen added so participants see the baseline.
- Burn is deducted at the end of each block.
- Planned hires are shown separately and no longer fold into team size.
- Customer growth depends on the launch-budget split (G1).
- Convertible terms (F4) rebalanced to a 2M cap with a conversion note.
- G4 reworked from a website colour choice to a trade-event question.
- H1 roles updated to 0, 1, 2, 3.
- Experience options extended to 0 through 5 or more.
- Country as a dropdown; gender keeps "Prefer not to say".
- Numbers rendered in US format throughout (commas as thousands separator).
- Café warm-up is now explicitly labelled as an example.
- Back button only in warm-up and intro screens; otherwise one-way.
- Validation on every field; nothing can be left blank.
- Dark mode: answer cards stay legible (forced light colours).
- Continue button: one click; validation on click.
- Interval warning if both values are the same.
- "What was this study about?" kept as suspicion check with explanation.
- Debrief content moved to the follow-up: the end screen shows a thank you,
  the code, and the follow-up notice; the full purpose, data note and
  personal results are shared in the follow-up a week later.
- No mail collection; the follow-up is opened with the pseudonym code.
- No "don't use my data" opt-out: participants withdraw by writing to the
  research team with their code (deadline stated).
- Scenario context popover ("About this scenario") on each measurement
  question, with sources, without disclosing the reference value.

## Debriefing (review A7)

The study is explained with the follow-up email a week after the session. That
email must go to **every** participant in `followup.csv` (the data page offers
the download), including those who do not answer the follow-up. The contests
and the raffle are fictional; neither the app nor the email promises results.
