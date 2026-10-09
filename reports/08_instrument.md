# Report 08: the joint model with an instrument

**Date:** 2026-10-08
**Scripts:** `scripts/10_instrument_grid.py` (the run), `scripts/11_summarise_step3.py` (table and figure)
**Results:** `results/generator-v2/instrument/EVELYN68961.csv` (280 rows: two models × 140 datasets)
**Table:** `reports/tables/step3_instrument.csv`
**Code commit recorded in every row:** 925d113

## Question

Without an instrument the joint model could not detect a hidden factor
(report 06). The approach it belongs to relies on one: a variable that moves
the choice of drug and affects the outcome in no other way (Conley et al.,
*J Econometrics* 2008). If the simulated patients are given an instrument,
does the joint model correct the bias, and what does it cost?

## What was run

- The generator gained an optional instrument: a standard normal variable
  that enters the drug-choice formula and nothing else. It has its own random
  stream, so datasets without an instrument are unchanged (the dataset
  fingerprints of report 04 are identical before and after).
- **Instrument strength** is the shift in the log-odds of the GLP-1 drug per
  SD of the instrument: 0.5 (about as strong on drug choice as BMI) and 1.0
  (twice that).
- The seven hidden-factor settings of step 2, at both instrument strengths,
  ten datasets each: 140 datasets of 5,000 patients.
- Two models per dataset:
  - **plain:** an outcome regression in which the drug effect varies with the
    features. It assumes nothing is hidden and does not use the instrument.
  - **joint:** the same, plus a probit model of drug choice that includes the
    instrument, with jointly normal errors of correlation rho. The instrument
    is excluded from the outcome part.
- Scoring as before. The validation check of report 07 was also applied to
  both models.

## Result

Averages across ten datasets per setting. Errors in mmol/mol.

### Instrument strength 1.0

| Hidden factor | Model | rho, mean (average 95% interval) | Error in the average effect (SD) | Typical error per patient | 95% intervals containing the truth | Sent to the worse drug | HbA1c lost per patient |
|---|---|---|---|---|---|---|---|
| Off | plain | fixed at 0 | 0.15 (0.71) | 1.14 | 94.0% | 10.2% | 0.08 |
| Off | joint | 0.00 (−0.09 to 0.09) | 0.08 (1.26) | 1.45 | 93.9% | 13.4% | 0.12 |
| Linear, 0.5 | plain | fixed at 0 | 1.06 (0.68) | 1.69 | 81.1% | 14.8% | 0.16 |
| Linear, 0.5 | joint | 0.04 (−0.05 to 0.13) | 0.26 (1.25) | 1.67 | 91.9% | 15.2% | 0.16 |
| Linear, 1 | plain | fixed at 0 | 3.77 (0.55) | 3.91 | 13.6% | 34.8% | 0.64 |
| Linear, 1 | joint | 0.13 (0.03 to 0.23) | 0.95 (1.32) | 1.78 | 91.9% | 16.5% | 0.18 |
| Threshold, 0.5 | plain | fixed at 0 | 0.79 (0.66) | 1.57 | 85.1% | 13.6% | 0.14 |
| Threshold, 0.5 | joint | 0.02 (−0.07 to 0.12) | 0.33 (1.18) | 1.66 | 92.5% | 15.0% | 0.16 |
| Threshold, 1 | plain | fixed at 0 | 2.91 (0.55) | 3.12 | 33.9% | 28.2% | 0.44 |
| Threshold, 1 | joint | 0.09 (−0.01 to 0.18) | 1.06 (1.22) | 1.82 | 91.5% | 16.4% | 0.18 |
| Effect, 0.5 | plain | fixed at 0 | 0.78 (0.68) | 1.54 | 85.1% | 13.5% | 0.14 |
| Effect, 0.5 | joint | 0.02 (−0.07 to 0.11) | 0.45 (1.23) | 1.67 | 91.0% | 15.0% | 0.16 |
| Effect, 1 | plain | fixed at 0 | 2.65 (0.53) | 2.86 | 37.6% | 26.0% | 0.38 |
| Effect, 1 | joint | 0.05 (−0.04 to 0.15) | 1.58 (1.22) | 2.06 | 82.6% | 18.7% | 0.24 |

### Instrument strength 0.5

| Hidden factor | Model | rho, mean (average 95% interval) | Error in the average effect (SD) | Typical error per patient | 95% intervals containing the truth | Sent to the worse drug | HbA1c lost per patient |
|---|---|---|---|---|---|---|---|
| Off | plain | fixed at 0 | 0.01 (0.69) | 1.38 | 90.5% | 11.5% | 0.09 |
| Off | joint | 0.00 (−0.13 to 0.12) | 0.09 (1.43) | 1.74 | 95.3% | 15.2% | 0.16 |
| Linear, 0.5 | plain | fixed at 0 | 1.15 (0.65) | 1.65 | 81.6% | 14.5% | 0.15 |
| Linear, 0.5 | joint | 0.02 (−0.11 to 0.15) | 0.73 (1.49) | 1.81 | 94.9% | 16.3% | 0.19 |
| Linear, 1 | plain | fixed at 0 | 4.10 (0.38) | 4.26 | 10.8% | 36.5% | 0.70 |
| Linear, 1 | joint | 0.08 (−0.06 to 0.22) | 2.28 (1.55) | 2.68 | 83.9% | 23.7% | 0.38 |
| Threshold, 0.5 | plain | fixed at 0 | 0.82 (0.66) | 1.48 | 86.9% | 12.7% | 0.12 |
| Threshold, 0.5 | joint | 0.01 (−0.12 to 0.13) | 0.68 (1.43) | 1.76 | 94.8% | 15.4% | 0.18 |
| Threshold, 1 | plain | fixed at 0 | 3.25 (0.36) | 3.49 | 27.0% | 30.5% | 0.51 |
| Threshold, 1 | joint | 0.04 (−0.10 to 0.17) | 2.29 (1.33) | 2.72 | 84.2% | 23.6% | 0.36 |
| Effect, 0.5 | plain | fixed at 0 | 0.85 (0.65) | 1.49 | 86.9% | 12.9% | 0.13 |
| Effect, 0.5 | joint | 0.00 (−0.13 to 0.13) | 0.82 (1.37) | 1.75 | 94.3% | 15.7% | 0.19 |
| Effect, 1 | plain | fixed at 0 | 2.91 (0.36) | 3.19 | 32.3% | 27.8% | 0.44 |
| Effect, 1 | joint | 0.02 (−0.11 to 0.15) | 2.45 (1.24) | 2.84 | 79.9% | 24.4% | 0.39 |

How often the joint model's 95% interval for rho excluded zero:

| Hidden factor | Instrument 0.5 | Instrument 1.0 |
|---|---|---|
| Off | 0 of 10 | 0 of 10 |
| Linear, 0.5 | 0 of 10 | 1 of 10 |
| Linear, 1 | 2 of 10 | 7 of 10 |
| Threshold, 1 | 0 of 10 | 4 of 10 |
| Effect, 1 | 0 of 10 | 3 of 10 |

![Figure](figures/step3_instrument.png)

## Reading

1. **With a strong instrument, the joint model corrects most of the bias.** At
   instrument strength 1.0 and a linear hidden factor of strength 1, the error
   in the average effect falls from 3.77 to 0.95, the share sent to the worse
   drug from 34.8% to 16.5%, and the HbA1c lost per patient from 0.64 to 0.18.
   Interval coverage rises from 13.6% to 91.9%.

2. **A weaker instrument corrects less.** At instrument strength 0.5 the same
   error falls only from 4.10 to 2.28, and the share sent to the worse drug
   from 36.5% to 23.7%. The model then detects the link in 2 of 10 datasets,
   against 7 of 10 with the stronger instrument.

3. **The correction is partial even at its best.** Rho is estimated at 0.13
   where the true value is about 0.16, and about a quarter of the bias
   remains. With limited information the model shrinks towards "no hidden
   link", as Conley et al. describe.

4. **The form of the hidden factor matters to the correction.** At instrument
   strength 1.0 and hidden-factor strength 1, the joint model removes 75% of
   the plain model's error for the linear shape, 64% for the threshold shape
   and 40% for the effect shape. The linear shape is the one that matches the
   model's assumption of jointly normal errors. The effect shape, where the
   hidden factor changes how well one drug works, is outside what this model
   can represent.

5. **The joint model is noisier, and that costs something when nothing is
   hidden.** The spread of its error in the average effect across datasets is
   about twice the plain model's (SD 1.2 to 1.5 against 0.4 to 0.7). With the
   hidden factor off it sends 13.4% of patients to the worse drug against the
   plain model's 10.2%, and with a moderate hidden factor (strength 0.5) the
   two are about level. It pays off only when the hidden factor is strong.

6. **Its intervals are honest throughout.** Coverage is 80% to 95% in every
   setting, against 11% to 38% for the plain model at strength 1.

7. **The validation check penalises the better model.** For the joint model
   at instrument strength 1.0 and a linear hidden factor of strength 1, the
   check's observed benefit (4.39) is well above the model's predicted benefit
   (3.02), while the true benefit is 2.07. For the plain model on the same
   datasets, predicted (4.39) and observed (4.30) agree, while the true
   benefit is 1.01. This repeats the pattern of report 07 with a model that is
   partly, not perfectly, right.

## Checks

- **Convergence.** The worst R-hat for any patient's effect in any fit was
  1.009.
- **The instrument does what an instrument should.** On a test dataset its
  correlation with the drug received was 0.32 and with the outcome −0.01.
- **Existing datasets are unchanged.** The 14 fingerprints of report 04 are
  identical after the generator change.
- **No duplicates and one code commit** across the 280 rows.

## Correction added 2026-10-09

The numbers in this report stand. Reading 3 does not.

Reading 3 says a quarter of the bias remains because the model shrinks
towards "no hidden link" when information is limited.
[Report 13](13_verification_and_corrected_joint_model.md) shows the remaining
bias came from a mismatch: the joint model assumes one noise level for both
drugs and the simulated patients have two. With a noise level per drug, the
same model on the same datasets removes all of the error for the linear form
(an error of −0.08 against 0.95 here), 92% for threshold and 54% for effect.
A classical two-step method agrees. The order of the three forms is unchanged.

## Limits

- **Ten datasets per setting,** half as many as in steps 2 and 3. The standard
  error of an average error in the average effect is about 0.4 for the joint
  model.
- **The causal forest was not run on these datasets** (about eight hours of
  computing). The comparison is plain regression against joint model.
- **The instrument is ideal.** It is exactly unrelated to the outcome and to
  the hidden factor, and its effect on drug choice is known to be of the right
  form. A real instrument, such as a practice's prescribing habit, has to be
  argued for and may be weaker or imperfect.
- **One simple joint model:** normal errors, a probit choice model, straight
  lines, one noise level. Conley et al. replace the normal errors with a
  Dirichlet process mixture. Flexible models of that kind were not
  implemented here, so nothing
  here shows what they would achieve under the threshold or effect shapes.
- **Both models are given the right form for the effects** (straight lines),
  which a model would not know in practice.
- The limits of report 03 apply: a simulation, 5,000 patients per dataset, a
  hidden factor unrelated to every recorded feature.
