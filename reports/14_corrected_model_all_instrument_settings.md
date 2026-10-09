# Report 14: the corrected joint model on every instrument setting

**Date:** 2026-10-09
**Scripts:** `scripts/12_followup_runs.py --run per_drug_noise` (the run, second part), `scripts/13_summarise_followups.py` (the table)
**Results:** `results/generator-v2/per_drug_noise/EVELYN68961.csv`, the 220 rows with code commit f361672
**Table:** `reports/tables/followup_per_drug_noise_instruments.csv`

## Question

Report 13 corrected the joint model by giving it a noise level per drug, and
fitted it on one instrument setting. Reports 08 to 10 used the first joint
model on several others. Do their conclusions hold with the corrected model?

## What was run

The corrected joint model on every instrument setting of reports 08 to 10,
with the same datasets:

- the ideal instrument at strength 1.0, datasets 10 to 19 (report 09);
- the ideal instrument at strength 0.5, datasets 0 to 9 (report 08);
- the practice-level instruments with 100 and 25 practices (report 10);
- the invalid instruments with a direct effect of 0.5 and 1.0 mmol/mol
  (report 10).

The plain regression and the first joint model are not refitted. Their rows
are those of the earlier reports.

## Result

Errors in the average effect, mmol/mol. Hidden factor at strength 1 unless
"off".

### Ideal instrument, strength 1.0, all twenty datasets

| Hidden factor | Plain | Joint, one noise level | Joint, noise per drug | Error removed | Sent to the worse drug, plain → corrected | Link detected |
|---|---|---|---|---|---|---|
| Linear | 3.72 | 1.00 | −0.01 | all | 34.7% → 18.2% | 14 of 20 |
| Threshold | 2.83 | 0.97 | 0.12 | 96% | 28.0% → 18.4% | 11 of 20 |
| Effect | 2.60 | 1.57 | 1.20 | 54% | 26.0% → 20.2% | 4 of 20 |
| Off | 0.13 | 0.14 | 0.12 | none to remove | 9.7% → 16.3% | 3 of 20 |

The two halves agree: for the linear form the corrected model's error is
−0.08 on datasets 0 to 9 and 0.06 on datasets 10 to 19; for threshold 0.22
and 0.01; for effect 1.21 and 1.19.

### Ideal instrument, strength 0.5, ten datasets

| Hidden factor | Plain | Joint, one noise level | Joint, noise per drug | Spread of the corrected model (SD) | Sent to the worse drug, plain → corrected |
|---|---|---|---|---|---|
| Linear | 4.10 | 2.28 | 0.24 | 3.08 | 36.5% → 26.2% |
| Threshold | 3.25 | 2.29 | 0.97 | 3.15 | 30.5% → 25.3% |
| Effect | 2.91 | 2.45 | 1.87 | 3.21 | 27.8% → 26.2% |
| Off | 0.01 | 0.09 | 0.20 | 2.65 | 11.5% → 23.0% |

### Practice-level instruments, ten datasets

| Instrument | Hidden factor | Plain | Joint, one noise level | Joint, noise per drug | Sent to the worse drug, plain → corrected |
|---|---|---|---|---|---|
| 100 practices | Linear | 3.90 | 0.82 | −0.39 | 36.3% → 16.2% |
| 100 practices | Off | −0.07 | −0.07 | −0.04 | 10.8% → 15.3% |
| 25 practices | Linear | 3.77 | 0.65 | −0.38 | 34.4% → 16.9% |
| 25 practices | Off | −0.01 | −0.22 | −0.24 | 11.8% → 18.9% |

### Invalid instruments, ten datasets

| Direct effect on the outcome | Hidden factor | Plain | Joint, one noise level | Joint, noise per drug | Two-step check | Sent to the worse drug, plain → corrected |
|---|---|---|---|---|---|---|
| 0.5 mmol/mol | Linear | 4.14 | 3.40 | 3.13 | 3.19 | 37.1% → 28.8% |
| 0.5 mmol/mol | Off | 0.57 | 2.32 | 3.02 | | 11.4% → 28.9% |
| 1.0 mmol/mol | Linear | 4.51 | 5.90 | 6.41 | 6.31 | 39.4% → 44.8% |
| 1.0 mmol/mol | Off | 0.99 | 4.55 | 5.98 | 5.66 | 13.6% → 44.8% |

With nothing hidden, the corrected model reported a link in 5 of 10 datasets
at 0.5 mmol/mol and in 10 of 10 at 1.0 mmol/mol.

## Reading

1. **The corrected result holds on twenty datasets.** With a valid instrument
   of strength 1.0 the joint model removes all of the error for the linear
   form, 96% for threshold and 54% for effect. The two halves of the datasets
   agree closely.

2. **The effect form stays hard.** About half the error remains in both
   halves and with the two-step method of report 13. This form changes the
   drug's effect from patient to patient, which a single link cannot describe.

3. **A weaker instrument removes the bias and costs a great deal of
   precision.** At strength 0.5 the corrected model's average error for the
   linear form is 0.24, but its answers vary between datasets with an SD of
   3.1, twice that at strength 1.0. With nothing hidden it sends 23% of
   patients to the worse drug, against 11.5% for the plain regression. Under a
   strong hidden factor it still does better than the plain regression (26%
   against 36%).

4. **The first joint model looked better at strength 0.5 than it was.** Its
   answers were less variable because its estimate of the link was held near
   zero (report 13). That stability was bought with a bias of 2.28.

5. **A practice-level instrument works as well as an ideal one.** With 100 or
   25 practices the corrected model's error is about −0.4, and it sends about
   16% of patients to the worse drug, as with the ideal instrument. Report 10's
   conclusion holds.

6. **An invalid instrument is worse than report 10 said.** With a direct
   effect of 1.0 mmol/mol and nothing hidden, the corrected model's error is
   5.98, against 4.55 for the first joint model, and it sends 45% of patients
   to the worse drug, close to tossing a coin. The two-step method agrees
   (5.66). The first joint model understated the damage for the same reason it
   understated the benefit: its link was held near zero.

7. **The joint model is a trade.** It removes bias and adds variability. It
   pays when the hidden factor is strong and the instrument is strong and
   valid. It costs when nothing is hidden, when the instrument is weak, and
   most of all when the instrument is invalid.

## Checks

- **Convergence.** The worst R-hat for any patient's effect in the 220 fits
  was 1.008.
- **No duplicates.** 330 rows in the file, one per dataset and setting.
- **Report 13's table is unchanged.** It is still built from the first part of
  the run only.
- **Independent method.** The two-step check of report 13 was run for the
  invalid instruments and for 25 practices (−0.20 against −0.38 here), and
  agrees.

## Limits

- **The two-step check was not run** for instrument strength 0.5 or for 100
  practices.
- **The corrected model still assumes** a probit curve for drug choice and
  straight-line effects. The patients follow a logistic curve.
- Ten datasets per setting except where twenty are stated. With an SD of 3
  between datasets, the averages at instrument strength 0.5 have a standard
  error of about 1.
- The limits of reports 08, 10 and 13 apply.
