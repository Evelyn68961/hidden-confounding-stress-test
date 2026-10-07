# Report 01: causal forest with nothing hidden

**Date:** 2026-10-07
**Script:** `scripts/01_causal_forest_no_hidden_factor.py`
**Commits:** 2e598c1 (run A), 3d07222 (run B), the commit that adds this version of the report (run C)

## Question

Before switching the hidden factor on, does the Bayesian causal forest recover
each patient's true drug effect when it can see everything that drives drug
choice? This run is the reference point for all later runs.

## What was run

5,000 simulated patients, hidden factor off (`strength = 0`), seed 1. Bayesian
causal forest from `stochtree` with default priors. The model estimates the
propensity score itself from the recorded features.

The run was repeated three times as the project changed:

| Run | Patients | Chains |
|---|---|---|
| A | First generator, effect sizes chosen by hand | 1 chain, 1,000 draws |
| B | Same generator | 4 chains, 200 warm-up + 500 draws each |
| C | Generator calibrated to a published cohort (see `docs/calibration.md`) | 4 chains, 500 warm-up + 2,000 draws each |

- **A to B:** a single chain gives no way to check that the sampler has
  settled. Four chains allow an R-hat check.
- **B to C, patients:** the hand-picked numbers were replaced by ones tuned to
  the cohort in Cardoso et al., *Diabetologia* 2024. The calibrated patients
  are a harder case: one in four gets the GLP-1 drug instead of one in two, the
  outcome is noisier (residual SD 12.5 instead of 10), and BMI, sex and
  starting HbA1c now drive both drug choice and the drug effect.
- **B to C, chains:** in run B, 18% of patients had an R-hat above 1.01. With
  2,000 draws per chain none does.

## Result

| Measure | Run A | Run B | Run C |
|---|---|---|---|
| True average effect, mmol/mol | −0.65 | −0.65 | −0.16 |
| Spread of true effects (SD) | 2.69 | 2.69 | 3.07 |
| Estimated average effect | −0.51 | −0.52 | 0.76 |
| Error in the average effect | 0.14 | 0.13 | 0.92 |
| Typical error in one patient's effect (RMSE) | 0.80 | 0.78 | 1.48 |
| 95% intervals containing the truth | 99.7% | 99.6% | 98.4% |
| Patients sent to the worse drug | 5.7% | 5.5% | 16.5% |
| HbA1c lowering lost per patient, mmol/mol | 0.02 | 0.02 | 0.16 |
| R-hat, average effect | not checked | 1.002 | 1.000 |
| R-hat, worst single patient | not checked | 1.050 | 1.009 |
| Patients with R-hat above 1.01 | not checked | 18% | 0% |

Run time on a laptop: about 40 seconds (A), 90 seconds (B), 5.5 minutes (C).

## Reading

- **Run C is the reference from here on.** The earlier runs used an easier,
  less realistic set of patients.
- **With realistic patients the forest is noticeably less accurate, even with
  nothing hidden.** Its typical error per patient is 1.48 mmol/mol against a
  spread of 3.07, and 16.5% of patients would be sent to the worse drug.
- **The average effect is off by 0.92 mmol/mol in this one dataset.** With
  1,250 patients on the GLP-1 drug and an outcome SD of about 15, chance alone
  gives a standard error near 0.5 for the average effect, so this is roughly
  two standard errors. One dataset cannot say whether it is chance or a
  systematic lean. The 20 repeats at strength 0 in the next step will.
- **The sampler has settled.** Every patient's R-hat is at or below 1.009.
- The intervals still contain the truth more often than 95% of the time.

## Limits

- One simulated dataset per run. The numbers will move with the seed.
- 5,000 patients. The published development cohort had about 27,000, so a
  real model would be more precise than this one.
- The forest is scored on the patients it was fitted to. The score uses the
  true effect, which the model never sees, but a held-out set would be stricter.
- The data are generated with an additive structure (prognosis plus effect
  times treatment), which is the structure the model assumes.

## Next

Switch the hidden factor on: two strengths and three shapes, plus strength 0,
with 20 simulated datasets per setting (`scripts/03_causal_forest_grid.py`).
