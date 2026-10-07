# Report 06: the joint model on all 140 datasets, without an instrument

**Date:** 2026-10-07
**Script:** `scripts/08_joint_model_grid.py`
**Results:** `results/generator-v2/joint_model/EVELYN68961.csv` (280 rows: two models × 140 datasets)
**Code commit recorded in every row:** 8840eb7

## Question

Report 05 tried the joint model on one dataset per setting. Does the pattern
hold across 20 datasets per setting? Specifically: without an instrument, does
a joint model of drug choice and outcome detect a hidden factor, correct the
bias, or at least report honest uncertainty?

## What was run

The same 140 simulated datasets as step 2 (same settings, same seeds, 5,000
patients each). Two models per dataset, fitted in PyMC with four chains of
1,000 warm-up and 1,000 kept draws:

- **plain:** a regression in which the drug effect varies with the features.
  It assumes nothing is hidden. It has the same structure as the published
  treatment selection models (an outcome regression with drug-by-feature
  interactions and one error term), with straight lines where they use smooth
  curves.
- **joint:** the same, plus a probit model of drug choice, with the two
  errors jointly normal with correlation rho.

## Result

Averages across 20 datasets per setting. Errors in mmol/mol.

| Hidden factor | Model | rho, mean (average 95% interval) | Error in the average effect | Typical error per patient | 95% intervals containing the truth | Sent to the worse drug | HbA1c lost per patient |
|---|---|---|---|---|---|---|---|
| Off | plain | fixed at 0 | 0.04 | 1.37 | 92.0% | 12.1% | 0.10 |
| Off | joint | 0.00 (−0.17 to 0.17) | −0.01 | 1.39 | 99.9% | 12.2% | 0.10 |
| Linear, 0.5 | plain | fixed at 0 | 1.33 | 1.82 | 77.1% | 16.3% | 0.18 |
| Linear, 0.5 | joint | 0.00 (−0.17 to 0.17) | 1.26 | 1.81 | 99.4% | 16.2% | 0.17 |
| Linear, 1 | plain | fixed at 0 | 4.39 | 4.56 | 9.4% | 39.0% | 0.81 |
| Linear, 1 | joint | 0.01 (−0.18 to 0.20) | 4.14 | 4.33 | 78.4% | 37.6% | 0.75 |
| Threshold, 0.5 | plain | fixed at 0 | 1.01 | 1.62 | 84.3% | 14.5% | 0.15 |
| Threshold, 0.5 | joint | 0.00 (−0.17 to 0.17) | 1.00 | 1.66 | 99.7% | 14.8% | 0.15 |
| Threshold, 1 | plain | fixed at 0 | 3.48 | 3.73 | 22.7% | 32.9% | 0.59 |
| Threshold, 1 | joint | 0.00 (−0.16 to 0.17) | 3.40 | 3.66 | 84.1% | 32.4% | 0.57 |
| Effect, 0.5 | plain | fixed at 0 | 1.01 | 1.64 | 83.4% | 14.5% | 0.15 |
| Effect, 0.5 | joint | 0.00 (−0.17 to 0.16) | 1.01 | 1.68 | 99.6% | 14.9% | 0.15 |
| Effect, 1 | plain | fixed at 0 | 3.17 | 3.46 | 27.2% | 30.4% | 0.52 |
| Effect, 1 | joint | 0.00 (−0.16 to 0.17) | 3.07 | 3.37 | 85.2% | 29.7% | 0.49 |

In none of the 140 joint fits did the 95% interval for rho exclude zero.

For comparison, the causal forest on the same datasets (report 03):

| Hidden factor | Forest: error in the average effect | Forest: 95% intervals containing the truth | Forest: sent to the worse drug |
|---|---|---|---|
| Off | 0.12 | 94.3% | 16.5% |
| Linear, 1 | 4.44 | 27.6% | 43.2% |
| Threshold, 1 | 3.52 | 45.7% | 37.2% |
| Effect, 1 | 3.18 | 49.8% | 34.2% |

## Reading

1. **Without an instrument, the joint model does not detect the hidden
   factor.** Rho is centred on zero in every setting, and its interval is the
   same width whether or not a hidden factor is present. At strength 1 the
   true correlation between the two errors is about 0.16, which lies inside
   that interval.
2. **So it does not correct the bias.** Its error in the average effect is
   within 0.25 mmol/mol of the plain model's everywhere, and it sends the same
   share of patients to the worse drug.
3. **What it does change is the uncertainty.** Not knowing rho, it widens its
   intervals. At strength 1, coverage rises from 9–27% (plain) to 78–85%
   (joint). It stops being confident about a wrong answer.
4. **The price is over-wide intervals when nothing is wrong.** With the hidden
   factor off or moderate, the joint model's intervals contain the truth more
   than 99% of the time. They are wider than they need to be.
5. **The plain regression fails in the same way as the forest.** Its error in
   the average effect matches the forest's and the crude comparison's (4.39,
   4.44 and 4.40 for the linear shape at strength 1). Model flexibility is not
   the issue. Neither model has any information about what is hidden.
6. **This matches the method's own literature.** Conley et al. (*J
   Econometrics* 2008) note that with little information such a model shrinks
   "toward the case of no endogeneity". Their method obtains its information
   from an instrument, and these datasets contain none by design.

## Checks

- **Convergence.** The worst R-hat for any patient's effect in any fit was
  1.009.
- **The model works when it can.** Report 05 shows it recovers a strong known
  link (0.61 for a true 0.6) in data made from its own assumptions.
- **No duplicates and one code commit** across the 280 rows.

## Limits

- **Do not read plain against forest as simple against flexible.** The
  simulated effects are straight lines in the features, and the plain and
  joint models assume straight lines. That is why they send fewer patients to
  the worse drug than the forest when nothing is hidden (12% against 16.5%).
  The forest had to learn the form.
- **The plain model's intervals are slightly short** even with nothing hidden
  (92.0% against a nominal 95%). The simulation has more noise on the GLP-1
  drug; the model assumes one noise level.
- **One simple joint model.** Normal errors, a probit choice model, straight
  lines. The models proposed for real use are more flexible (Dirichlet process
  mixtures for the errors, Bayesian additive regression trees for the mean).
- The limits of report 03 apply: a simulation, 5,000 patients, a hidden factor
  unrelated to every recorded feature.

## Next

Give the simulated patients an instrument and repeat (script 10). Separately,
test whether the published concordant-against-discordant validation check
notices a model misled by a hidden factor (script 09).
