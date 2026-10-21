# Reference values for G1 and G3 (codebook entries)

**Author:** Amie (Chapter 9)
**Date:** 20 October 2026
**Code:** `g1_model.py`, `g3_model.py`, `g3_variants.py`, delivered with this file.

These entries replace the G1 basis and the G3 placeholder in `sim/codebook.json`.

---

## G1 · Split of the launch budget (overestimation)

### Result

**Reference step: 40/60** (`reference_value: 0.4`). This is the value already in the codebook; it is now derived from the model below. It lies inside the ladder, so both over- and underestimation can be scored.

### Model

The launch has two periods:
1. **Launch period.** The budget *B* is split between the first channel (share *s*) and tests of *K* = 3 untested alternative channels, which share the rest equally.
2. **Scale-up period.** A budget of *h · B* goes into the best channel known after the launch.

Assumptions:
- Every channel works independently with probability *p*, the base rate. Without test results, the first channel is not more likely to work than its alternatives. This is the argument of Chapter 9.1.
- A channel that works acquires customers at cost *c*. A channel that does not work is *r_f* times as efficient.
- A test of an alternative shows whether it works with probability *d* = min(1, spend per channel / *m*), where *m* is the minimum spend for a reliable read.
- The result of the first channel is always observed.

Output: expected customers over both periods, in units of *B / c*.

### Parameters

| Parameter | Base value | Source / reason |
|---|---|---|
| *p* (base rate) | 0.3 | Upper bound for an untested idea to have a true effect (Berman and Van den Bulte 2022, 6762) |
| *p*, sensitivity | 0.6 | New-product failure rate of about 40 % (Castellion and Markham 2013, 976) |
| *K* | 3 | Screen text: "two or three other channels" |
| *r_f* | 0.25 | Assumption, varied 0 to 0.5 |
| *m* | 0.2 · *B* | Assumption, varied 0.1 to 0.3 · *B* |
| *h* | 1 | Assumption, varied 0.5 to 2 |

### Expected customers (units of B/c)

| Split | *p* = 0.3 | *p* = 0.6 |
|---|---|---|
| 100/0 | 1.107 | 1.580 |
| 70/30 | 1.249 | 1.659 |
| **40/60** | **1.349** | **1.692** |
| 20/80 | 1.349 | 1.692 |

How to read this:
- In the launch period all splits yield the same expected number of customers (0.475 each at *p* = 0.3). The difference comes only from what the tests reveal for the scale-up.
- 40/60 and 20/80 are equally good, because both give every alternative enough test budget for a reliable read. The reference is **the smallest test share that reaches the maximum**, which is 40/60. A founder who tests more than that is not wrong; the score then shows underestimation, which is what the score is designed to record.
- The sensitivity value *p* = 0.6 gives the same step.

### Sensitivity

The model was run for 54 combinations: *r_f* ∈ {0, 0.25, 0.5}, *m* ∈ {0.1, 0.2, 0.3} · *B*, *h* ∈ {0.5, 1, 2} and *K* ∈ {2, 3}. The best step per combination was:

| | 40/60 | 70/30 | 20/80 | 100/0 |
|---|---|---|---|---|
| *p* = 0.3 | 25 | 18 | 11 | 0 |
| *p* = 0.6 | 24 | 16 | 14 | 0 |

40/60 is the most frequent optimum, and 100/0 is never optimal. As a robustness check, Chapter 9 recomputes the scores with 70/30 as the reference. This replaces the earlier alternative of 0.55, which rested on a Harvard Business Review figure.

### Consequence for the app

In the launch period the model gives every split the same expected number of customers. The area summary should therefore show the same number of new customers for all four splits (for example +45), not +50 for 70/30. Otherwise the game rewards a split that the scoring treats as overestimation.

### Codebook fields (existing fields only)

- `reference_value`: 0.4 (unchanged).
- `provenance`: "derived".
- `basis`: "Two-period launch model: each channel works with the base rate p; tests reveal working alternatives for the scale-up. With p = 0.3 (upper bound, Berman and Van den Bulte 2022) and p = 0.6 (Castellion and Markham 2013) the smallest test share that reaches the maximum expected customers is 40/60. Model and sensitivity grid in g1_model.py."
- `sources`: ["Berman and Van den Bulte (2022)", "Castellion and Markham (2013)", "Koning, Hasan and Chatterji (2022)"]
- `open`: "Robustness check with 70/30 as the reference, which replaces the earlier alternative of 0.55. The alternative value 0.55 is no longer used."

---

## G3 · New paying customers in month 9 (overprecision)

This assumes the app shows **9, 16, 21** and asks for **month 9** (round 2, item 3).

### Result: reference percentiles

| Percentile | 10th | 25th | 50th | 75th | 90th |
|---|---|---|---|---|---|
| New paying customers in month 9 | 22 | 34 | 56 | 91 | 127 |

- The median (56) is almost the straight-line value of 57. The reference is therefore centered on the obvious extrapolation, but much wider than it.
- An 80 % range of a calibrated forecaster should reach roughly from 22 to 127.

### Model

The model is a discrete-time Bass model (Bass 1969):

*n_t* = (*p* + *q* · *N*_{t−1} / *M*) · (*M* − *N*_{t−1})

with *n_t* the new customers in month *t* and *N* the cumulative customers.

**Priors (monthly scale).**
- *p* ~ log-uniform(0.001, 0.05)
- *q* ~ uniform(0, 0.5)
- *M* ~ log-uniform(100, 3,000)

The annual coefficients of Sultan, Farley and Lehmann (1990, 70–71), averaging .03 and .38, are not used unscaled, as Chapter 9 explains. The bounds span slower and faster channels around their monthly equivalents. *M* is the number of customers the channel can reach, between about 2 and 65 times the 46 customers it brought in its first three months.

**Conditioning.** 2 million parameter draws were weighted by a Poisson likelihood of the observed 9, 16 and 21 (effective sample size about 154,000). Month 9 was then predicted with Poisson noise.

**What the model implies.**
- The posterior medians are *p* ≈ 0.013, *q* ≈ 0.36 and *M* ≈ 890.
- In about half of the paths month 9 lies above the straight-line value of 57.
- In 2 % of the paths month 9 lies below month 3.

So the reference allows both acceleration and leveling off, as Chapter 9.2 requires.

### Sensitivity

The reference depends on the priors. These alternatives were computed:

| Prior variant | 10th | 25th | 50th | 75th | 90th |
|---|---|---|---|---|---|
| **A base** | 22 | 34 | 56 | 91 | 127 |
| B: *q* only up to 0.3 | 18 | 25 | 37 | 51 | 65 |
| C: *M* from 60 to 10,000 | 24 | 39 | 68 | 112 | 157 |
| D: *q* up to 1.0 | 9 | 28 | 67 | 146 | 261 |
| E: *p* from 0.0005 to 0.2 | 9 | 21 | 45 | 81 | 119 |

Variants B (narrower) and C (wider) serve as the robustness check for the width ratio at G3. Chapter 9 reports whether the sign of the primary result holds under both.

### Codebook fields (existing fields only)

- `quantity`: "new paying customers from the new channel in month 9, after 9, 16 and 21"
- `reference_percentiles`: {"0.10": 22, "0.25": 34, "0.50": 56, "0.75": 91, "0.90": 127}
- `provenance`: "derived"
- `basis`: "Discrete-time Bass model with broad monthly priors (p 0.001 to 0.05, q 0 to 0.5, M 100 to 3,000), conditioned on 9, 16 and 21 by Poisson likelihood. The median matches the straight-line value of 57. Model in g3_model.py."
- `sources`: ["Bass (1969)", "Sultan, Farley and Lehmann (1990)", "Van den Bulte and Stremersch (2004)"]
- `open`: "Robustness check with prior variants B (narrower) and C (wider), see g3_variants.py."

ChartMogul and SaaS Capital are no longer needed for G3.
