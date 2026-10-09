# Saved results

Every long run saves one row per fitted model. The summary scripts
(`scripts/05_summarise_grid.py` and `scripts/11_summarise_step3.py`) read
these files and write the tables and figures in `reports/`.

## Layout

One folder per version of the patient generator. Results from different
versions are never pooled.

| Path | Rows | What it holds | Written by |
|---|---|---|---|
| `generator-v2/EVELYN68961.csv` | 119 | Causal forest, hidden factor on; repeats 0 to 9 and 13 to 19 | `scripts/03_causal_forest_grid.py` |
| `generator-v2/EVELYN68961PC.csv` | 21 | Causal forest, hidden factor on; repeats 10 to 12, second computer | `scripts/03_causal_forest_grid.py` |
| `generator-v2/EVELYN68961PC_RUNLOG.md` | | Log of the second computer's run | by hand |
| `generator-v2/crosscheck/*_fingerprints.csv` | 14 each | A SHA-256 fingerprint of each simulated dataset, per computer | `scripts/04_cross_check.py fingerprint` |
| `generator-v2/crosscheck/EVELYN68961_refits.csv` | 3 | Three of the second computer's fits, repeated on the first | `scripts/04_cross_check.py refit` |
| `generator-v2/joint_model/EVELYN68961.csv` | 280 | Plain regression and joint model, no instrument; 20 datasets per setting | `scripts/08_joint_model_grid.py` |
| `generator-v2/validation/EVELYN68961.csv` | 280 | The concordant-against-discordant check, for the plain regression and for a model that is exactly right | `scripts/09_validation_framework.py` |
| `generator-v2/instrument/EVELYN68961.csv` | 560 | Plain regression and joint model, with an instrument; 20 datasets per setting. Report 08 uses datasets 0 to 9; report 09 adds 10 to 19 | `scripts/10_instrument_grid.py` |
| `generator-v2/realistic/EVELYN68961.csv` | 160 | Plain regression and joint model with four less ideal instruments (report 10) | `scripts/12_followup_runs.py --run realistic` |
| `generator-v2/as_feature/EVELYN68961.csv` | 70 | Plain regression with the instrument added as a feature (report 11) | `scripts/12_followup_runs.py --run as_feature` |
| `generator-v2/more_patients/EVELYN68961.csv` | 40 | Plain regression and joint model on 20,000 patients, no instrument (report 12) | `scripts/12_followup_runs.py --run more_patients` |
| `generator-v2/per_drug_noise/EVELYN68961.csv` | 110 | Joint model with a noise level per drug: with the ideal instrument, and without an instrument at 5,000 and 20,000 patients (report 13) | `scripts/12_followup_runs.py --run per_drug_noise` |
| `generator-v1/` | 24 | Superseded. Kept as a record and used nowhere; see its own README | |

The file name is the name of the computer that produced it. Each computer
writes only its own files, so results from two computers cannot be mixed.

## Columns

Where a row came from:

| Column | Meaning |
|---|---|
| `generator_version` | Version of the patient generator |
| `host` | Computer that ran the fit |
| `code_commit` | Git commit of the code that ran. The scripts refuse to run with uncommitted changes |
| `seconds` | Time the fit took |

The setting:

| Column | Meaning |
|---|---|
| `shape` | Form of the hidden factor: `none`, `linear`, `threshold` or `effect` |
| `strength` | Strength of the hidden factor: 0, 0.5 or 1 |
| `instrument_strength` | Strength of the instrument: 0.5 or 1 (instrument file only) |
| `repeat` | Number of the simulated dataset. It is also the random seed |
| `model` | `plain` or `joint`; in the validation file, `plain` or `truth`; in the as-feature file, `plain_with_instrument`; in the per-drug-noise file, `joint_per_drug_noise` |
| `run`, `variant` | Follow-up files: which run, and which instrument (`practice_100`, `practice_25`, `flaw_0.5`, `flaw_1.0`, `ideal_as_feature`, `ideal_instrument`, `no_instrument`, `no_instrument_20000`) |
| `patients` | Follow-up files: patients per dataset |

The scores, all against the known truth (errors in mmol/mol of HbA1c):

| Column | Meaning |
|---|---|
| `crude_error` | Error of comparing the two drug groups with no adjustment |
| `bias_average` | Estimated minus true average drug effect |
| `rmse_individual` | Typical error in one patient's estimated effect |
| `coverage_95` | Share of patients whose 95% interval contains their true effect |
| `wrong_drug` | Share of patients for whom the model picks the worse drug |
| `hba1c_lost` | HbA1c lowering lost per patient by following the model |
| `rho_mean`, `rho_low`, `rho_high` | Joint model: posterior mean and 95% interval of the correlation between the errors of the choice and outcome equations |

Whether the sampler settled:

| Column | Meaning |
|---|---|
| `rhat_average_effect` | R-hat of the average effect |
| `rhat_worst_patient` | Largest R-hat of any one patient's effect |
| `share_patients_rhat_above_1.01` | Share of patients whose R-hat is above 1.01 |

The validation check:

| Column | Meaning |
|---|---|
| `share_concordant` | Share of patients who received the drug the model recommends |
| `pairs` | Number of matched pairs |
| `predicted_benefit` | Benefit of the recommended drug that the model predicts |
| `observed_benefit` | Benefit the check observes in the matched pairs |
| `true_benefit` | True benefit, known only in a simulation |
