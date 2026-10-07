# Report 01: causal forest with nothing hidden

**Date:** 2026-10-07
**Script:** `scripts/01_causal_forest_no_hidden_factor.py`
**Commits:** 2e598c1 (first run, one chain), 3d07222 (rerun, four chains)

## Question

Before switching the hidden factor on, does the Bayesian causal forest recover
each patient's true drug effect when it can see everything that drives drug
choice? This run is the reference point for all later runs.

## What was run

- 5,000 simulated patients, hidden factor off (`strength = 0`), seed 1.
- Bayesian causal forest from `stochtree` with default priors. The model
  estimates the propensity score itself from the recorded features.
- **First run:** one chain, 10 grow-from-root sweeps, 1,000 draws kept.
- **Rerun:** four chains, each started from a different grow-from-root
  ensemble, 200 warm-up draws discarded and 500 kept per chain.

The rerun was made because a single chain gives no way to check that the
sampler has settled. Four chains allow an R-hat check.

## Result

True effects (GLP-1 receptor agonist minus SGLT2 inhibitor, change in HbA1c)
have a mean of −0.65 mmol/mol and a standard deviation of 2.69 mmol/mol across
patients.

| Measure | One chain | Four chains |
|---|---|---|
| Estimated average effect | −0.51 mmol/mol | −0.52 mmol/mol |
| Error in the average effect | 0.14 mmol/mol | 0.13 mmol/mol |
| Typical error in one patient's effect (RMSE) | 0.80 mmol/mol | 0.78 mmol/mol |
| 95% intervals containing the truth | 99.7% | 99.6% |
| Patients sent to the worse drug | 5.7% | 5.5% |
| HbA1c lowering lost per patient | 0.02 mmol/mol | 0.02 mmol/mol |

Convergence, four-chain run:

| Check | Value |
|---|---|
| R-hat, average effect | 1.002 |
| R-hat, worst single patient | 1.050 |
| Patients with R-hat above 1.01 | 18% |

Run time on a laptop: about 40 seconds for one chain, about 90 seconds for four.

## Reading

- The forest recovers most of the real differences between patients: a typical
  error of 0.78 against a spread of 2.69.
- The patients sent to the worse drug are those for whom the two drugs are
  nearly equal, so the loss in HbA1c lowering is close to zero.
- The intervals are wider than they need to be here: they contain the truth
  far more often than 95% of the time.
- The scores did not change materially between one chain and four.
- The chains agree on the average effect. For individual patients agreement is
  looser: about one in five has an R-hat above 1.01, none above 1.05.

## Limits

- One simulated dataset. The numbers will move with the seed.
- The forest is scored on the patients it was fitted to. The score uses the
  true effect, which the model never sees, but a held-out set would be stricter.
- The data are generated with an additive structure (prognosis plus effect
  times treatment), which is the structure the model assumes.
- Chains are short. Per-patient R-hat does not meet the 1.01 standard.

## Next

Switch the hidden factor on across three strengths and three shapes, with
about 20 simulated datasets per setting.
