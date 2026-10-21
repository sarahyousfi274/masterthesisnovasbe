# Response to the simulator review of 20 October 2026

**Release:** 0.10.0 (codebook 0.10.0) · **Date:** 21 October 2026
**For:** Amie and the team

Every finding was checked against the code of 0.9.1 first. All of them were confirmed. One
more item of the same kind was found and fixed (see A7). One new problem came up while
testing A3 (see "Open for the team").

## Tests

| Check | Result |
|---|---|
| `tests/walkthrough.py`, all three tracks, solo and co-founder | end to end ok, 22 scored nodes per session |
| New walkthrough checks: A1, A4, A5, A9 | all pass |
| `tests/simulate_participants.py` (300 synthetic participants) | r = 0.919 / 0.941 / 0.893, cross correlations below 0.05 |
| Path simulation, 60,000 random sessions | no infeasible F1 option; 0 of 52,977 comparisons where an F1 option ends better off than the reference |
| Laptop 1366 × 768 (viewport 1366 × 640) | Continue visible on every decision screen without scrolling (F3: 595 px, G3: 618 px, K1: 603 px) |
| Phone 390 px | smallest text 12.8 px (0.8 rem) |

## Part A

**A1. Outcome nodes last.** Go-to-market runs G1, G3, G4. In Finance, Team and Go-to-market,
contest pairs and attention checks are inserted only before the last story node
(`flow.build`, block flag `outcome_last`). The walkthrough checks that F4, H4 and G4 are
the last decision of their area.

**A2. Consequences.** G1: every split gives +45 customers; the market-confidence effects
stay (−1 for 100/0, +1 for 40/60 and 20/80). G4: every option gives +15 customers and
nothing else. Both are shown only in the final report. The area summary lists "After the
first month: [option]" with the note "no direct cost".

**A3. F1.** New screen:
> **When do you start fundraising?** (with a co-founder: "When do you and your co-founder start fundraising?")
> Lumora has 12 months of runway. Starting means preparing the deck and contacting investors. Until then, Lumora keeps paying its running costs from the cash it has.
> ○ Right away, with 12 months left ○ When 9 months of runway are left ○ When 6 months are left ○ When 3 months are left

Only options below the runway shown are offered. The runway left at the start is stored as
`numeric_value`; the score is the delay (runway shown minus runway left) against the
reference delay (runway shown minus 9, at least 0), so `reference_rule` is unchanged. The
extra deduction is gone (`state.delay_cost` now returns 0). A start with fewer than 6
months left closes on worse terms in the final report: €15,000 bridge fee on the loan, or
2 ownership points on the SAFE or the priced round. "When 3 months are left" keeps a
market-confidence −1 (final report only); the reference is never worse off.

**A4. Anchors.** Building the product: T3 before T1. Team: H3, H1, H4.

**A5. F3.** Solved through A9: revenue is €8,000 at F3 in every track, so the chart is
always the fixed series ending at €8,000 (checked in the walkthrough).

**A6. G3.** "A new paid sales channel brought Lumora 9, 16 and 21 new paying customers in
its first three months. How many new paying customers will it bring in month 9?" Chart
9, 16, 21, future slot "Month 9". Help texts as specified, step 1. Codebook fields
`quantity`, `reference_percentiles` (22, 34, 56, 91, 127), `provenance`, `basis`,
`sources`, `open` updated. G1 fields updated as specified; `reference_value_alternative`
(0.55) was removed, since `open` now says it is no longer used. The model scripts are in
`models/`.

**A7. End page.** "With the follow-up we will also explain what the study was about."
The decision timeline sits on the same page, so the sentence appears once (in the thank-you
text) instead of twice in a row. **Also found:** under every contest the app said "Results
are announced after the study." That line is removed too. The README now states that the
debriefing email goes to everyone in `followup.csv`.

**A8. K1.** "Enter with a premium entry · €17,000 · raises the chance to 1 in 8".

**A9. No outcome feedback.** `state.apply` holds back every effect on customers, morale and
market confidence (`state["deferred"]`, with the decision label); the hiring morale rule
and the short-runway rule are held back the same way. A new final report after K1
(`report_final`, built with the existing report screen) applies them in one step via
`state.settle`, together with the late-start terms from A3. During the session the morale
and market-confidence tiles are hidden and the numbers line no longer lists customers
(constant until the end); revenue and net burn change only through costs.

## Part B

- **B1** "On my own, as the solo founder".
- **B2** "Founded last year · based in Europe".
- **B3** No month labels: "At the start of this area", "Area n of 4", "End of this area",
  "area by area", timeline by area. Time inside the story is kept.
- **B4** Type scale 1.75 / 1.25 / 1 / 0.875 rem, minimum 0.8 rem, also for the transition
  screen and the end-of-area curtain. The bar charts are now HTML instead of SVG, so their
  labels keep the scale on phones too.
- **B5** One-line numbers strip, lower charts, "lower/higher" inside the range bar, the
  three finished intro sections collapse into one chip ("Introduction") during the
  simulation, status cards in four columns. The final report and the end page may scroll.
- **B6** T5, F5, H5, G5 and K1 as emails: From, Subject, greeting, body, sign-off. Senders:
  Mentor, Accelerator program, Recruiting partner, Procurement (potential customer),
  Founders' network.
- **B7** Checked first: with `.streamlit/config.toml` the selected dot is the theme color
  (31, 95, 91); without it, Streamlit's red (255, 75, 75). The deployed app was not
  reading the file, most likely because the hidden `.streamlit` folder never reached
  GitHub. It needs to be uploaded. A CSS fallback now keeps the theme color even without
  the file.

## Open for the team

**F1 in Track 3.** Finance is the last area in Track 3. In the path simulation the runway at
F1 had a median of 12 months in Track 1 (always all four options), 7 in Track 2 (right
away, 6, 3) and 2 in Track 3, where 81 percent see only "Right away" and about 3 percent
start with less than one month. F1 is feasible everywhere now, but in Track 3 it carries
almost no information, so F1 still measures different things by track. Options:

1. Score F1 only where at least two options were offered, and report it as a limitation.
2. Give the Finance area a fixed starting runway (for example a bridge from existing
   investors at the start of Finance), so F1 starts from the same point in every track.
3. Change the Latin square so that Finance is never last. This gives up full balance for
   Finance.

## Update 0.11.2: F1 in Track 3 resolved (team decision of 21 October)

F1 is now the opening decision right after the starting situation, at the same
position for every participant. The runway shown is always 14 months. Path
simulation (60,000 sessions): all four options feasible in 100 percent of
sessions in every track, 0 of 80,000 comparisons where an option ends better
off than the reference. In the synthetic-participant check F1 now spreads
41 / 26 / 34 percent above, at and below the reference (before: 23 / 62 / 15).

## Update 0.12.0: contest outcomes (team decision of 21 October)

During the session the area report shows only that a contest decision is
pending. Outcomes are drawn in the final report after K1, after every measured
decision, with the stated chance, so they cannot feed back into later answers
(A9). This resolves the story without promising real results (A7).
