# Founder decision simulation

The instrument for Chapter 5 of the work project *Founder Overconfidence and Startup
Performance*. It runs the session described in the Simulation Walkthrough of 5 October:
four domain blocks, three measurement nodes per block, a situation that travels through
the game, and a mandatory debrief.

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. Data goes to `data/sessions.db`.

For putting it online, see **DEPLOY.md**. The short version: a hosted Streamlit app has no
permanent disk, so set `DATABASE_URL` to a Postgres database before collecting real data,
or it will be lost on the next restart.

## The data page

`?view=admin`, for example `http://localhost:8501/?view=admin`. It shows how many sessions
have been started and completed, offers one CSV download per table, computes the group
level results so far, and deletes a participant by pseudonym code for a withdrawal by
mail.

It needs `ADMIN_PASSWORD` in `.streamlit/secrets.toml` (copy `secrets.toml.example`).
Without a password the page refuses to open, so a deployed app is never accidentally
public. Participants never see a link to it.

From a script instead:

```python
from sim import storage
storage.export_csv("export")                        # sessions.csv, responses.csv
storage.export_csv("export", include_followup=True) # adds the mail addresses
storage.delete("ABC-1234")                          # a withdrawal by mail
```

The follow-up mail addresses live in their own table and are left out of the normal
export, so the analysis file carries no contact data.

## Tests

```bash
python -m tests.simulate_participants   # does the scoring recover known biases?
python -m tests.walkthrough             # does a whole session run and store correctly?
```

`simulate_participants` is evaluation episode 1 from Section 4.3: 300 synthetic
participants with known bias parameters, scored by the real scoring module. It reports
how well each form score recovers the parameter that produced it and whether the three
form scores stay independent. Current result: r = 0.92 / 0.84 / 0.90 with cross
correlations below 0.09.

`walkthrough` drives the real app through both tracks with Streamlit's AppTest harness
and checks that every screen is stored, timed and carries a snapshot of the situation.

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

**`sim/codebook.json` is why the repository has to stay private.** It holds every
reference value and the whole measurement logic. A participant who could read it would
know what is being measured and what counts as an aggressive answer, which is exactly what
R5 keeps from them.

The split matters for the design: `content.py` is the story, which participants
experience, and `codebook.json` holds the reference values, which they never see. The
story reacts only to the effect table in `content.py`, never to a measurement result.

## Changing the reference values

Everything scored sits in `sim/codebook.json`. Each node carries a `provenance` tag:

- `empirical` — a published figure is used directly (F3, H1, H3, G1)
- `derived` — computed from published figures plus a stated assumption (T1, T3, F1, and
  the four contests)
- `placeholder` — needs the team's own interview or pilot data before fielding (G3)

Every entry also carries `basis`, `sources` and, where something is still open, an
`open` field. Changing a number means editing this file; nothing else needs touching.

## The contests

`contest_variant` at the top of the codebook switches between two sets of numbers.

`harmonised` (default) applies one rule to all four contests: ten competitors, a one in
ten chance, an upgrade to one in eight, entry costing `prize / 10 + 2000` and the upgrade
`prize / 8 + 4500`. Every contest then has an expected value of −2,000 euros for entry
and −4,500 for the upgrade, so entry rates are comparable across domains, which is what
R2 and Section 6.3 need.

`walkthrough` restores the numbers from the draft of 5 October. T2 and F2 are identical
in both variants; H2 and G2 differ, because the draft gave them expected values of
−1,250 / −4,000 and −5,000 / −21,250.

## Scoring

| Form | Score |
|---|---|
| Overestimation | signed distance of the chosen option from the reference value, in the node's own unit, positive meaning more aggressive, then z-standardised across the sample |
| Overplacement | entry into a contest with a negative expected value, plus the size of the stake |
| Overprecision | width of the stated range over the width of the reference range, below 1 meaning too narrow, plus the coverage of the reference distribution |

For overprecision the module reports both the binary hit against one drawn value, which
the walkthrough specifies and the debrief shows, and `expected_coverage`, the share of
the reference distribution falling inside the stated range. The second is the expectation
of the first without the noise of a single draw, so with one decision per cell it is the
more efficient statistic for the analysis (Section 4.3 on reliability).

## Open points

1. **G3's reference distribution** is an assumption about how channel growth flattens, not
   a measured one. It needs the interviews or a pilot.
2. **F1's nine-month runway reference** is a convention. Report the score for a six-month
   reference as well, or defend nine from the interviews.
3. **T1's ladder is censored on the aggressive side.** With the reference at option B,
   only one option can show overestimation while two can show caution. The other three
   ladders have two or three options above the reference. See Zorowitz and Niv (2023) on
   ceiling effects, already cited in Section 4.3.
4. **No random-outcome control contest.** Section 4.2 says the design provides for control
   decisions with random outcomes, following Binnendyk et al. (2025) and the luck
   condition of Camerer and Lovallo (1999). None of the four contests is one. Without it,
   entry can reflect risk or ambiguity attitude rather than overplacement.
5. **Risk and ambiguity attitude (R7)** were missing from the walkthrough and are added
   here as three sliders in the post-survey. Replace them with whichever validated items
   the team decides on.
6. **Soll and Klayman (2004) recommend a three-point format.** Adding a "most likely"
   value to each interval node raised the hit rate from 57 to 66 percent in their data and
   would give a point estimate per node as well. It costs four extra screens.
7. **The reference distributions have short tails.** They are defined by five stated
   percentiles and interpolated log-linearly between them, so values far outside the 10 to
   90 range are compressed. The scored quantities, the width ratio and the coverage, use
   the documented range and are unaffected, and the drawn value shown at the debrief stays
   in a sensible span. It is worth a sentence in the appendix rather than a change.
