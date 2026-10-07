# Where the numbers in the generator come from

The simulated patients are tuned to resemble the people starting an SGLT2
inhibitor or a GLP-1 receptor agonist in:

> Cardoso P, Young KG, Nair ATN, et al. Phenotype-based targeted treatment of
> SGLT2 inhibitors and GLP-1 receptor agonists in type 2 diabetes.
> *Diabetologia* 2024;67:822–836. https://doi.org/10.1007/s00125-024-06099-3

No patient data were used. Only figures printed in the paper were used, and
the generator's settings were adjusted until a large simulated cohort
reproduced them. "Simulated" below is from 400,000 simulated patients with the
hidden factor off (seed 11), generator version 2.

## Generator versions

| Version | Features | Why it was replaced |
|---|---|---|
| 1 | Age, sex, starting HbA1c, BMI, eGFR | Age did not change which drug is better, although the paper says it does. The GLP-1 group's simulated HbA1c change was −12.7 against a published −11.7, so the simulated GLP-1 group did better than the SGLT2 group where the published one did slightly worse. |
| 2 (current) | Adds the number of drug classes ever prescribed and the number of other current diabetes drugs; age now changes which drug is better; each drug has its own noise level | n/a |

Results from different versions are kept in separate folders under `results/`
and are never pooled.

## Who gets which drug

Source: Table 1 of the paper (28,081 starting a GLP-1 receptor agonist and
84,193 starting an SGLT2 inhibitor).

| Figure | Published | Simulated |
|---|---|---|
| Share starting the GLP-1 drug | 25% | 25% |
| Women, GLP-1 group | 46.7% | 46% |
| Women, SGLT2 group | 39.1% | 39% |
| Age, GLP-1 group, mean (SD), years | 57.7 (11.2) | 57.5 (10.9) |
| Age, SGLT2 group | 58.4 (10.8) | 58.2 (10.9) |
| BMI, GLP-1 group | 37.3 (7.2) | 37.0 (6.9) |
| BMI, SGLT2 group | 33.7 (6.9) | 33.8 (6.8) |
| Starting HbA1c, GLP-1 group, mmol/mol | 78.6 (17.1) | 78.2 (17.8) |
| Starting HbA1c, SGLT2 group | 76.9 (16.9) | 76.7 (16.7) |
| eGFR, GLP-1 group | 92.0 (19.7) | 92.4 (17.0) |
| eGFR, SGLT2 group | 94.7 (15.5) | 94.6 (16.9) |
| Drug classes ever prescribed (2 / 3 / 4 / 5 or more), GLP-1 group | 10.3 / 24.1 / 37.5 / 28.1% | 11.4 / 23.6 / 35.7 / 29.2% |
| Drug classes ever prescribed, SGLT2 group | 22.2 / 30.4 / 30.0 / 17.4% | 21.8 / 30.5 / 30.8 / 16.9% |
| Other current diabetes drugs (0 / 1 / 2 / 3 / 4 or more), GLP-1 group | 4.1 / 35.4 / 44.2 / 13.8 / 0.8% | 4.4 / 35.8 / 44.8 / 14.5 / 0.5% |
| Other current diabetes drugs, SGLT2 group | 6.1 / 40.4 / 42.2 / 10.9 / 0.3% | 6.0 / 40.5 / 41.9 / 11.3 / 0.4% |

The coefficients in the drug-choice formula were set so that the group
differences above come out right. For a continuous feature, the coefficient
is roughly the published difference between the groups divided by the
feature's variance. For sex it is the logarithm of the odds ratio. For the two
counts it is the slope of the log ratio of the two groups' percentages.

The simulation gives both groups the same eGFR spread; the published spreads
differ. The two counts are simulated as unrelated to each other and to the
other features, which they would not be in real patients.

## The outcome

| Figure | Published | Simulated |
|---|---|---|
| HbA1c change at 12 months, SGLT2 group, mean (SD), mmol/mol | −12.0 (15.3) | −12.0 (15.3) |
| HbA1c change, GLP-1 group | −11.7 (17.6) | −11.7 (17.6) |

Three settings were solved to reproduce these four numbers: the two noise
levels (12.6 on the SGLT2 drug, 15.4 on the GLP-1 drug) and the effect of
drug classes ever prescribed on response (+2.45 mmol/mol per class: patients
who have been through more drugs respond less). The paper lists that count
among the predictors of response; it gives no size.

## The drug effect and what changes it

| Figure | Published | Simulated |
|---|---|---|
| Average effect across everyone | 0.1 mmol/mol in favour of the GLP-1 drug (95% CrI −0.3 to 0.5) | 0.1 in favour of the GLP-1 drug |
| GLP-1 drug the better one | 52% | 50% |
| SGLT2 drug better by more than 3 mmol/mol | 17.5% | 17.8% |
| GLP-1 drug better by more than 3 mmol/mol | 20.3% | 20.4% |
| SGLT2 drug the better one, starting HbA1c below 64 | 32% | 34% |
| SGLT2 drug the better one, starting HbA1c 86 or above | 67% | 71% |
| Extra response to the GLP-1 drug in women | 4.4 mmol/mol (95% CrI 2.2 to 6.3), liraglutide arm of HARMONY-7 | 4.4 |

Directions are from the paper: those with a greater predicted benefit on the
GLP-1 drug were "predominantly female and older, with lower baseline HbA1c,
eGFR and BMI", and "a higher number of concurrent therapies" favoured the
SGLT2 drug. The paper gives no slopes. They were found by trying 243
combinations of the five slopes and keeping one that came closest to the four
percentages above.

In the simulation the true effect has a standard deviation of 3.3 mmol/mol
across patients.

## Numbers that were chosen, not sourced

| Setting | Value | Note |
|---|---|---|
| Age on which drug is better | −0.12 per year (older favours the GLP-1 drug) | Direction from the paper; size from the search. |
| Other current drugs on which drug is better | +1.5 per drug (more favours the SGLT2 drug) | Direction from the paper; size from the search. |
| Starting HbA1c on which drug is better | +0.08 per mmol/mol | Direction from the paper; size pinned fairly tightly by the two HbA1c percentages. |
| eGFR on which drug is better | +0.05 per unit | Direction from the paper; size from the search. |
| BMI on which drug is better | +0.10 per unit | Direction from the paper; size from the search. In the paper's Table 2, BMI is among the features predicting the difference between the drugs and not among those predicting response on the SGLT2 drug; the generator follows that. |
| Slope of HbA1c change on starting HbA1c | −0.5 per mmol/mol | Chosen. |
| Slope of HbA1c change on age | −0.05 per year | Chosen. |
| The hidden factor: strength scale, shapes, direction | See the generator | Chosen. This is the experimental setting, not a claim about real patients. |

Several combinations of slopes fit the published percentages almost equally
well. The ones used are one reasonable choice, not the only one.

## What this calibration is not

The simulation reproduces summary figures from one paper. It is not a model of
that cohort. Features in the published model that are not simulated include
diabetes duration, ALT and the comorbidities. The published treatment effects
were themselves estimated from observational records with a Bayesian causal
forest, so they carry the same risk of hidden confounding that this project
studies.
