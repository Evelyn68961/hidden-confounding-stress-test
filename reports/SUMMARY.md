# What this project found, in plain words

A summary of reports 01 to 14. Each finding points to the report that holds
the numbers, the checks and the limits. First written 2026-10-08. Rewritten
2026-10-12 so that every joint-model number is from the corrected model
(reports 13 and 14) and the terms match the README: bias, RMSE, coverage and
misclassification rate.

The results are preliminary. They rest on 10 or 20 simulated datasets per
setting, and a uniform rerun with 20 datasets for every setting is in
progress.

## The question

Treatment selection models learn from health records which drug works best
for which patient. Doctors choose drugs for reasons that are not always
recorded. When such a reason also affects the outcome, the estimated drug
effect is confounded.

In real records this cannot be checked, because each patient takes one drug.
In a simulation each patient's true drug effect is known. So this project
asks, for simulated people with type 2 diabetes starting an SGLT2 inhibitor or
a GLP-1 receptor agonist:

1. How large is the bias as a hidden factor gets stronger, and does the shape
   of the hidden factor matter?
2. Can a joint model of drug choice and outcome remove the bias, and what
   does it need?

## The setup

- **Patients.** Simulated, 5,000 per dataset, tuned to the summary figures
  printed in Cardoso et al., *Diabetologia* 2024. No patient data were used
  ([calibration](../docs/calibration.md)).
- **The hidden factor.** A standard normal value per patient that makes the
  GLP-1 drug more likely and the outcome worse. It has a **strength** (0.5
  moves drug choice about as much as BMI does; 1 is a severe setting) and a
  **shape** (`linear`, `threshold`, or `effect`, where the effect of the GLP-1
  drug weakens) ([report 02](02_what_the_hidden_factor_does.md)).
- **Models.** A Bayesian causal forest; a plain regression in which the drug
  effect varies with patient features; and a joint model that adds a probit
  equation for drug choice and estimates ρ, the correlation between the error
  in the outcome and the error in drug choice.
- **The instrument.** A variable that shifts drug choice, is independent of
  the hidden factor, and affects the outcome only through drug choice.
- **Scoring.** Against the known truth: the bias and the RMSE of the average
  drug effect, in mmol/mol; the coverage of the 95% intervals for each
  patient's effect; and the misclassification rate, which is the share of
  patients for whom the model picks the worse drug.

## What was found

### 1. With no hidden factor, the causal forest's bias is small

Its bias is 0.12 mmol/mol and the coverage of its 95% intervals is 94.3%. Its
misclassification rate is 16.5% at 5,000 patients
([report 03](03_causal_forest_grid.md)).

### 2. A causal forest does not remove the bias from a hidden factor

At strength 1 the forest's bias matched the unadjusted bias: 4.44 against 4.40
for the linear shape, 3.52 against 3.49 for threshold, and 3.18 against 3.25
for effect. At strength 0.5 the misclassification rate rose from 16.5% to
between 19.2% and 21.2%. At strength 1 it rose to between 34.2% and 43.2%
([report 03](03_causal_forest_grid.md)).

### 3. The coverage of its intervals falls

Coverage was 94.3% with no hidden factor, 87.3% to 90.5% at strength 0.5, and
27.6% to 49.8% at strength 1 ([report 03](03_causal_forest_grid.md)).

### 4. The shape of the hidden factor matters

At strength 1, the linear shape gave the largest bias and the effect shape the
smallest, for the causal forest and for the plain regression.

### 5. A joint model with a valid instrument removes the bias for two shapes

With an ideal instrument and a hidden factor of strength 1, over 20 datasets:

| Shape | Bias, plain regression | Bias, joint model |
|---|---|---|
| Linear | 3.72 | −0.01 |
| Threshold | 2.83 | 0.12 |
| Effect | 2.60 | 1.20 |

The joint model also lowered the RMSE and the misclassification rate for all
three shapes. A classical two-step method agrees with it to within 0.15
mmol/mol on the first ten datasets
([report 13](13_verification_and_corrected_joint_model.md),
[report 14](14_corrected_model_all_instrument_settings.md)).

### 6. With a weaker hidden factor the joint model does not lower the RMSE

At strength 0.5 the joint model still removed the bias (0.05, 0.15 and 0.40
for the three shapes, against 1.07, 0.79 and 0.77 for the plain regression).
Its RMSE was higher than the plain regression's (1.57 to 1.61 against 0.92 to
1.18), and so was its misclassification rate (16.5% to 16.6% against 12.9% to
14.4%).

### 7. With no hidden factor the joint model has the higher misclassification rate

With an ideal instrument and no hidden factor, the bias was 0.12 for the joint
model and 0.13 for the plain regression. The joint model's RMSE was 1.55
against 0.54, and its misclassification rate 16.3% against 9.7%
([report 14](14_corrected_model_all_instrument_settings.md)).

### 8. Without an instrument the joint model does not clearly lower the RMSE

Linear hidden factor at strength 1, 10 datasets. At 5,000 patients the joint
model's RMSE was 5.22 against 4.22 for the plain regression, and at 20,000
patients 3.82 against 4.32. Its estimate of ρ was imprecise (95% interval
−0.40 to 0.50 with 5,000 patients). In a quarter of these fits the largest
R-hat was above 1.01 (maximum 1.03)
([report 13](13_verification_and_corrected_joint_model.md)).

### 9. A practice-level instrument works; a weaker one is imprecise

An instrument with one value per practice (100 or 25 practices) removed the
bias as the ideal one did (−0.39 and −0.38). With a weaker instrument the
joint model's bias was 0.23, with a Monte Carlo standard error of 0.97. With
no hidden factor the weaker instrument gave a misclassification rate of 23.0%,
against 11.5% for the plain regression
([report 14](14_corrected_model_all_instrument_settings.md)).

### 10. An instrument with a direct effect on the outcome leaves the model biased

With a direct effect of 0.5 mmol/mol the joint model's bias was 3.13, against
4.14 for the plain regression. With a direct effect of 1 mmol/mol it was 6.41,
against 4.51. With no hidden factor, the same two instruments gave a bias of
3.02 and 5.98, and a misclassification rate of 28.9% and 44.8%
([report 14](14_corrected_model_all_instrument_settings.md)).

### 11. An instrument must not be used as an ordinary feature

Added to the plain regression as a feature, the instrument increased its bias
by 0.10 to 0.17 mmol/mol at strength 0.5 and by 0.36 to 0.49 mmol/mol at
strength 1 ([report 11](11_instrument_as_a_feature.md)).

## How the joint-model findings changed

The first joint model assumed one noise level for both drugs, and the
simulated patients have two. An independent code review found this. It found
no error that changes a number in the other models, and least squares
reproduced the plain regression exactly.

Reports 06, 08, 09, 10 and 12 describe the first joint model and are kept as
they were written. Two of their findings changed:

- They reported that an ideal instrument removed 75% of the bias for the
  linear shape. The corrected model removes all of it.
- For the model without an instrument, report 12 found intervals with a
  coverage under 1% at 20,000 patients. The corrected model's estimate is
  imprecise instead.

[Report 13](13_verification_and_corrected_joint_model.md) sets the two models
side by side.

## The validation check

[Report 07](07_validation_check.md) applies a concordant-against-discordant
comparison to the simulated patients: patients who received the drug a model
recommends are compared with matched patients who did not. With a linear
hidden factor at strength 1, the plain regression predicted a benefit of 4.82
mmol/mol, the check observed 4.93, and the true benefit was 0.70.

Two limits apply. The matching was written from the description in published
papers, not from the authors' code, and may differ from theirs. The published
models were also validated in randomised trials, where a hidden factor cannot
drive the choice of drug, and this simulation has no trial arm.

## What this does not show

- **Nothing here is about real patients.** The size of any hidden factor in
  real prescribing is unknown.
- **It is not a verdict on any published model.**
- **The hidden factor is unrelated to every recorded feature.**
- **The joint model is the simplest of its kind:** a probit for drug choice,
  linear effects, and normal errors with a noise level per drug. Flexible
  versions were not implemented, so nothing here shows what they would
  achieve.
- **Small scale.** 5,000 patients per dataset (20,000 in one setting), and 10
  or 20 simulated datasets per setting.

## Next step

Allow ρ to differ by drug, as in an endogenous switching regression (Maddala
1983), and test whether the correction then holds for the effect shape. In the
effect shape the hidden factor acts on the outcome of GLP-1 patients only, and
the joint model has one ρ for both drugs. This reasoning comes from the code
and has not been tested.

## Reproducibility

Every run is a numbered script, every result row records the code commit that
produced it, and the long runs were shared between two computers that were
shown to give identical results for the same data
([report 04](04_cross_computer_check.md)).
