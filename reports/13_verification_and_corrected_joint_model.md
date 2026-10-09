# Report 13: verification, and a joint model with a noise level per drug

**Date:** 2026-10-09
**Scripts:** `checks/independent_check_1.py`, `checks/independent_check_2.py` (the checks); `scripts/12_followup_runs.py --run per_drug_noise` (the run); `scripts/13_summarise_followups.py` (the table)
**Results:** `results/generator-v2/per_drug_noise/EVELYN68961.csv` (110 rows, one model × 110 datasets)
**Table:** `reports/tables/followup_per_drug_noise.csv`
**Code commit recorded in every row:** 39d276b

## Question

Are the numbers in reports 01 to 12 right, and are the explanations given for
them right?

## What was done

1. **An independent code review.** A reviewer who had not seen the reports
   read the generator, the models, the scoring and the run and summary
   scripts, looking for errors that would change a reported number.
2. **A second method.** The key results were recomputed with methods that
   share no code with the PyMC models and use only numpy and scipy:
   - least squares with drug × feature terms, against the plain regression;
   - a classical two-step correction (a probit first stage fitted by maximum
     likelihood, then its generalised residual added to the outcome
     regression), against the joint model.
3. **A corrected joint model.** The review found a mismatch between the joint
   model and the simulated patients (below). The joint model was given an
   option that removes it and was fitted again: with the ideal instrument of
   strength 1.0 (seven hidden-factor settings), and without an instrument at
   5,000 and 20,000 patients (hidden factor off, and linear at strength 1).
   Ten datasets each, the same seeds as before.

## Findings

### 1. No coding error was found

The review found no error that changes a reported number. Every headline
number was recomputed from the saved rows and matched. Four datasets were
refitted from scratch and gave the saved values to two decimals.

### 2. The plain regression is confirmed exactly

| Setting (ten datasets) | Plain regression (PyMC) | Least squares |
|---|---|---|
| Ideal instrument present, linear hidden factor at 1 | 3.77 | 3.77 |
| Ideal instrument present, nothing hidden | 0.15 | 0.15 |
| Instrument added as a feature, linear 1 | 4.26 | 4.26 |
| Invalid instrument (1 mmol/mol), linear 1 | 4.51 | 4.52 |
| No instrument, linear 1, 5,000 patients | 4.20 | 4.21 |
| No instrument, linear 1, 20,000 patients | 4.32 | 4.32 |

Errors in the average effect, mmol/mol. This also confirms the generator and
the scoring, which both methods share.

### 3. A mismatch between the joint model and the simulated patients

The joint model of reports 05 to 12 assumes one noise level for both drugs.
The simulated patients have two: results vary more on the GLP-1 drug (an SD
of 15.4) than on the SGLT2 drug (12.6), as in the published cohort.

In this kind of model a hidden link implies a particular relation between the
two groups' variation. The data contradict that relation for a reason that
has nothing to do with a hidden link, and the model reads the contradiction
as evidence against one. So its estimate of the link is pulled towards zero.

The reviewer confirmed this on the model's likelihood directly, and the
two-step method, which does not make the one-noise assumption, did not show
the problem.

### 4. With an instrument, the corrected model removes nearly all of the bias

Ideal instrument of strength 1.0, ten datasets, errors in the average effect:

| Hidden factor | Plain regression | Joint, one noise level (report 08) | Joint, noise per drug | Two-step check |
|---|---|---|---|---|
| Off | 0.15 | 0.08 | 0.05 | 0.03 |
| Linear, 0.5 | 1.06 | 0.26 | −0.05 | −0.01 |
| Linear, 1 | 3.77 | 0.95 | −0.08 | 0.06 |
| Threshold, 0.5 | 0.79 | 0.33 | 0.12 | 0.14 |
| Threshold, 1 | 2.91 | 1.06 | 0.22 | 0.34 |
| Effect, 0.5 | 0.78 | 0.45 | 0.33 | 0.29 |
| Effect, 1 | 2.65 | 1.58 | 1.21 | 1.10 |

- **Share of the error removed at strength 1:** all of it for the linear form
  (75% before), 92% for threshold (64% before), 54% for effect (40% before).
- **The corrected model and the two-step check agree** to within 0.15 in every
  row. They are independent of each other.
- **The link is now estimated correctly:** rho 0.17 (0.06 to 0.27) for the
  linear form at strength 1, where the true value is about 0.16. Report 08
  had 0.13.
- **The effect form is still the hardest.** About half the bias remains with
  either method, so this is a property of the problem and not of one model.

### 5. The corrected model is less biased and more variable

Linear hidden factor at strength 1, ideal instrument, ten datasets:

| Model | Average error | Spread across datasets (SD) | Typical distance of one dataset's answer from the truth | Sent to the worse drug | Coverage |
|---|---|---|---|---|---|
| Plain regression | 3.77 | 0.55 | 3.81 | 34.8% | 13.6% |
| Joint, one noise level | 0.95 | 1.32 | 1.58 | 16.5% | 91.9% |
| Joint, noise per drug | −0.08 | 1.70 | 1.61 | 17.5% | 96.7% |

Removing the mismatch removes the bias and adds spread, so the answer from
any one dataset is no closer to the truth than before (1.61 against 1.58).
With nothing hidden, the corrected model sends 15.5% of patients to the worse
drug, against 13.4% for the one-noise model and 10.2% for the plain
regression. The cost of the joint model when it is not needed is a little
larger than report 08 said.

### 6. Without an instrument, the corrected model is uncertain, not wrong

Linear hidden factor at strength 1, ten datasets:

| Patients | Model | rho, mean (average 95% interval) | Average error | Spread (SD) | Typical distance from the truth | Sent to the worse drug |
|---|---|---|---|---|---|---|
| 5,000 | Plain regression | fixed at 0 | 4.20 | 0.48 | 4.22 | 38.2% |
| 5,000 | Joint, one noise level | 0.01 (−0.18 to 0.20) | 3.97 | 0.53 | 4.01 | 36.7% |
| 5,000 | Joint, noise per drug | 0.12 (−0.40 to 0.50) | 0.68 | 5.45 | 5.22 | 36.8% |
| 20,000 | Plain regression | fixed at 0 | 4.32 | 0.26 | 4.32 | 38.6% |
| 20,000 | Joint, one noise level | 0.00 (−0.09 to 0.10) | 4.23 | 0.15 | 4.23 | 38.1% |
| 20,000 | Joint, noise per drug | 0.09 (−0.27 to 0.39) | 1.97 | 3.45 | 3.82 | 28.6% |

Nothing hidden:

| Patients | Model | Average error | Spread (SD) | Sent to the worse drug |
|---|---|---|---|---|
| 5,000 | Plain regression | −0.05 | 0.54 | 12.4% |
| 5,000 | Joint, noise per drug | 0.50 | 6.29 | 34.4% |
| 20,000 | Plain regression | 0.05 | 0.27 | 5.6% |
| 20,000 | Joint, noise per drug | 1.02 | 3.34 | 23.0% |

- **The one-noise model said "no hidden link" and was sure.** That
  confidence came from the mismatch.
- **The corrected model does not know.** Its interval for the link runs from
  about −0.4 to 0.5. Its answer for the average effect swings from −9 to +10
  mmol/mol between datasets at 5,000 patients.
- **It is worse than the plain regression when nothing is hidden,** by a wide
  margin: 34% sent to the worse drug against 12%.
- **More patients help slowly.** At 20,000 the spread falls from 5.5 to 3.4.
  It is still too wide to use.
- **The conclusion that a joint model needs an instrument stands.** The
  reason is now the right one: without an instrument the data hold almost no
  information about the link.

## What this changes in the earlier reports

No number in an earlier report is changed. Four explanations were wrong or
incomplete. Each of those reports now carries a dated correction.

| Report | What it said | What is now known |
|---|---|---|
| 06 | Without an instrument the joint model's intervals widen and become "far more honest" | The intervals were not honest. The estimate of the link was held near zero by the mismatch. |
| 08 | A quarter of the bias remains because the model "shrinks towards no hidden link" with limited information | The remaining bias came from the mismatch. The corrected model and a two-step method remove it. |
| 10 | One SD of the instrument changes the chance of the GLP-1 drug "by roughly a fifth", so a flaw is magnified "about five times" | The change is 0.15. The textbook magnification is 1/0.15, about 6.5. The two-step method gives errors of 5.66 and 6.31 where the one-noise joint model gave 4.55 and 5.90. The conclusion is unchanged and somewhat stronger. |
| 12 | The reason for the confident wrong answer at 20,000 patients was "a likely reason, not yet tested" | Tested and supported. With the mismatch removed, the model is uncertain instead of confidently wrong. |

Reports 09, 10 and 11 used the one-noise joint model. Their conclusions hold:
the two-step method confirms the practice-level result (an error of −0.20 for
25 practices, against 0.65) and the invalid-instrument result, and report 11
concerns the plain regression only.

## Checks

- **Convergence with an instrument.** In the 70 corrected fits the worst
  R-hat for any patient's effect was 1.007.
- **Convergence without an instrument is not complete.** In 10 of the 40
  corrected fits without an instrument, the R-hat of patients' effects was
  above 1.01 (worst 1.035). The chains mix slowly because the data say so
  little about the link. The averages above are therefore approximate; the
  wide spread between datasets is far larger than this imprecision.
- **Earlier datasets are unchanged.** The new option is off by default.

## Limits

- **The corrected model was not run** at instrument strength 0.5, on the
  practice-level or invalid instruments, or on datasets 10 to 19. For those,
  the one-noise results of reports 08 to 10 stand, with the two-step check
  where it was run.
- **The two-step method is a check, not a second analysis.** It gives an
  average effect only, with no intervals.
- **One mismatch was found and removed. Others remain:** drug choice follows
  a logistic curve where the model assumes a probit one, and the hidden factor
  adds variation that differs between drug groups for the effect form.
- Ten datasets per setting. The limits of reports 08 and 12 apply.
