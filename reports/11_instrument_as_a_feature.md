# Report 11: the instrument used as an ordinary feature

**Date:** 2026-10-09
**Scripts:** `scripts/12_followup_runs.py --run as_feature` (the run), `scripts/13_summarise_followups.py` (the table)
**Results:** `results/generator-v2/as_feature/EVELYN68961.csv` (70 rows: one model × 70 datasets)
**Table:** `reports/tables/followup_as_feature.csv`
**Code commit recorded in every row:** 47a37bf

## Question

In report 08 the plain regression does not use the instrument, and the joint
model uses it in the drug-choice equation only. A third option is the most
natural one for someone building a prediction model: the instrument predicts
which drug is prescribed, so add it to the model like any other feature. What
does that do?

## What was run

- The plain regression of report 08, with the instrument added as one more
  feature. It enters the baseline response and the drug effect, like age or
  BMI.
- The 70 datasets of report 08 that have the ideal instrument at strength
  1.0: seven hidden-factor settings, ten datasets each, same seeds.
- The plain regression and the joint model on these datasets are not refitted.
  Their rows are those of report 08.

## Result

Averages across ten datasets. Errors in the average effect, in mmol/mol.

| Hidden factor | Plain, instrument left out | Plain, instrument as a feature | Change | Joint model |
|---|---|---|---|---|
| Off | 0.15 | 0.16 | +0.01 | 0.08 |
| Linear, 0.5 | 1.06 | 1.23 | +16% | 0.26 |
| Linear, 1 | 3.77 | 4.26 | +13% | 0.95 |
| Threshold, 0.5 | 0.79 | 0.90 | +13% | 0.33 |
| Threshold, 1 | 2.91 | 3.30 | +13% | 1.06 |
| Effect, 0.5 | 0.78 | 0.92 | +17% | 0.45 |
| Effect, 1 | 2.65 | 3.00 | +14% | 1.58 |

Share of patients sent to the worse drug, hidden factor at strength 1:

| Hidden factor | Plain, instrument left out | Plain, instrument as a feature | Joint model |
|---|---|---|---|
| Linear, 1 | 34.8% | 37.6% | 16.5% |
| Threshold, 1 | 28.2% | 30.8% | 16.4% |
| Effect, 1 | 26.0% | 28.4% | 18.7% |

## Reading

1. **Adding the instrument as a feature makes the bias larger.** In every
   setting with a hidden factor the error grows by 13% to 17%, and more
   patients are sent to the worse drug.

2. **With nothing hidden it does no harm.** The error is 0.16 against 0.15.

3. **Why.** Among patients with the same value of the instrument, the choice
   of drug is explained by fewer other things, so the hidden factor accounts
   for a larger share of who gets which drug. Adjusting for the instrument
   removes harmless variation in drug choice and leaves the harmful part.
   This is known in the literature as bias amplification.

4. **The same variable helps or harms depending on how it is used.** Placed
   in the drug-choice equation of a joint model and kept out of the outcome
   equation, the instrument removes 40% to 75% of the error (report 08).
   Placed in an outcome regression as a predictor, it adds 13% to 17%.

5. **A practical consequence.** A feature that predicts prescribing and not
   the outcome looks like a useful adjustment variable, and standard
   variable-selection for the propensity of treatment would favour it. Under
   a hidden factor it should be left out of an outcome model, or used as an
   instrument.

## Checks

- **Convergence.** The worst R-hat for any patient's effect in any of the 70
  fits was 1.010.
- **Same datasets.** The comparison rows are those of report 08 for
  instrument strength 1.0 and datasets 0 to 9.

## Limits

- **One model.** The effect was measured for the plain regression. The causal
  forest was not refitted with the instrument as a feature; the mechanism does
  not depend on the model, but the size might.
- **One instrument strength (1.0).** A stronger instrument would amplify the
  bias more.
- **An ideal instrument.** The flawed instruments of report 10 were not used
  here.
- Ten datasets per setting. The limits of report 08 apply.
