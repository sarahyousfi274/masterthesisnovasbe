# Changelog

All notable changes to the simulation, newest first. Review responses with
the full detail of each feedback round: `REVIEW_RESPONSE_0.10.0.md`,
`REVIEW_RESPONSE_ROUND3_0.13.0.md`, `REVIEW_RESPONSE_ROUND4_0.14.0.md` and
`REVIEW_RESPONSE_FOLLOWUP_0.15.0.md`.

## 0.15.0

The follow-up one week later (build spec of 30 October 2026, version 3): a 5-minute self-report on the participant's own startup under a personal link (`?fu=<token>`), followed by the debriefing, in the design of the simulation. 12 new items in the format of Costa et al. (2026), one per measured decision, 4 unchanged Costa items as anchors and a control row; forecasts for current founders only; interstitial when the debriefing link is opened first; withdrawal button on the debriefing page. New table `followup_responses`, new columns in `followup`, a "Follow-up" section on the data page (due list, invitation file, wide and long exports) and `tests/followup_walkthrough.py`. The simulation itself is unchanged.

## 0.14.2

A resume link opened after more than 30 minutes asks for the email address first, so a forwarded link cannot open someone else's session; phone fixes (background note, report lines, bigger answer pills on touch screens).

## 0.14.1

Without `.streamlit/config.toml` the app now still looks right in dark mode (empty radio dots, light dropdown lists).

## 0.14.0

Applies the simulator check of round 4 (details in `REVIEW_RESPONSE_ROUND4_0.14.0.md`). A session can be resumed after a reload, a locked phone, a laptop asleep or a redeploy: the progress is saved under a random token in the URL (`?r=…`), and a participant who comes back through the plain link and enters the same email is offered "Continue where I stopped". A dropped connection is kept for an hour (`disconnectedSessionTTL = 3600`). Text fixes: F1 listed once in the final report, "Planned hires" instead of "Open roles", an uneven F3 series (+2, +4, +3 %), the same follow-up wording everywhere, a digital product named before the industry is chosen, contact emails kept in one piece, a Head of Product instead of a Head of Growth (H5/H2), and normal figures in running text.

## 0.13.3

The end of the Team area pays the month before the new people start; H4 and the report make clear that the Head of Sales comes on top of the planned hires; F3 opens with "Investors will ask … for a revenue forecast"; the starting situation explains the free trial behind the steady revenue; the net burn help names what the costs cover.

## 0.13.2

The story explains the paying customers at the start: they use a pilot the team still runs largely by hand, and the MVP turns it into a first real product (setup text and Building the product intro).

## 0.13.1

"About you" has its own colors (stone grey page, white card, charcoal panel, terracotta accent), clearly apart from the green and beige simulation; the email text says there is exactly one follow-up email; a completed run with the same email ends on a thank-you screen; the industry of Lumora has no preselection (the field shows a dash).

## 0.13.0

Applies the simulator check of round 3 (details in `REVIEW_RESPONSE_ROUND3_0.13.0.md`): F1 counted apart from Finance, ranges with low = high refused, G4 persistence coding, a Finance bridge to 6 months of runway, H1 as a plan, T1 founder time aligned with T3, a flatter F3 chart, H2 paid in cash, digital product sentences, one complete run per email, H4 option C resolved, and layout fixes for laptop and phone. It keeps the speed fix of 0.12.1.

## 0.12.1

Makes each page move on at once with Postgres: connections are reused instead of opened for every write, and writes run in one background thread in order, with five retries. Reads (data page, deletion) wait for the queue first. Failed writes, if any, are listed on the data page.

## 0.12.0

Closes the open threads of the contests: the area report notes that a decision is pending (for example "Head of Growth: she decides in the coming weeks"), and the final report after K1 draws every entered contest with its stated chance and shows how it turned out. A win adds the prize. The outcomes are stored with the final report.

## 0.11.2

Makes F1 the opening decision right after the starting situation, the same position for everyone. The runway shown is always 14 months, so all four options are feasible in every track (in the Finance area, Track 3 left a median of 2 months and only "Right away"). Finance now runs F3 and F4 plus its contest pair.

## 0.11.1

The end-of-area curtain covers the whole screen again (the screen fade no longer uses a transform), the slider track is neutral instead of the theme color (red when `.streamlit/config.toml` is missing), and pill options are never cut off.

## 0.11.0

Applies the team feedback of 21 October: dark green and beige only (no blue anywhere), a dark green top panel with the sections, a progress bar with a gradient and the numbers line, one font everywhere, "This section is about you." in About you, sliders without a preselected answer for experience, risk attitude and earlier startups, answer rows that span the full width, more vertical space (decision screens still fit a 1366 x 768 laptop), "Your startup: Lumora", the email icon rings like a push notification, longer and smoother transitions, a closing screen after the thank-you page and the team's text on the welcome page.

## 0.10.0

Applies the simulator review of 20 October 2026 (Amie): F4, H4 and G4 are always the last decision of their area; T3 comes before T1 and H3 before H1; no outcome feedback before a final report after K1 (customers, revenue, morale and market confidence are held back, the morale and market tiles are hidden until then); G1 and G4 give every option the same effect; F1 asks in remaining runway, offers only feasible options, charges no running costs twice and applies worse terms to a start with fewer than 6 months left in the final report; G3 shows 9, 16, 21 and asks for month 9; G1 and G3 take their reference values from the models in `models/`; K1 says "premium entry"; no contest results are promised; "solo founder", "based in Europe", no month labels, one type scale, every decision screen fits a 1366 x 768 laptop, the invitations read as emails, and the selection color holds even without `.streamlit/config.toml`.

## 0.9.1

Uses three tracks instead of two. Building the product always comes first; the other three areas form a Latin square, so each of them appears once in position 2, 3 and 4. Allocation is balanced: at consent, a new participant gets the track with the fewest completed plus currently running sessions (ties at random). The data page shows completed sessions per track.

## 0.9.0

Gives the simulation its own look and feel: a warm "boardroom" palette (paper white, navy, deep teal), Lumora as a company with a logo and a one-line product per industry, simulated time (each area is one month), a numbers panel on every question, contest invitations as messages, a short "End of month" curtain with rolling numbers in each monthly report, a timeline of the participant's decisions on the end screen, a sticky Continue button on phones, a fade between screens and a favicon (`assets/favicon.png`). No measured question, option or reference value changed.

## 0.8.1

Brings back the choice at setup: participants run Lumora on their own or with one co-founder. Every text that mentions the founder adapts ("you" or "you and your co-founder"), as do the status labels. The team composition in the demographics describes the real company only.

## 0.8.0

Shows the scientific background per question on hover over a link icon (author and year only), removes the scenario dropdown, gives "About you" its own form look, adds an animated transition into the simulation, lets every participant run the same startup (Lumora), adds G4 (reaction to the first month) and K1 (a raffle as random-outcome control) and sets the study contact address. The session has 22 decisions (20 measured, 2 attention checks).

## 0.7.0

Adds four rank-belief items (one per area, asked before each contest), states the 1-in-10 base rate in every contest, removes every benchmark from the scenario popovers (fictional + author and year only), switches all range questions to Low/High at 80%, adds net burn with a revenue tile, an ownership tile, hires joining at the end of the Team area, a full morale and market confidence rule set, consequences for fundraising timing, a randomized candidate order in H4, attention checks in areas 2 and 3, and the SOEP risk items. The session has 20 decisions (18 measured, 2 attention checks).

## 0.6.0

Applies the notes of 18 October (V3): Streamlit pinned to 1.65.0 so the cloud runs the exact tested version, accent color indigo instead of red for every selection, light mode enforced, Back only once per area (from the first decision to the area's starting situation), the status strip fixed at each area's starting numbers, a new welcome page, a general screening question, timestamps per screen (entered_at, answered_at) and total duration per session, and a full copy edit in American English ("startup").

## 0.5.0

Applies the team notes of 18 October: a new light-only design system (`sim/ui.py`), a section bar at the top, the email address instead of a pseudonym code, the questions about the person first, a logical order inside each area, one screen per range question, status cards that explain every change, and attention checks written into the question text.

## 0.4.0

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
