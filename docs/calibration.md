# Where the numbers in the generator come from

The simulated patients are tuned to resemble the people starting an SGLT2
inhibitor or a GLP-1 receptor agonist in:

> Cardoso P, Young KG, Nair ATN, et al. Phenotype-based targeted treatment of
> SGLT2 inhibitors and GLP-1 receptor agonists in type 2 diabetes.
> *Diabetologia* 2024;67:822–836. https://pmc.ncbi.nlm.nih.gov/articles/PMC10955037/

No patient data were used. Only figures printed in the paper were used, and
the generator's settings were adjusted until a large simulated cohort
reproduced them. "Simulated" below is from 400,000 simulated patients with the
hidden factor off (seed 11).

## Who gets which drug

Source: Table 1 of the paper (28,081 starting a GLP-1 receptor agonist and
84,193 starting an SGLT2 inhibitor).

| Figure | Published | Simulated |
|---|---|---|
| Share starting the GLP-1 drug | 25% | 25% |
| Women, GLP-1 group | 46.7% | 47% |
| Women, SGLT2 group | 39.1% | 39% |
| BMI, GLP-1 group, mean (SD) | 37.3 (7.2) | 37.1 (6.9) |
| BMI, SGLT2 group | 33.7 (6.9) | 33.8 (6.8) |
| Starting HbA1c, GLP-1 group, mmol/mol | 78.6 (17.1) | 78.3 (17.8) |
| Starting HbA1c, SGLT2 group | 76.9 (16.9) | 76.6 (16.7) |
| eGFR, GLP-1 group | 92.0 (19.7) | 92.2 (16.9) |
| eGFR, SGLT2 group | 94.7 (15.5) | 94.6 (16.9) |
| Age, GLP-1 group, years | 57.7 (11.2) | 58.0 (11.0) |
| Age, SGLT2 group | 58.4 (10.8) | 58.0 (10.9) |

The coefficients in the drug-choice formula (`-1.3`, `0.31`, `0.073`,
`-0.009`, `0.006`) were set so that the group differences above come out
right. Age is not in the drug-choice formula, so the simulation does not
reproduce the small published age difference. The simulation gives both
groups the same eGFR spread; the published spreads differ.

## The outcome

| Figure | Published | Simulated |
|---|---|---|
| HbA1c change at 12 months, SGLT2 group, mean (SD), mmol/mol | −12.0 (15.3) | −11.8 (15.1) |
| HbA1c change, GLP-1 group | −11.7 (17.6) | −12.7 (14.8) |

`NOISE_SD = 12.5` was set to reproduce the spread in the SGLT2 group. The
simulation uses the same noise for both drugs, so it does not reproduce the
wider spread in the GLP-1 group.

## The drug effect and what changes it

| Figure | Published | Simulated |
|---|---|---|
| Average effect across everyone | 0.1 mmol/mol in favour of the GLP-1 drug (95% CrI −0.3 to 0.5) | 0.1 in favour of the GLP-1 drug |
| SGLT2 drug better by more than 3 mmol/mol | 17.5% | 15.9% |
| GLP-1 drug better by more than 3 mmol/mol | 20.3% | 19.5% |
| SGLT2 drug the better one, starting HbA1c below 64 | 32% | 34% |
| SGLT2 drug the better one, starting HbA1c 86 or above | 67% | 71% |
| Extra response to the GLP-1 drug in women | 4.4 mmol/mol (95% CrI 2.2 to 6.3), liraglutide arm of HARMONY-7 | 4.4 |

In the simulation the true effect has a standard deviation of 3.1 mmol/mol
across patients.

## Numbers that were chosen, not sourced

| Setting | Value | Note |
|---|---|---|
| Effect of eGFR on which drug is better | 0.08 per unit, favouring the SGLT2 drug | Direction from the paper: those with a greater predicted benefit on the GLP-1 drug were "predominantly female and older, with lower baseline HbA1c, eGFR and BMI". No size is given. The value was picked together with the BMI and HbA1c slopes to match the percentages above. |
| Effect of BMI on which drug is better | 0.15 per unit, favouring the SGLT2 drug | As for eGFR. In the paper's Table 2, BMI is among the features predicting the difference between the drugs and not among those predicting response on the SGLT2 drug; the generator follows that. |
| No effect of age on which drug is better | n/a | An omission. The paper reports that older patients benefit more from the GLP-1 drug and ranks age among the most influential predictors. Its most influential predictor, the number of other current glucose-lowering drugs, is not simulated at all. |
| Slope of HbA1c change on starting HbA1c | −0.5 per mmol/mol | Chosen. |
| Slope of HbA1c change on age | −0.05 per year | Chosen. |
| Spread of age, BMI and eGFR overall | 11, 7, 17 | Close to the published group SDs. |
| The hidden factor: strength scale, shapes, direction | See the generator | Chosen. This is the experimental setting, not a claim about real patients. |

## What this calibration is not

The simulation reproduces summary figures from one paper. It is not a model of
that cohort. The published treatment effects were themselves estimated from
observational records with a Bayesian causal forest, so they carry the same
risk of hidden confounding that this project studies.
