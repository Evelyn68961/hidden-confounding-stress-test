# Hidden-confounding stress test

A small simulation that asks: how wrong does a treatment selection model get
when something that drives the choice of drug is missing from the records?

**Status: in progress.** Step 1 of 4 is done and step 2 is running. Nothing here is a finished result.

## The problem

Treatment selection models learn from health records which drug works best for
which patient. In records, doctors choose drugs for reasons that are often not
written down, such as frailty.

Suppose frail patients are more often given drug A, and frail patients also
respond worse to any drug. A model sees worse results on drug A and blames the
drug. In real records this cannot be checked, because each patient takes one
drug and their result on the other drug never exists.

## The approach

In a simulation the true effect of each drug on each patient is known, so a
model's estimates can be scored against it.

1. Simulate people with type 2 diabetes starting an SGLT2 inhibitor or a GLP-1
   receptor agonist. The outcome is the change in HbA1c at 12 months.
2. Add a hidden factor that affects both the drug chosen and the outcome. Vary
   its **strength**, and the **shape** of its effect on the outcome:
   - `linear`: each extra unit worsens the result by the same amount;
   - `threshold`: only patients above a cut-off are affected;
   - `effect`: it changes how well one drug works.
3. Hide the factor and fit the models.
4. Score each model against the truth: error in each patient's estimated
   effect, whether the 95% intervals contain the truth, and the share of
   patients who would be sent to the worse drug.

The patients are artificial. They are tuned to resemble the cohort in Cardoso
et al., *Diabetologia* 2024, using only figures printed in that paper. Each
number, its source and how closely the simulation reproduces it are in
[docs/calibration.md](docs/calibration.md).

## Progress

| Step | Content | State |
|---|---|---|
| 1 | Patient generator; Bayesian causal forest with the hidden factor off; what each setting of the hidden factor does to the data | Done ([report 01](reports/01_causal_forest_no_hidden_factor.md), [report 02](reports/02_what_the_hidden_factor_does.md)) |
| 2 | Causal forest with the hidden factor on: two strengths, three shapes, 20 datasets each | Running |
| 3 | Joint model of drug choice and outcome in PyMC | Not started |
| 4 | Figures and write-up | Not started |

### Step 1: nothing hidden

One simulated dataset of 5,000 patients (`scripts/01_causal_forest_no_hidden_factor.py`,
seed 1), fitted with four chains of 2,000 draws each after 500 warm-up draws.
True effects vary between patients with a standard deviation of 3.1 mmol/mol.

| Measure | Value |
|---|---|
| Error in the average effect | 0.92 mmol/mol |
| Typical error in one patient's effect | 1.48 mmol/mol |
| 95% intervals containing the truth | 98.4% |
| Patients sent to the worse drug | 16.5% |
| HbA1c lowering lost per patient | 0.16 mmol/mol |
| R-hat, worst single patient | 1.009 |

This is one dataset, so these numbers will move with the seed. Even with
nothing hidden, the forest is far from perfect on realistic patients: one in
four gets the GLP-1 drug and the outcome is noisy. Whether the error in the
average effect is chance or a systematic lean is settled by the repeats in
step 2.

## Run it

Requires [uv](https://docs.astral.sh/uv/).

```
uv sync
uv run pytest
uv run python scripts/01_causal_forest_no_hidden_factor.py
uv run python scripts/02_what_the_hidden_factor_does.py
uv run python scripts/03_causal_forest_grid.py   # several hours
```

## Layout

- `src/stresstest/generator.py` makes the patients and holds the truth.
- `src/stresstest/causal_forest.py` fits the Bayesian causal forest ([stochtree](https://stochtree.ai/)).
- `src/stresstest/scoring.py` compares estimates with the truth.
- `docs/calibration.md` lists where each number in the generator comes from.
- `tests/` checks that the generator does what it says, including that the
  simulated cohort matches the published figures.
- `results/` holds the saved output of the long runs.
- `scripts/` holds one numbered script per run or analysis.
- `reports/` holds one progress report per script: the question, what was run,
  the result, how to read it and its limits. Start at [reports/README.md](reports/README.md).

## Reference

Hahn PR, Murray JS, Carvalho CM. Bayesian regression tree models for causal
inference: regularization, confounding, and heterogeneous effects. *Bayesian
Analysis* 2020;15(3):965??056.
