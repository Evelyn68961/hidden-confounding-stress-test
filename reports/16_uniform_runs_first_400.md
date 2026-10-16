# 16. Uniform runs: the first 400 datasets

**Date:** 2026-10-16. **Script:** `scripts/14_uniform_runs.py`, on EVELYN68961PC.
**Results:** `results/generator-v2/uniform_2000/EVELYN68961PC.csv`, 720 rows, up to
commit 280e27f.

## Question

Earlier runs grew step by step. Some settings rested on 10 datasets and some on
20, and the PyMC models kept 1,000 draws per chain. Do the results on the slides
hold when every one of those settings has 20 datasets and 2,000 draws per chain?

## What was run

The plain regression and the joint model with a noise level per drug, refitted
on 20 datasets per setting with 2,000 draws per chain, for the settings shown on
the slides. The same seeds were used as before, so dataset r of a setting holds
the same simulated patients as in the earlier runs.

- 400 datasets, 720 fit rows, no errors.
- 19 of 20 datasets for each 20,000-patient setting. The last two were stopped
  in progress on 2026-10-16 to free memory for the causal forest refit, and are
  rerun in phase 3.
- Rows carry three code labels (91a1180, c0c56a8, 40f0b0a) because of restarts
  and results-only commits. `git diff --stat c0c56a8 HEAD -- src scripts
  pyproject.toml uv.lock` is empty for each, so the code is the same.
- Not in this batch: the hidden factor at strength 0.5 with an ideal instrument,
  the practice-level instruments with no hidden factor, and the instrument as a
  feature at strength 0.5. They are in phase 3.

## Results

Bias and RMSE in mmol/mol; misclassification rate in %. "Before" is the figure
on the slides of 2026-10-12, with its number of datasets. Monte Carlo standard
errors are in brackets.

### Ideal instrument, strength 1 (slide 15)

Before: 20 datasets, 1,000 draws. Now: 20 datasets, 2,000 draws.

| Hidden factor | Joint bias, before | Joint bias, now | Joint RMSE, now | Joint misclassification, now |
|---|---|---|---|---|
| None | 0.12 | 0.12 (0.35) | 1.55 | 16.3 |
| Linear | −0.01 | −0.02 (0.39) | 1.69 | 18.1 |
| Threshold | 0.12 | 0.12 (0.41) | 1.77 | 18.4 |
| Effect | 1.20 | 1.20 (0.39) | 2.07 | 20.1 |

The plain regression is unchanged (3.72, 2.83, 2.60, 0.13). ρ for the linear
shape is 0.16 (0.05 to 0.27), as before.

### No instrument, linear hidden factor at strength 1 (slide 17)

| Patients | Model | Bias, before (10) | Bias, now | RMSE, before | RMSE, now | Misclassification, before | Misclassification, now |
|---|---|---|---|---|---|---|---|
| 5,000 | Plain | 4.20 | 4.39 (0.11) | 4.22 | 4.42 | 38.2 | 39.0 |
| 5,000 | Joint | 0.68 | 1.38 (1.02) | 5.22 | 4.66 | 36.8 | 35.0 |
| 20,000 | Plain | 4.32 | 4.32 (0.06) | 4.32 | 4.33 | 38.6 | 38.5 |
| 20,000 | Joint | 1.97 | 2.25 (0.92) | 3.82 | 4.49 | 28.6 | 30.6 |

The 20,000-patient rows rest on 19 datasets. ρ: 95% interval −0.40 to 0.49 at
5,000 patients (mean of the per-dataset bounds).

Convergence improved with 2,000 draws. Among the 20 joint fits at 5,000 patients,
1 had a largest R-hat above 1.01 (1.011). Across the 78 no-instrument joint fits,
5 did, with a maximum of 1.016. Every fit with an instrument had a largest R-hat
of 1.004 or less.

### Less-than-ideal instruments, linear hidden factor at strength 1 (slide 19)

Before: 10 datasets for every row except the ideal one.

| Instrument | Plain, before | Plain, now | Joint, before | Joint, now | Joint misclassification, before | now |
|---|---|---|---|---|---|---|
| Practice-level, 100 | 3.90 | 3.87 | −0.39 | −0.15 (0.34) | 16.2 | 16.5 |
| Practice-level, 25 | 3.77 | 3.77 | −0.38 | −0.28 (0.32) | 16.9 | 15.2 |
| Weaker | 4.10 | 4.16 | 0.23 | 0.25 (0.70) | 26.2 | 25.3 |
| Direct effect, 0.5 | 4.14 | 4.09 | 3.13 | 3.18 (0.40) | 28.8 | 29.8 |
| Direct effect, 1 | 4.51 | 4.47 | 6.41 | 6.42 (0.42) | 44.8 | 44.9 |

### No hidden factor (slide 20)

| Instrument | Plain, before | Plain, now | Joint, before | Joint, now | Joint misclassification, before | now |
|---|---|---|---|---|---|---|
| Weaker | 0.01 | 0.00 | 0.20 | 0.13 (0.63) | 23.0 | 22.7 |
| Direct effect, 0.5 | 0.57 | 0.55 | 3.02 | 3.05 (0.36) | 28.9 | 29.0 |
| Direct effect, 1 | 0.99 | 0.98 | 5.98 | 5.93 (0.36) | 44.8 | 44.6 |

The plain regression's misclassification rate for these rows is now 11.4, 11.0
and 13.3 (before: 11.5, 11.4, 13.6).

### The instrument as a feature (slide 21)

Increase in the plain regression's bias when the ideal instrument is added as a
feature, paired by dataset.

| Hidden factor | Before (10) | Now (20) |
|---|---|---|
| None | +0.01 (0.06) | −0.08 (0.07) |
| Linear, strength 1 | +0.49 (0.09) | +0.47 (0.06) |
| Threshold, strength 1 | +0.39 (0.08) | +0.40 (0.06) |
| Effect, strength 1 | +0.36 (0.09) | +0.34 (0.06) |

## How to read it

- **Every answer line on the slides still holds.** No sign changed, and every
  difference between before and now is within about two Monte Carlo standard
  errors of the earlier figure.
- **Slide 15 is unchanged in substance.** Its settings already had 20 datasets;
  doubling the draws moved no figure by more than 0.01.
- **Without an instrument, the joint model's gain is smaller than the 10-dataset
  figures suggested.** At 20,000 patients its RMSE is now 4.49 against 4.33 for
  the plain regression, where it was 3.82 against 4.32. This strengthens "did not
  clearly lower the RMSE at either sample size".
- **The practice-level instruments** give −0.15 and −0.28, closer to zero than
  the earlier −0.39 and −0.38.
- **The R-hat sentence on slide 17 is out of date.** With 2,000 draws, 1 of the
  20 fits on that slide has a largest R-hat above 1.01, not a quarter.

## Limits

- Three settings shown on the slides are not yet refitted (see "What was run").
- The 20,000-patient settings have 19 datasets until phase 3 finishes.
- The causal forest is not part of this script. Its refit with 1,000 warm-up
  draws is running separately.

## Next

1. Phase 3: the remaining 260 datasets, after the causal forest refit.
2. Update the slides, the README and SUMMARY.md to these figures, after review.
