# Report 02: what the hidden factor does to the data

**Date:** 2026-10-07
**Script:** `scripts/02_what_the_hidden_factor_does.py`
**Generator:** calibrated version (see `docs/calibration.md`). An earlier
version of this report used the first, hand-picked generator; the pattern was
the same and the numbers slightly different.

## Question

Before fitting any model to confounded data, what does each setting of the
hidden factor do? How uneven do the drug groups become, how much of the
outcome does the hidden factor explain, and how wrong is the crudest method?

## The two settings

The hidden factor is one number per patient, standard normal, unrelated to
every recorded feature. A higher value makes the GLP-1 drug more likely.

**Strength** scales both of its links at once:

| Strength | Odds of the GLP-1 drug, per SD | Outcome, per SD |
|---|---|---|
| 0 | no influence | no influence |
| 0.5 | × 1.65 | 2.5 mmol/mol worse |
| 1 | × 2.72 | 5 mmol/mol worse |

For comparison with recorded features: BMI shifts the log-odds of drug choice
by 0.51 per SD, and starting HbA1c shifts the outcome by 8.5 mmol/mol per SD.
Strength 0.5 is "as strong on drug choice as BMI, and a third as strong on the
outcome as starting HbA1c". Strength 1 is "twice as strong on drug choice as
BMI, and about 60% as strong on the outcome as starting HbA1c".

**Shape** is the form of its link to the outcome:

| Shape | Link to the outcome |
|---|---|
| `linear` | Each SD worsens the result by the same amount, on either drug. |
| `threshold` | Only patients more than 1 SD above average (16%) are affected. Scaled to add the same variance as `linear`. |
| `effect` | It changes how well the GLP-1 drug works and does nothing on the SGLT2 drug. |

## What was run

400,000 simulated patients per setting, seed 7. No model is fitted. The crude
comparison is the mean outcome in the GLP-1 group minus the mean outcome in
the SGLT2 group. Its error at strength 0, which comes from recorded features,
is subtracted so that the last column shows the hidden factor alone.

## Result

| Shape | Strength | GLP-1 group in the top 16% of the hidden factor | SGLT2 group in the top 16% | Outcome variance from the hidden factor | Extra error of the crude comparison |
|---|---|---|---|---|---|
| linear | 0 | 16% | 16% | 0.0% | 0.00 mmol/mol |
| linear | 0.5 | 25% | 13% | 2.6% | 1.19 mmol/mol |
| linear | 1 | 32% | 9% | 9.8% | 4.11 mmol/mol |
| threshold | 0 | 16% | 16% | 0.0% | 0.00 mmol/mol |
| threshold | 0.5 | 25% | 13% | 2.6% | 0.89 mmol/mol |
| threshold | 1 | 32% | 9% | 9.7% | 3.22 mmol/mol |
| effect | 0 | 16% | 16% | 0.0% | 0.00 mmol/mol |
| effect | 0.5 | 25% | 13% | 0.6% | 0.90 mmol/mol |
| effect | 1 | 32% | 9% | 2.8% | 2.98 mmol/mol |

## Reading

- **A small share of the outcome, a large error.** At strength 1 the hidden
  factor explains under 10% of the variation in the outcome, yet it shifts the
  crude comparison by about 4 mmol/mol. The true average effect is close to
  zero and true effects vary with an SD of 3.1.
- **The error grows faster than the strength.** Doubling the strength more
  than triples the error, because strength scales both links.
- **Same variance, different error.** `linear` and `threshold` add the same
  variance to the outcome, yet the crude comparison is less wrong under
  `threshold`. The form of the confounding matters, not only its size.
- **`effect` is a different kind of problem.** The drug works less well in the
  patients who were selected for it, so the effect among treated patients
  differs from the effect across all patients. This is called essential
  heterogeneity. Brooks et al. (*BMC Med Res Methodol* 2024;24:66) found that
  under it a generalized random forest recovered true effects only for treated
  patients. They did not test Bayesian causal forests.

## Limits

- These errors are for a crude comparison of the two groups, not for the
  causal forest. They show the size of the problem, not how a model copes.
- One dial moves both links. The two could be varied separately.
- The direction is fixed: the hidden factor always pushes towards the GLP-1
  drug and always worsens the result.
- The hidden factor is unrelated to recorded features. In real records, part
  of it would be visible through them.

## Next

Fit the causal forest at each of these settings and compare its error with
the crude error above.
