# Report 12: the joint model without an instrument, with four times as many patients

**Date:** 2026-10-09
**Scripts:** `scripts/12_followup_runs.py --run more_patients` (the run), `scripts/13_summarise_followups.py` (the table)
**Results:** `results/generator-v2/more_patients/EVELYN68961.csv` (40 rows: two models × 20 datasets)
**Table:** `reports/tables/followup_more_patients.csv`
**Code commit recorded in every row:** 47a37bf

## Question

In report 06 the joint model, given no instrument, did not detect the hidden
factor in any of 140 datasets of 5,000 patients. Published treatment selection
models use many more patients. Was 5,000 simply too few?

## What was run

- Datasets of 20,000 patients, with no instrument: hidden factor off, and
  linear at strength 1. Ten datasets each, with the same seeds as report 06.
  A seed gives a different set of patients at a different size, so these are
  new datasets, not the old ones enlarged.
- Plain regression and joint model, fitted as in report 06.
- The rows for 5,000 patients are those of report 06, datasets 0 to 9.

## Result

Averages across ten datasets. Errors in the average effect, in mmol/mol.

### Linear hidden factor at strength 1

| Patients | Model | rho, mean (average 95% interval) | Error in the average effect (SD) | Coverage of 95% intervals | Sent to the worse drug | Link detected |
|---|---|---|---|---|---|---|
| 5,000 | plain | fixed at 0 | 4.20 (0.48) | 10.1% | 38.2% | |
| 20,000 | plain | fixed at 0 | 4.32 (0.26) | 0.0% | 38.6% | |
| 5,000 | joint | 0.01 (−0.18 to 0.20) | 3.97 (0.53) | 83.7% | 36.7% | 0 of 10 |
| 20,000 | joint | 0.00 (−0.09 to 0.10) | 4.23 (0.15) | 0.8% | 38.1% | 0 of 10 |

### Nothing hidden

| Patients | Model | rho, mean (average 95% interval) | Error in the average effect (SD) | Coverage of 95% intervals | Sent to the worse drug |
|---|---|---|---|---|---|
| 5,000 | plain | fixed at 0 | −0.05 (0.54) | 91.8% | 12.4% |
| 20,000 | plain | fixed at 0 | 0.05 (0.27) | 94.3% | 5.6% |
| 5,000 | joint | 0.00 (−0.17 to 0.17) | −0.10 (0.69) | 99.9% | 12.6% |
| 20,000 | joint | 0.00 (−0.09 to 0.08) | 0.13 (0.32) | 99.9% | 5.7% |

## Reading

1. **More patients do not help the joint model find the hidden factor.** With
   20,000 patients its estimate of the link is still zero, in every one of
   ten datasets (the estimates run from −0.004 to 0.012). The error in the
   average effect is 4.23, the same as the plain regression's 4.32.

2. **More patients make it confident in the wrong answer.** The interval for
   rho narrows from (−0.18 to 0.20) to (−0.09 to 0.10). The true value is
   about 0.16, so the interval at 5,000 patients contained the truth and the
   interval at 20,000 does not.

3. **The honest intervals of report 06 came from having few patients.** At
   5,000 patients, 84% of the joint model's intervals for a patient's effect
   contained the truth. At 20,000 it is 0.8%. Report 06 read the wide
   intervals as the model "no longer being confident about a wrong answer".
   That held at that size only. With enough data the model becomes confident
   again, and it is still wrong.

4. **A likely reason, not yet tested.**

   - **The one clue the model has.** Some patients receive a drug against the
     odds: their recorded features made it unlikely, and they got it anyway.
     If a hidden factor exists, it must have pushed those patients hard, so
     their results should be shifted more than the results of patients who
     were always likely to get that drug. Without an instrument, this pattern
     is the only trace of a hidden link that the model can look for.
   - **The clue is faint and easily lost.** It can be read only if the model's
     description of everything else is exactly right. Any small error in that
     description produces a pattern of the same kind, and the two cannot be
     told apart.
   - **The simulated patients differ from the model's description in two
     small ways.** The chance of each drug follows a slightly different curve
     from the one the model assumes (logistic, where the model assumes
     probit). And results vary more on one drug than the other (an SD of 15.4
     against 12.6), where the model assumes one amount of variation.
   - **What points to this reason.** In report 05, the same model was given
     20,000 patients built to match its description exactly, with a strong
     link of 0.6. It found 0.61. And here its interval does not merely fail to
     find the link: it excludes the true value. A model that only lacked
     information would be unsure. This one is sure of a wrong value, which is
     what a wrong description produces.
   - **What would test it.** Patients built to match the model exactly, with
     the weak link of this report (about 0.16), at 20,000 patients. That run
     was not done.

5. **With nothing hidden, more patients help as they should.** Both models
   send about 6% of patients to the worse drug at 20,000 patients, against
   12% at 5,000.

6. **Sample size does not substitute for an instrument.** Reports 08 and 09
   show that an ideal instrument recovers most of the truth at 5,000
   patients. Four times the patients with no instrument recovers none.

## Checks

- **Convergence.** The worst R-hat for any patient's effect in any of the 40
  fits was 1.006.
- **Time.** A fit took five minutes on average, against about two at
  5,000 patients.

## Correction added 2026-10-09

The numbers in this report stand. Reading 4 has now been tested.

[Report 13](13_verification_and_corrected_joint_model.md) confirms the
reason, and narrows it to one of the two mismatches named there: the single
noise level. With a noise level per drug and 20,000 patients, the joint
model without an instrument is no longer confidently wrong. Its estimate of
the link is 0.09 (−0.27 to 0.39) against 0.00 (−0.09 to 0.10) here. Its
average error is 1.97 against 4.23, but its answers vary so much between
datasets (an SD of 3.45) that it is still not usable. Reading 6, that sample
size does not substitute for an instrument, is unchanged.

## Limits

- **One larger size.** 20,000 is still far below the hundreds of thousands in
  published cohorts. The direction of the result, a narrowing interval around
  zero, does not suggest that a larger size would behave differently, but it
  was not run.
- **One hidden-factor setting** (linear, strength 1) besides off.
- **The reason in point 4 is a conjecture.** A check would fit the model to
  patients simulated exactly from it, at 20,000 patients.
- **One simple joint model.** A flexible model of the errors might use the
  shape of the distribution better. It was not built.
- Ten datasets per setting.
