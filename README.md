# Hidden-confounding stress test

[![tests](https://github.com/Evelyn68961/hidden-confounding-stress-test/actions/workflows/tests.yml/badge.svg)](https://github.com/Evelyn68961/hidden-confounding-stress-test/actions/workflows/tests.yml)

A simulation of treatment selection models when a reason for the choice of
drug is not recorded. It asks how large the bias is, and whether a joint model
of drug choice and outcome can remove it.

**Author:** Evelyn Chang. Built with an AI coding assistant; see
[How this was built](#how-this-was-built).

**Status: preliminary results.** The numbers below rest on 10 or 20 simulated
datasets per setting. A uniform rerun (20 datasets and 2,000 draws per chain
for every setting) is in progress in `results/generator-v2/uniform_2000/`, and
the tables will be rebuilt from it when it finishes.

This is a learning exercise in Python, Bayesian causal forests and PyMC. It
uses simulated patients only. It is not a verdict on any published model.

## Findings at a glance

A hidden factor of strength 1 is the severe setting; strength 0.5 moves drug
choice about as much as BMI does. Bias is in mmol/mol of HbA1c.

- **A Bayesian causal forest did not remove the bias.** At strength 1 its
  bias matched the unadjusted bias (4.44 against 4.40 for the linear shape),
  and the coverage of its 95% intervals fell from 94.3% to between 27.6% and
  49.8%.
- **A joint model with a valid instrument removed the bias for the linear and
  threshold shapes** (3.72 to −0.01, and 2.83 to 0.12), and it lowered the
  RMSE and the misclassification rate for all three shapes. For the effect
  shape a bias of 1.20 remained, out of 2.60.
- **With a weaker hidden factor (strength 0.5) the joint model still removed
  the bias, but it did not lower the RMSE or the misclassification rate.**
- **Without an instrument the joint model did not clearly lower the RMSE**, at
  5,000 or at 20,000 patients. Its estimate of ρ was imprecise (95% interval
  −0.40 to 0.50 with 5,000 patients).
- **The instrument has to be valid.** With an instrument that also had a
  direct effect on the outcome, the joint model stayed biased (3.13 and 6.41
  for direct effects of 0.5 and 1 mmol/mol).
- **With no hidden factor, the joint model had a higher misclassification rate
  than the plain regression with every instrument.**
- **Adding the instrument to the plain regression as an ordinary feature
  increased its bias**, by 0.10 to 0.17 mmol/mol at strength 0.5 and by 0.36
  to 0.49 mmol/mol at strength 1.

## The problem

Treatment selection models learn from health records which drug works best for
which patient. Doctors choose drugs for reasons that are not always recorded,
for example frailty. When such a reason also affects the outcome, the
estimated drug effect is confounded.

In real records this cannot be checked, because each patient takes one drug
and their result on the other drug never exists. In a simulation each
patient's true drug effect is known, so the error can be measured.

## The simulation

1. **Simulate patients.** 5,000 per dataset, with type 2 diabetes, starting an
   SGLT2 inhibitor or a GLP-1 receptor agonist. The outcome is the change in
   HbA1c at 12 months.
2. **Add a hidden factor.** Either off, or on with one of three shapes and one
   of two strengths.
3. **Add an instrument.** A variable that shifts drug choice, in four
   settings.
4. **Fit three models to each dataset:** a Bayesian causal forest, a plain
   regression and a joint model.
5. **Score each model** against each patient's known true drug effect.
6. **Repeat** on new simulated datasets, and average the scores.

The patients are tuned to the summary figures printed in Cardoso et al.,
*Diabetologia* 2024;67:822–836. No patient data are used. Each number, its
source and how closely the simulation reproduces it are in
[docs/calibration.md](docs/calibration.md).

### The hidden factor

Each patient has a hidden factor, a standard normal value. It is not given to
any model.

**Strength (s)** sets how much it shifts drug choice and the outcome. For a
patient whose hidden factor is 1 SD above average:

| Strength | Chance of being prescribed GLP-1 (a man with average features) | HbA1c at 12 months higher by (linear shape) |
|---|---|---|
| 0 (off) | 21% | 0 mmol/mol |
| 0.5 | 30% | 2.5 mmol/mol |
| 1 | 41% | 5 mmol/mol |

For comparison, a BMI 1 SD higher also gives 30%, and the mean fall in HbA1c
on either drug is 12 mmol/mol.

**Shape** is how the outcome changes as the hidden factor rises:

- `linear`: the outcome worsens in proportion to the hidden factor;
- `threshold`: the outcome worsens by a fixed amount above +1 SD, which is the
  16% of patients with the highest values;
- `effect`: the effect of the GLP-1 drug weakens.

### The three models

| Model | Form | Fitted with |
|---|---|---|
| Bayesian causal forest | HbA1c change = μ(x) + τ(x) × drug + noise, where μ and τ are sums of regression trees (Hahn, Murray and Carvalho 2020) | [stochtree](https://stochtree.ai/), default priors, four chains |
| Plain regression | HbA1c change = a + b·x + (c + d·x) × drug + noise | [PyMC](https://www.pymc.io/), four chains |
| Joint model | The plain regression's outcome equation with error ε₁, and a probit equation for drug choice with error ε₂ that may include an instrument z. ρ is the correlation between ε₁ and ε₂ | PyMC, four chains |

A hidden cause of both drug choice and outcome makes ρ non-zero. The joint
model estimates ρ and uses it to correct the drug effect. It assumes normal
errors, with a noise level per drug, and with ρ = 0 it is the plain
regression. It is the simplest model of the kind in Conley, Hansen, McCulloch
and Rossi (2008).

### The instrument

An instrument is a variable that shifts drug choice, is independent of the
hidden factor, and affects the outcome only through drug choice. The
simulated instrument is a standard normal variable.

| Setting | Instrument varies by | Effect on drug choice | Direct effect on the outcome |
|---|---|---|---|
| Ideal | Patient | Log-odds of GLP-1 + 1 per SD | None |
| Practice-level | Practice (100 or 25) | Log-odds of GLP-1 + 1 per SD | None |
| Weaker | Patient | Log-odds of GLP-1 + 0.5 per SD | None |
| Direct effect | Patient | Log-odds of GLP-1 + 1 per SD | 0.5 or 1 mmol/mol per SD |

The direct-effect setting violates the exclusion restriction.

### How each model is scored

The true drug effect is known for every simulated patient: the HbA1c result on
the GLP-1 drug minus the result on the SGLT2 drug.

| Score | Definition | Ideal |
|---|---|---|
| Bias | Mean, over datasets, of the estimated minus the true average drug effect, in mmol/mol | 0 |
| RMSE | Root mean squared error of the estimated average drug effect, over datasets, in mmol/mol | 0 |
| Coverage | Share of patients whose 95% interval contains their true effect | 95% |
| Misclassification rate | Share of patients for whom the model picks the worse drug | A coin toss gives 50% |

The estimands are the average treatment effect (bias and RMSE) and each
patient's conditional average treatment effect (coverage and misclassification
rate). Reporting follows Morris, White and Crowther (2019).

## Results

Bias and RMSE are in mmol/mol. Coverage and misclassification rate are in %.
Every table gives its number of datasets and the report that holds the checks
and limits.

### Can a causal forest cope with a hidden factor?

20 datasets per setting ([report 03](reports/03_causal_forest_grid.md)).

| Hidden factor | Bias, not adjusted | Bias, causal forest | Coverage | Misclassification rate |
|---|---|---|---|---|
| No hidden factor | 0.30 | 0.12 | 94.3 | 16.5 |
| Strength 0.5, linear | 1.53 | 1.39 | 87.3 | 21.2 |
| Strength 0.5, threshold | 1.22 | 1.06 | 90.5 | 19.2 |
| Strength 0.5, effect | 1.23 | 1.06 | 90.1 | 19.3 |
| Strength 1, linear | 4.40 | 4.44 | 27.6 | 43.2 |
| Strength 1, threshold | 3.49 | 3.52 | 45.7 | 37.2 |
| Strength 1, effect | 3.25 | 3.18 | 49.8 | 34.2 |

"Not adjusted" is the mean outcome on the GLP-1 drug minus the mean on the
SGLT2 drug, minus the true average effect.

The causal forest did not remove the bias. At strength 1 its bias matched the
unadjusted bias, and the coverage of its 95% intervals fell from 94.3% to
between 27.6% and 49.8%.

### Can a joint model with a valid instrument remove the bias?

Ideal instrument, 20 datasets per setting
([report 13](reports/13_verification_and_corrected_joint_model.md),
[report 14](reports/14_corrected_model_all_instrument_settings.md)).

| Hidden factor | Bias, plain | Bias, joint | RMSE, plain | RMSE, joint | Misclassification, plain | Misclassification, joint |
|---|---|---|---|---|---|---|
| No hidden factor | 0.13 | 0.12 | 0.54 | 1.55 | 9.7 | 16.3 |
| Strength 1, linear | 3.72 | −0.01 | 3.75 | 1.70 | 34.7 | 18.2 |
| Strength 1, threshold | 2.83 | 0.12 | 2.87 | 1.77 | 28.0 | 18.4 |
| Strength 1, effect | 2.60 | 1.20 | 2.64 | 2.07 | 26.0 | 20.2 |

The joint model removed the bias for the linear and threshold shapes, and it
lowered the RMSE and the misclassification rate for all three shapes. For the
effect shape a bias of 1.20 remained. For the linear shape ρ was 0.16 (0.05 to
0.27), and its true value is about 0.16.

### Does the joint model still help with a weaker hidden factor?

Ideal instrument, 20 datasets per setting. Computed from
`results/generator-v2/per_drug_noise/` and `results/generator-v2/instrument/`,
on the same simulated datasets for both models.

| Hidden factor | Bias, plain | Bias, joint | RMSE, plain | RMSE, joint | Misclassification, plain | Misclassification, joint |
|---|---|---|---|---|---|---|
| Strength 0.5, linear | 1.07 | 0.05 | 1.18 | 1.57 | 14.4 | 16.6 |
| Strength 0.5, threshold | 0.79 | 0.15 | 0.93 | 1.59 | 12.9 | 16.6 |
| Strength 0.5, effect | 0.77 | 0.40 | 0.92 | 1.61 | 13.0 | 16.5 |

The joint model still removed the bias, but it did not lower the RMSE or the
misclassification rate.

### Does the joint model work without an instrument?

Linear hidden factor at strength 1, no instrument, 10 datasets per row
([report 13](reports/13_verification_and_corrected_joint_model.md)).

| Patients per dataset | Bias, plain | Bias, joint | RMSE, plain | RMSE, joint | Misclassification, plain | Misclassification, joint |
|---|---|---|---|---|---|---|
| 5,000 | 4.20 | 0.68 | 4.22 | 5.22 | 38.2 | 36.8 |
| 20,000 | 4.32 | 1.97 | 4.32 | 3.82 | 38.6 | 28.6 |

Without an instrument the joint model did not clearly lower the RMSE at either
sample size. Its estimate of ρ was imprecise (95% interval −0.40 to 0.50 with
5,000 patients). In a quarter of these joint fits the largest R-hat was above
1.01 (maximum 1.03).

### What if the instrument is less than ideal?

Linear hidden factor at strength 1. The ideal row uses 20 datasets and the
other rows 10
([report 14](reports/14_corrected_model_all_instrument_settings.md)).

| Instrument | Bias, plain | Bias, joint | Misclassification, plain | Misclassification, joint |
|---|---|---|---|---|
| Ideal | 3.72 | −0.01 | 34.7 | 18.2 |
| Practice-level, 100 practices | 3.90 | −0.39 | 36.3 | 16.2 |
| Practice-level, 25 practices | 3.77 | −0.38 | 34.4 | 16.9 |
| Weaker | 4.10 | 0.23 | 36.5 | 26.2 |
| Direct effect, 0.5 mmol/mol | 4.14 | 3.13 | 37.1 | 28.8 |
| Direct effect, 1 mmol/mol | 4.51 | 6.41 | 39.4 | 44.8 |

The joint model removed the bias with the practice-level instruments. Its
estimate was imprecise with the weaker instrument. It stayed biased with the
direct-effect instruments.

### What does the joint model cost when nothing is hidden?

No hidden factor. The ideal row uses 20 datasets and the other rows 10
([report 14](reports/14_corrected_model_all_instrument_settings.md)).

| Instrument | Bias, plain | Bias, joint | Misclassification, plain | Misclassification, joint |
|---|---|---|---|---|
| Ideal | 0.13 | 0.12 | 9.7 | 16.3 |
| Practice-level, 100 practices | −0.07 | −0.03 | 10.8 | 15.3 |
| Practice-level, 25 practices | −0.01 | −0.24 | 11.8 | 18.9 |
| Weaker | 0.01 | 0.20 | 11.5 | 23.0 |
| Direct effect, 0.5 mmol/mol | 0.57 | 3.02 | 11.4 | 28.9 |
| Direct effect, 1 mmol/mol | 0.99 | 5.98 | 13.6 | 44.8 |

The joint model had a higher misclassification rate than the plain regression
with every instrument. The direct-effect instruments also added bias.

### Can the instrument be used as an ordinary feature?

Bias of the plain regression with the ideal instrument left out or added as a
feature. 10 datasets per setting; the increase is paired by dataset
([report 11](reports/11_instrument_as_a_feature.md)).

| Hidden factor | Left out | As a feature | Increase in bias |
|---|---|---|---|
| No hidden factor | 0.15 | 0.16 | +0.01 |
| Strength 0.5, linear | 1.06 | 1.23 | +0.17 |
| Strength 0.5, threshold | 0.79 | 0.90 | +0.10 |
| Strength 0.5, effect | 0.78 | 0.92 | +0.14 |
| Strength 1, linear | 3.77 | 4.26 | +0.49 |
| Strength 1, threshold | 2.91 | 3.30 | +0.39 |
| Strength 1, effect | 2.65 | 3.00 | +0.36 |

Adding the instrument to the plain regression as a feature increased its bias
by 0.10 to 0.17 mmol/mol with a hidden factor of strength 0.5, and by 0.36 to
0.49 mmol/mol at strength 1.

## Limits and next step

| Limit | What it means |
|---|---|
| Simulation only | The size of any hidden factor in real prescribing is unknown. |
| Independent hidden factor | Unrelated to every recorded feature. |
| Simple joint model | Probit choice, linear effects, normal errors with a noise level per drug. |
| Small scale | 5,000 patients per dataset (20,000 in one setting), and 10 or 20 simulated datasets per setting. |

**Next step:** allow ρ to differ by drug, as in an endogenous switching
regression (Maddala 1983), and test whether the correction then holds for the
effect shape. In the effect shape the hidden factor acts on the outcome of
GLP-1 patients only, and the joint model has one ρ for both drugs. This
reasoning comes from the code and has not been tested.

## Also in this repository

- **An earlier joint model.** The first joint model assumed one noise level
  for both drugs, where the simulated patients have two. An independent review
  found this, and the model was refitted with a noise level per drug. Reports
  06, 08, 09, 10 and 12 describe the first model and are kept as they were
  written; reports 06, 08, 10 and 12 carry a dated correction.
  [Report 13](reports/13_verification_and_corrected_joint_model.md) sets the
  two side by side. Every joint-model number on this page is from the
  corrected model.
- **A validation check.** [Report 07](reports/07_validation_check.md) applies
  a concordant-against-discordant comparison to the simulated patients. The
  matching was written from the description in published papers, not from the
  authors' code, and the simulation has no trial arm.
- **A plain-language account** of all the reports is in
  [reports/SUMMARY.md](reports/SUMMARY.md), and the reports are listed in
  [reports/README.md](reports/README.md).

## Run it

Requires [uv](https://docs.astral.sh/uv/).

```
uv sync
uv run pytest
uv run python scripts/01_causal_forest_no_hidden_factor.py
uv run python scripts/02_what_the_hidden_factor_does.py
uv run python scripts/03_causal_forest_grid.py     # many hours
uv run python scripts/04_cross_check.py compare
uv run python scripts/05_summarise_grid.py
uv run python scripts/06_joint_model_trial.py
uv run python scripts/07_joint_model_check.py
uv run python scripts/08_joint_model_grid.py       # about 2.5 hours
uv run python scripts/09_validation_framework.py   # about 45 minutes
uv run python scripts/10_instrument_grid.py        # about 2.5 hours
uv run python scripts/11_summarise_step3.py
uv run python scripts/12_followup_runs.py --run realistic       # about 1.5 hours
uv run python scripts/12_followup_runs.py --run as_feature      # about 30 minutes
uv run python scripts/12_followup_runs.py --run more_patients   # about 1 hour
uv run python scripts/12_followup_runs.py --run per_drug_noise  # about 8 hours
uv run python scripts/13_summarise_followups.py
uv run python scripts/14_uniform_runs.py           # several days; in progress
uv run python checks/independent_check_1.py                     # about a minute
uv run python checks/independent_check_2.py
```

To check the reported numbers without refitting anything, run the tests and
scripts 05, 11 and 13. They rebuild the tables and figures in `reports/` from
the saved results.

The long runs save each result as it finishes and continue where they stopped
if run again. Script 03 can be shared between computers; see
[docs/RUNNER.md](docs/RUNNER.md).

## Layout

- `src/stresstest/generator.py` makes the patients and holds the truth.
- `src/stresstest/causal_forest.py` fits the Bayesian causal forest.
- `src/stresstest/joint_model.py` fits the plain regression and the joint model.
- `src/stresstest/validation.py` is the concordant-against-discordant check.
- `src/stresstest/scoring.py` compares estimates with the truth.
- `docs/calibration.md` lists where each number in the generator comes from.
- `docs/RUNNER.md` explains how a second computer runs part of the long jobs
  without the results getting mixed up.
- `checks/` holds two scripts that recompute key results with least squares
  and a classical two-step correction, using numpy and scipy only.
- `tests/` checks the generator, including that the simulated cohort matches
  the published figures, and the validation check.
- `scripts/` holds one numbered script per run or analysis.
- `reports/` holds one progress report per run: the question, what was run,
  the result, how to read it and its limits.
- `results/generator-v<N>/` holds the saved output of the long runs: one
  folder per version of the generator, one file per computer. Results from
  different versions are never pooled. The files and their columns are
  described in [results/README.md](results/README.md).

## How this was built

The code, reports and figures were written with an AI coding assistant
(Claude Code), as the commit history shows. The author chose the question,
decided the design in discussion with the assistant, and reviewed each result
before the next step.

- **Checks that changed the work.** The first version of the simulated
  patients did not reproduce the published outcome in both drug groups. It was
  replaced, and its results are kept apart in `results/generator-v1/` and used
  nowhere. The first forest fits ran one chain; all reported fits run four.
  An independent code review led to the corrected joint model.
- **Second methods.** Least squares reproduces the plain regression, and a
  classical two-step correction agrees with the joint model to within 0.15
  mmol/mol on the first ten datasets (`checks/`).
- **Two computers.** The long runs were shared between two computers, each
  operated by an assistant session. The reports and logs call them the lead
  and the runner. [Report 04](reports/04_cross_computer_check.md) shows they
  simulate the same patients and give the same scores.
- **What is reproducible.** Every result row records the commit of the code
  that produced it.

## References

- Cardoso P, Young KG, Nair ATN, et al. Phenotype-based targeted treatment of
  SGLT2 inhibitors and GLP-1 receptor agonists in type 2 diabetes.
  *Diabetologia* 2024;67:822–836.
- Conley TG, Hansen CB, McCulloch RE, Rossi PE. A semi-parametric Bayesian
  approach to the instrumental variable problem. *J Econometrics*
  2008;144:276–305.
- Hahn PR, Murray JS, Carvalho CM. Bayesian regression tree models for causal
  inference: regularization, confounding, and heterogeneous effects. *Bayesian
  Analysis* 2020;15(3):965–1056.
- Maddala GS. *Limited-Dependent and Qualitative Variables in Econometrics*.
  Cambridge University Press, 1983.
- Morris TP, White IR, Crowther MJ. Using simulation studies to evaluate
  statistical methods. *Stat Med* 2019;38:2074–2102.
- Dennis JM, Young KG, Cardoso P, et al. A five-drug class model using
  routinely available clinical features to optimise prescribing in type 2
  diabetes. *Lancet* 2025;405:701–714.
- Dennis JM, Young KG, McGovern AP, et al. Development of a treatment
  selection algorithm for SGLT2 and DPP-4 inhibitor therapies in people with
  type 2 diabetes. *Lancet Digit Health* 2022;4:e873–e883.
- Brooks JM, Chapman CG, Chen BK, Floyd SB, Hikmet N. Assessing the properties
  of patient-specific treatment effect estimates from causal forest algorithms
  under essential heterogeneity. *BMC Med Res Methodol* 2024;24:66.
