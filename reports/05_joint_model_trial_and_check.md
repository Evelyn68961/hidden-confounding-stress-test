# Report 05: the joint model, first trial and a check that it works

**Date:** 2026-10-07
**Scripts:** `scripts/06_joint_model_trial.py`, `scripts/07_joint_model_check.py`
**Model:** `src/stresstest/joint_model.py`
**Commit:** 8840eb7

## Question

Step 2 showed that a causal forest cannot correct for a hidden factor. Does a
model that describes drug choice and outcome together do better? Before
running it on all 140 datasets: how long does one fit take, does the model
detect the hidden factor at all, and does the code work when the task is easy?

## The model

    outcome     = baseline(features) + effect(features) × drug + outcome error
    drug choice = 1 if  choice(features) + choice error > 0

The two errors are jointly normal with correlation **rho**. Baseline, effect
and choice are straight-line functions of the seven recorded features. This is
the classic endogenous-treatment model, the simplest member of the family of
joint outcome and treatment models.

- If nothing hidden drives both drug choice and outcome, rho is 0.
- A hidden factor that pushes both shows up as a non-zero rho, and the model
  then shifts its estimate of the drug effect.

A **plain** version with rho fixed at 0 is fitted alongside. It is an ordinary
regression with interactions and, like the forest, assumes nothing is hidden.

Fitted in PyMC with the NUTS sampler: four chains, 1,000 warm-up and 1,000
kept draws each.

**The simulated patients contain no instrument** (no feature that moves drug
choice without affecting the outcome). So rho can only be learned from the
shape of the outcome's distribution within each drug group.

## Trial: four diabetes datasets (script 06)

One dataset per setting, 5,000 patients, seed 0. Errors in mmol/mol.

| Hidden factor | Model | rho, mean (95% interval) | Error in the average effect | Typical error per patient | 95% intervals containing the truth | Sent to the worse drug | Seconds |
|---|---|---|---|---|---|---|---|
| Off | plain | fixed at 0 | −0.24 | 1.03 | 99.2% | 8.5% | 27 |
| Off | joint | −0.01 (−0.19 to 0.17) | 0.08 | 1.02 | 100.0% | 7.4% | 69 |
| Linear, 1 | plain | fixed at 0 | 4.04 | 4.30 | 16.1% | 33.4% | 31 |
| Linear, 1 | joint | 0.00 (−0.18 to 0.18) | 4.02 | 4.29 | 78.0% | 33.3% | 81 |
| Threshold, 1 | plain | fixed at 0 | 2.90 | 3.37 | 37.7% | 25.1% | 30 |
| Threshold, 1 | joint | 0.00 (−0.16 to 0.16) | 2.91 | 3.38 | 87.0% | 25.2% | 72 |
| Effect, 1 | plain | fixed at 0 | 2.83 | 3.37 | 37.3% | 24.7% | 31 |
| Effect, 1 | joint | 0.00 (−0.15 to 0.16) | 2.76 | 3.31 | 81.2% | 24.3% | 72 |

## Check: data made from the model's own assumptions (script 07)

20,000 abstract patients with two features, a very uneven choice of drug, and
a known link.

| True rho | Model | Estimated rho (95% interval) | Error in the average effect | Typical error per patient | 95% intervals containing the truth |
|---|---|---|---|---|---|
| 0 | plain | fixed at 0 | −0.03 | 0.06 | 100% |
| 0 | joint | −0.01 (−0.08 to 0.06) | 0.03 | 0.06 | 100% |
| 0.6 | plain | fixed at 0 | 3.85 | 3.87 | 0% |
| 0.6 | joint | 0.61 (0.57 to 0.64) | 0.06 | 0.22 | 94% |

## Reading

- **The code works.** When the link is strong and the data match the model's
  assumptions, the joint model recovers rho (0.61 for a true 0.6) and removes
  the bias entirely (0.06 against 3.85 for the plain model).
- **In the diabetes simulation it does not detect the hidden factor.** Rho
  stays centred on zero in every setting. At strength 1 the true correlation
  between the two errors is about 0.16, which lies just inside the model's
  95% interval for rho. The data cannot tell 0 from 0.16.
- **So the bias is not corrected.** The joint model's error in the average
  effect, and the share of patients sent to the worse drug, are the same as
  the plain model's.
- **But its intervals become far more honest.** Because rho is uncertain, the
  intervals for each patient's effect widen. Coverage rises from 16–38% to
  78–87% at strength 1. The joint model does not fix the answer; it stops
  being confident about a wrong one.
- **The difference between the two cases is identification, not the code.**
  The check has 20,000 patients, a link of 0.6 and a strongly uneven choice
  of drug. The diabetes simulation has 5,000 patients, a link near 0.16 and
  no instrument.
- **A fit takes about 30 seconds (plain) or 75 seconds (joint)** on a laptop
  without a C compiler, so the full grid is affordable.

## Limits

- **One dataset per setting.** The trial shows the pattern; the numbers will
  move. The full grid (script 08) gives 20 datasets per setting.
- **These models are given the right form.** The simulated effects are
  straight lines in the features, and both models assume straight lines. That
  is why they send fewer patients to the worse drug than the forest did with
  nothing hidden (about 8% against 16.5%). It is not a fair comparison of
  flexible and simple models, and should not be read as one.
- **The joint model assumes normal errors and one noise level.** The
  simulation has a logistic choice of drug and more noise on the GLP-1 drug.
  The threshold shape breaks the normality assumption on purpose.
- **Over-coverage with nothing hidden.** Both models' intervals contain the
  truth about 99–100% of the time, more than the 95% they claim.
- The check uses data unlike the diabetes patients. It shows the code is
  right, not that the model would work on real records.

## Next

Run both models on all 140 datasets of step 2 (`scripts/08_joint_model_grid.py`)
and compare them with the forest, setting by setting.
