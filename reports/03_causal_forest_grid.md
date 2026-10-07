# Report 03: the causal forest with the hidden factor switched on

**Date:** 2026-10-07
**Scripts:** `scripts/03_causal_forest_grid.py` (the fits), `scripts/05_summarise_grid.py` (table and figure)
**Generator:** version 2 (see `docs/calibration.md`)
**Results:** `results/generator-v2/EVELYN68961.csv` (119 fits) and `results/generator-v2/EVELYN68961PC.csv` (21 fits)
**Table:** `reports/tables/step2_causal_forest.csv`

## Question

How wrong does a Bayesian causal forest get as a hidden factor that drives
both drug choice and outcome gets stronger, and does the form of its effect
on the outcome matter?

## What was run

- 140 simulated datasets of 5,000 patients each: 20 with the hidden factor
  off, and 20 for each of three shapes (`linear`, `threshold`, `effect`) at
  each of two strengths (0.5 and 1).
- Repeat *r* uses seed *r* in every setting.
- Each dataset was fitted with a Bayesian causal forest (`stochtree`, default
  priors, propensity score estimated by the package): four chains, 500 warm-up
  draws and 2,000 kept draws each.
- The forest is never shown the hidden factor.
- The fits were shared between two computers. Report 04 shows that the two
  computers produce identical results for the same dataset.

What the strengths mean, per SD of the hidden factor:

| Strength | Odds of the GLP-1 drug | Outcome | Compared with recorded features |
|---|---|---|---|
| 0.5 | × 1.65 | 2.5 mmol/mol worse | As strong on drug choice as BMI; a third as strong on the outcome as starting HbA1c |
| 1 | × 2.72 | 5 mmol/mol worse | Twice as strong on drug choice as BMI; about 60% as strong on the outcome as starting HbA1c |

## Result

Averages across 20 datasets per setting. SD is the spread between datasets.
All errors are in mmol/mol of HbA1c.

| Hidden factor | Crude error | Forest: error in the average effect (SD) | Typical error per patient (SD) | 95% intervals containing the truth | Patients sent to the worse drug (SD) | HbA1c lowering lost per patient |
|---|---|---|---|---|---|---|
| Off | 0.30 | 0.12 (0.60) | 1.82 (0.25) | 94.3% | 16.5% (2.6%) | 0.19 |
| Linear, 0.5 | 1.53 | 1.39 (0.60) | 2.21 (0.48) | 87.3% | 21.2% (5.7%) | 0.30 |
| Linear, 1 | 4.40 | 4.44 (0.48) | 4.80 (0.47) | 27.6% | 43.2% (4.5%) | 1.03 |
| Threshold, 0.5 | 1.22 | 1.06 (0.62) | 2.03 (0.45) | 90.5% | 19.2% (5.3%) | 0.25 |
| Threshold, 1 | 3.49 | 3.52 (0.50) | 3.97 (0.48) | 45.7% | 37.2% (5.5%) | 0.79 |
| Effect, 0.5 | 1.23 | 1.06 (0.59) | 2.05 (0.42) | 90.1% | 19.3% (4.7%) | 0.25 |
| Effect, 1 | 3.25 | 3.18 (0.45) | 3.70 (0.42) | 49.8% | 34.2% (5.2%) | 0.68 |

"Crude error" is the error of comparing the two drug groups directly, with no
adjustment. True effects vary between patients with an SD of 3.3, and the true
average effect is close to zero.

![Figure](figures/step2_causal_forest.png)

## Reading

1. **With nothing hidden, the forest is honest but imprecise.** Its average
   effect has no systematic lean: the mean error is 0.12 with a standard error
   of 0.13 across 20 datasets. Its 95% intervals contain the truth 94.3% of
   the time. But at 5,000 patients it still sends one patient in six to the
   worse drug. Those are mostly patients for whom the two drugs are close: the
   loss is 0.19 mmol/mol per patient.

2. **The forest removes confounding it can see and none that it cannot.** With
   the hidden factor off, it cuts the crude error from 0.30 to 0.12. With the
   hidden factor on, its error in the average effect is the same as the crude
   comparison's to within about 0.2 mmol/mol at every setting (for example
   4.44 against 4.40).

3. **A moderate hidden factor does modest damage.** At strength 0.5, the share
   sent to the worse drug rises from 16.5% to between 19% and 21%, and interval
   coverage falls from 94% to between 87% and 91%.

4. **A strong one breaks the model.** At strength 1, between 34% and 43% of
   patients are sent to the worse drug, and the loss per patient rises from
   0.19 to between 0.68 and 1.03 mmol/mol. Random allocation would send 50%.

5. **The intervals fail before the point estimates look wrong.** At strength 1
   only 28% to 50% of the 95% intervals contain the truth. The model reports
   the same confidence while being far less often right. Nothing in its output
   signals the problem.

6. **The form matters, at the same strength.** `linear` and `threshold` add
   the same variance to the outcome, yet `linear` does more harm (43% against
   37% sent to the worse drug at strength 1). The ordering linear, threshold,
   effect is the same as the ordering of the crude error.

7. **The damage grows faster than the strength.** Going from 0.5 to 1 roughly
   triples the error in the average effect, because strength scales both of
   the hidden factor's links.

## Checks

- **Convergence.** R-hat for the average effect never exceeded 1.002. For
  individual patients, 59% of fits had at least one patient above 1.01, but on
  average under 1% of patients in a fit were above it (worst fit: 7.9% of
  patients; worst single R-hat: 1.042). The conclusions above rest on averages
  over patients and are not sensitive to this.
- **One dataset stands out.** Repeat 16 gives high errors at every setting,
  including with the hidden factor off (error in the average effect 1.13).
  That is a chance imbalance in one simulated dataset, present before any
  hidden factor is added. It is kept in the averages.
- **Same code throughout.** The rows record four commits (f63f4b3, c1bb600,
  b468ead, bf0b09f). They differ only in result files, documentation and
  scripts 04 and 05. The generator, the forest and the scoring are unchanged
  across them.

## Limits

- **It is a simulation.** The sizes depend on how the patients were built. The
  patients match printed summary figures from one paper; several slopes were
  chosen (see `docs/calibration.md`).
- **5,000 patients per dataset.** The published model was built on about
  27,000. A larger dataset would make the forest more precise when nothing is
  hidden. It would not reduce the bias from a hidden factor.
- **One dial moves both links,** and the direction is fixed: the hidden factor
  always favours the GLP-1 drug and always worsens the result.
- **The hidden factor is unrelated to every recorded feature.** In real
  records part of it would be visible through them. This is the hardest case.
- **Under the `effect` shape the scoring target is a choice.** Estimates are
  scored against the effect across all patients with the same recorded
  features. Brooks et al. (*BMC Med Res Methodol* 2024;24:66) found that a
  generalized random forest recovers the effect among treated patients under
  this kind of selection. Whether that explains the error seen here was not
  tested.
- **Three shapes, two strengths.** Other forms, such as a hidden factor that
  interacts with a recorded feature, were not tried.
- **Scored in-sample.** Each forest is scored on the patients it was fitted
  to, against a truth it never sees.

## Run time

119 fits on the lead computer took a median of 13 minutes each with four
running side by side. 21 fits on the second computer took a median of 59
minutes each with three side by side; its last fit, running alone, took 29
minutes. Total fitting time across both computers was about 46 hours.

## Next

Step 3: fit a joint model of drug choice and outcome to the same datasets, and
ask whether it does better than the forest when the hidden factor is on.
