# Response to the simulator check, round 3

**Release:** 0.13.0 (codebook 0.13.0) · **Date:** 25 October 2026

All items of Part A are in. The release also carries the speed fix of 0.12.1
(see the last section), which came after the check was written.

## Tests

| Check | Result |
|---|---|
| `tests/walkthrough.py`, all three tracks, solo and co-founder | end to end ok, 22 scored nodes per session |
| New walkthrough checks | A3 (low = high refused), A11 (Finance never below 6 months), A16 (same email blocked), A17 (second round resolved): all pass |
| `tests/simulate_participants.py` | r = 0.920 / 0.947 / 0.885, scoring recovers the parameters |
| Laptop 1366 × 640 | Continue bottom: F3 621 px, G3 633 px, K1 636 px (before 630 to 667, 652, 646) |
| Phone 375 px | tick labels wrap, no overlap; long dropdown options wrap |

## Part A

**A1. Theme file.** Not a code change: `.streamlit/config.toml` must be uploaded to
GitHub at exactly that path (Cmd+Shift+. shows the hidden folder on a Mac). Since
0.11.1 the app also forces the colors itself, but dark dropdowns and the radio dot
need the file.

**A2. F1 outside Finance.** `decision_eyebrow()` leaves out screens with `opening`,
so Finance counts "Decision 1 of 4" (or "of 5" with an attention check). F1 is listed
under "Your first decision · Your startup" in the end timeline, and in the final
report instead of the Finance area report. F1 keeps `domain: "finance"` for scoring.

**A3. Range check.** `render_interval` refuses `low >= high`: "Please give two
different numbers: your low estimate must be lower than your high estimate."

**A4. G4 coding.** `coding` {A: 4, B: 3, C: 2, D: 1} and `coding_note` in the
codebook; `scoring.py` returns `"coded"` for outcome nodes.

**A5. Fold.** Bars at most 30 px high; tighter spacing only on the screens with a
chart (F3, G3) or an email (rank items, K1).

**A6. G3.** "Suppose a new paid sales channel brings Lumora 9, 16 and 21 new paying
customers in its first three months. How many new paying customers will it bring in
month 9?" The chart has a "…" column between Month 3 and Month 9.

**A7. Phone.** Slider tick labels wrap at 0.8 rem; dropdown options wrap to two
lines; when a long option is chosen, the full text is shown under the closed field
on phones.

**A8. Solo founders.** Emails open with "Hi there," instead of "Hi Lumora team,".

**A9. T1.** Co-founders: 16 / 12 / 8 / 3 weeks of founder time; solo: 32 / 24 / 16 /
6 weeks of your time (`extra_solo`, read via `pick(opt, "extra")`). Codebook `basis`
extended.

**A10. H1.** "How many people do you plan to have hired within the next 3 months?"
Body: "Each new hire adds about €5,000 to the monthly costs. In the numbers,
everyone you plan to hire is counted from the end of this area." Event "Hires
planned". Codebook `quantity` and `open` updated.

**A11. Finance bridge.** `FINANCE_START_RUNWAY = 6`. At the Finance intro, if the
runway is below 6 months: bridge = 6 × net burn − cash, rounded up to €1,000,
applied as "Bridge from existing investors", named in the intro ("Your existing
investors have bridged Lumora with €… so that the financing decisions start from 6
months of runway."), stored as `state.finance_bridge` and logged on the
`intro_finance` row. Path simulation (20,000 random paths per track):

| Track | Finance is area | Runway at Finance start (median) | Bridge given | Bridge median / max |
|---|---|---|---|---|
| 1 | 2 | 12 months (min 11) | never | – |
| 2 | 3 | 7 months (min 6) | never | – |
| 3 | 4 | 2 months before, 6 after | 96 % | €148,000 / €303,000 |

With typical choices (H1 = 2, Head of Sales hired) Track 3 gets €130,000.

**A12. F3 chart.** €7,300 → €7,550 → €7,800 → €8,000 (+3 % a month); codebook
`basis` sentence replaced.

**A13. H2.** A win pays €40,000 in cash: "The Head of Growth chooses Lumora: the
saved search is worth €40,000". Codebook note updated.

**A14. Product sentences.** All digital (industrial: software for machine sensors;
consumer: an app for household subscriptions; food: an app for office lunch orders;
other: "a new digital product in …"). Codebook `industry` rule extended.

**A15.** "Founding teams you have been part of" now starts at 1.

**A16. One complete run per email.** If a completed session with the same email
exists, the session ends at the email step with: "Thank you. You have already taken
part in this study with this email address, so the session ends here. If you think
this is a mistake, write to decisions-in-founding@outlook.com." Nothing of that
session is kept. An incomplete earlier session does not block. Withdrawal by email
deletes every linked session (`codes_for_email`).

**A17. H4 option C.** Choosing the second round adds a deferred entry: "Head of
Sales: after the second round, the candidate with the stronger work sample is hired"
(team +1, costs +€7,000), applied in the final report. The stored answer stays C.

## Speed (0.12.1, included)

Each click used to open a new encrypted connection from Streamlit Cloud (US) to Neon
(Frankfurt), one to three times per page. Now connections are reused, and writes run
in one background thread, in order, with five retries; reads on the data page wait
for the queue first. Failed writes are listed on the data page. Tested against
Postgres 16: all 180 answers of four full sessions stored over one connection; with
a simulated 0.6 s connection setup the page wait per write fell from 0.6 s to under
1 ms.
