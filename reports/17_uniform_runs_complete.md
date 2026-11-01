# 17. Uniform runs complete, and the causal forest refit

**Date:** 2026-11-01. **Results:** `results/generator-v2/uniform_2000/EVELYN68961PC.csv`
(1,180 rows, 660 datasets) and `results/generator-v2/forest_warmup_1000/EVELYN68961PC.csv`
(140 rows), at commit 18eb79e. This report completes report 16.

## Question

With every setting at 20 datasets and 2,000 draws per chain, what are the final
figures? Does a longer warm-up change the causal forest's results?

## What was run

- **Uniform runs** (`scripts/14_uniform_runs.py`): the plain regression and the
  joint model with a noise level per drug on every setting, finished 2026-10-22.
  No errors. The code under `src`, `scripts`, `pyproject.toml` and `uv.lock` was
  the same at every restart.
- **Causal forest refit** (`scripts/03_causal_forest_grid.py --warmup 1000`):
  140 fits with 1,000 warm-up draws instead of 500, finished 2026-10-21.

## Results

Bias and RMSE in mmol/mol, misclassification rate in %. Every row has 20 datasets.
Monte Carlo standard errors are in brackets.

### Causal forest: 500 against 1,000 warm-up draws

| Hidden factor | Bias, 500 | Bias, 1,000 | Coverage, 500 | Coverage, 1,000 | Misclassification, 500 | Misclassification, 1,000 |
|---|---|---|---|---|---|---|
| None | 0.12 | 0.12 | 94.3 | 94.4 | 16.5 | 16.5 |
| Linear, 0.5 | 1.39 | 1.39 | 87.3 | 87.4 | 21.2 | 21.2 |
| Threshold, 0.5 | 1.06 | 1.06 | 90.5 | 90.6 | 19.2 | 19.2 |
| Effect, 0.5 | 1.06 | 1.05 | 90.1 | 90.2 | 19.3 | 19.3 |
| Linear, 1 | 4.44 | 4.44 | 27.6 | 27.7 | 43.2 | 43.1 |
| Threshold, 1 | 3.52 | 3.52 | 45.7 | 45.6 | 37.2 | 37.2 |
| Effect, 1 | 3.18 | 3.18 | 49.8 | 50.0 | 34.2 | 34.2 |

The longest warm-up did not improve the largest single-patient R-hat: its maximum
is 1.149, in one fit, against 1.042 before. Two fits exceed 1.05. For the average
effect the largest R-hat is 1.003.

### Ideal instrument

| Hidden factor | Bias, plain | Bias, joint | RMSE, plain | RMSE, joint | Misclassification, plain | Misclassification, joint |
|---|---|---|---|---|---|---|
| None | 0.13 (0.12) | 0.12 (0.35) | 0.54 | 1.55 | 9.7 | 16.3 |
| Linear, 1 | 3.72 (0.11) | −0.02 (0.39) | 3.75 | 1.69 | 34.7 | 18.1 |
| Threshold, 1 | 2.83 (0.12) | 0.12 (0.41) | 2.87 | 1.77 | 28.0 | 18.4 |
| Effect, 1 | 2.60 (0.11) | 1.20 (0.39) | 2.64 | 2.07 | 26.0 | 20.1 |
| Linear, 0.5 | 1.07 (0.12) | 0.05 (0.36) | 1.18 | 1.57 | 14.4 | 16.5 |
| Threshold, 0.5 | 0.79 (0.11) | 0.14 (0.36) | 0.93 | 1.59 | 13.0 | 16.6 |
| Effect, 0.5 | 0.77 (0.11) | 0.41 (0.36) | 0.92 | 1.62 | 13.0 | 16.5 |

### No instrument, linear hidden factor at strength 1

| Patients | Bias, plain | Bias, joint | RMSE, plain | RMSE, joint | Misclassification, plain | Misclassification, joint |
|---|---|---|---|---|---|---|
| 5,000 | 4.39 (0.11) | 1.38 (1.02) | 4.42 | 4.66 | 39.0 | 35.0 |
| 20,000 | 4.32 (0.05) | 2.24 (0.87) | 4.33 | 4.40 | 38.5 | 30.2 |

ρ: 95% interval −0.40 to 0.49 at 5,000 patients and −0.28 to 0.37 at 20,000 (mean
of the per-dataset bounds). The largest R-hat exceeded 1.01 in 1 of 20 joint fits
at each sample size (maximum 1.013). Across all 80 no-instrument joint fits, 5 did
(maximum 1.016). With an instrument, the largest R-hat was 1.004.

### Less-than-ideal instruments

| Instrument | Linear, strength 1: bias plain | bias joint | misclassification plain | misclassification joint | No hidden factor: bias plain | bias joint | misclassification plain | misclassification joint |
|---|---|---|---|---|---|---|---|---|
| Ideal | 3.72 | −0.02 (0.39) | 34.7 | 18.1 | 0.13 | 0.12 (0.35) | 9.7 | 16.3 |
| Practice-level, 100 | 3.87 | −0.15 (0.34) | 35.3 | 16.5 | 0.08 | 0.10 (0.31) | 10.6 | 14.8 |
| Practice-level, 25 | 3.77 | −0.28 (0.32) | 34.2 | 15.2 | −0.08 | −0.23 (0.31) | 11.5 | 16.3 |
| Weaker | 4.16 | 0.25 (0.70) | 36.8 | 25.3 | 0.00 | 0.13 (0.63) | 11.4 | 22.7 |
| Direct effect, 0.5 | 4.09 | 3.18 (0.40) | 37.1 | 29.8 | 0.55 | 3.05 (0.36) | 11.0 | 29.0 |
| Direct effect, 1 | 4.47 | 6.42 (0.42) | 39.4 | 44.9 | 0.98 | 5.93 (0.36) | 13.3 | 44.6 |

### The instrument as a feature

Bias of the plain regression with the ideal instrument left out or added as a
feature, and the paired increase with its 95% interval.

| Hidden factor | Left out | As a feature | Increase | 95% interval |
|---|---|---|---|---|
| None | 0.13 | 0.05 | −0.08 (0.07) | −0.22 to 0.07 |
| Linear, 0.5 | 1.07 | 1.19 | +0.13 (0.06) | 0.00 to 0.25 |
| Threshold, 0.5 | 0.79 | 0.87 | +0.08 (0.06) | −0.05 to 0.20 |
| Effect, 0.5 | 0.77 | 0.86 | +0.09 (0.06) | −0.03 to 0.22 |
| Linear, 1 | 3.72 | 4.19 | +0.47 (0.06) | 0.36 to 0.58 |
| Threshold, 1 | 2.83 | 3.22 | +0.40 (0.06) | 0.28 to 0.51 |
| Effect, 1 | 2.60 | 2.94 | +0.34 (0.06) | 0.23 to 0.45 |

## How to read it

- **The longer warm-up changed nothing that matters.** No forest figure moved by
  more than 0.2 percentage points or 0.01 mmol/mol.
- **The conclusions of the 2026-10-12 deck hold**, with one exception below.
- **One claim weakens.** With 10 datasets the slides said that adding the
  instrument as a feature increased the bias by 0.10 to 0.17 at strength 0.5. With
  20 datasets the increase is 0.08 to 0.13, and all three 95% intervals reach
  zero. The increase is clear only at strength 1 (0.34 to 0.47).
- **Without an instrument the joint model's RMSE is not lower at either sample
  size** (4.66 against 4.42, and 4.40 against 4.33). Its misclassification rate is
  lower at 20,000 patients (30.2 against 38.5).
- **The sent email's claims all hold.**

## Limits

- Twenty datasets give a Monte Carlo standard error of about 0.4 on the joint
  model's bias. An MCSE of 0.1 would need about 300.
- The single-patient R-hat of the causal forest remains above 1.01 in some fits
  after the longer warm-up. The figures above are unaffected.

## Next

Update the slides, the README and SUMMARY.md to these figures, after review.
