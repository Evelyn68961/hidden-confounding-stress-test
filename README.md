# Hidden-confounding stress test

A small simulation that asks: how wrong does a treatment selection model get
when something that drives the choice of drug is missing from the records?

**Status: in progress.** Step 1 of 4 is done. Nothing here is a finished result.

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

The patients are artificial. The effect sizes follow the direction of published
findings but were not estimated from patient data.

## Progress

| Step | Content | State |
|---|---|---|
| 1 | Patient generator; Bayesian causal forest with the hidden factor off | Done |
| 2 | Causal forest across three strengths and three shapes | Not started |
| 3 | Joint model of drug choice and outcome in PyMC | Not started |
| 4 | Figures and write-up | Not started |

### Step 1: nothing hidden

One simulated dataset of 5,000 patients (`scripts/01_causal_forest_no_hidden_factor.py`,
seed 1), fitted with four chains of 500 draws each after 200 warm-up draws.
True effects vary between patients with a standard deviation of 2.7 mmol/mol.

| Measure | Value |
|---|---|
| Error in the average effect | 0.13 mmol/mol |
| Typical error in one patient's effect | 0.78 mmol/mol |
| 95% intervals containing the truth | 99.6% |
| Patients sent to the worse drug | 5.5% |
| HbA1c lowering lost per patient | 0.02 mmol/mol |

| Do the chains agree? | Value |
|---|---|
| R-hat, average effect | 1.002 |
| R-hat, worst single patient | 1.050 |
| Patients with R-hat above 1.01 | 18% |

This is one dataset, so these numbers will move with the seed. The intervals
contain the truth more often than 95%, which means they are wider than needed
here. The chains agree on the average effect. For individual patients they
agree less closely: about one in five has an R-hat above the strict 1.01 limit,
though none is above 1.05.

## Run it

Requires [uv](https://docs.astral.sh/uv/).

```
uv sync
uv run pytest
uv run python scripts/01_causal_forest_no_hidden_factor.py
```

## Layout

- `src/stresstest/generator.py` makes the patients and holds the truth.
- `src/stresstest/causal_forest.py` fits the Bayesian causal forest ([stochtree](https://stochtree.ai/)).
- `src/stresstest/scoring.py` compares estimates with the truth.
- `tests/` checks that the generator does what it says.

## Reference

Hahn PR, Murray JS, Carvalho CM. Bayesian regression tree models for causal
inference: regularization, confounding, and heterogeneous effects. *Bayesian
Analysis* 2020;15(3):965–1056.
