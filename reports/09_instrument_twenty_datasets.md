# Report 09: the instrument result on ten more datasets

**Date:** 2026-10-08
**Scripts:** `scripts/10_instrument_grid.py` (the run), `scripts/13_summarise_followups.py` (the table)
**Results:** `results/generator-v2/instrument/EVELYN68961.csv`, rows with `repeat` 10 to 19 (280 new rows)
**Table:** `reports/tables/followup_instrument_twenty.csv`
**Code commit recorded in the new rows:** b41aaa2

## Question

Report 08 rests on ten datasets per setting, half as many as the earlier
steps. Does its result hold on ten new datasets?

## What was run

- The run of report 08 again, for datasets 10 to 19: the seven hidden-factor
  settings at both instrument strengths, plain regression and joint model.
- Nothing else changed. The patient generator gained two options between the
  two runs, both off here; the dataset fingerprints of report 04 are
  identical before and after.
- **Report 08 is not changed.** Its table and figure are still built from
  datasets 0 to 9 only. The new rows sit beside the old ones in the same
  file and are told apart by `repeat` and by `code_commit` (925d113 for the
  first ten, b41aaa2 for the second ten).

## Result

Hidden factor at strength 1, or off. Errors in the average effect, in
mmol/mol, plain regression → joint model.

### Instrument strength 1.0

| Hidden factor | Datasets | Plain → joint | Error removed | Sent to the worse drug | Coverage of 95% intervals | Link detected |
|---|---|---|---|---|---|---|
| Linear, 1 | First ten (report 08) | 3.77 → 0.95 | 75% | 34.8% → 16.5% | 13.6% → 91.9% | 7 of 10 |
| Linear, 1 | Second ten | 3.67 → 1.04 | 72% | 34.6% → 18.9% | 19.2% → 84.8% | 6 of 10 |
| Linear, 1 | All twenty | 3.72 → 1.00 | 73% | 34.7% → 17.7% | 16.4% → 88.4% | 13 of 20 |
| Threshold, 1 | First ten (report 08) | 2.91 → 1.06 | 64% | 28.2% → 16.4% | 33.9% → 91.5% | 4 of 10 |
| Threshold, 1 | Second ten | 2.75 → 0.87 | 68% | 27.7% → 17.8% | 37.7% → 86.8% | 5 of 10 |
| Threshold, 1 | All twenty | 2.83 → 0.97 | 66% | 28.0% → 17.1% | 35.8% → 89.2% | 9 of 20 |
| Effect, 1 | First ten (report 08) | 2.65 → 1.58 | 40% | 26.0% → 18.7% | 37.6% → 82.6% | 3 of 10 |
| Effect, 1 | Second ten | 2.55 → 1.55 | 39% | 25.9% → 20.2% | 40.5% → 77.3% | 2 of 10 |
| Effect, 1 | All twenty | 2.60 → 1.57 | 40% | 26.0% → 19.5% | 39.0% → 80.0% | 5 of 20 |
| Off | First ten (report 08) | 0.15 → 0.08 | none to remove | 10.2% → 13.4% | 94.0% → 93.9% | 0 of 10 |
| Off | Second ten | 0.10 → 0.20 | none to remove | 9.2% → 14.0% | 97.5% → 93.9% | 2 of 10 |
| Off | All twenty | 0.13 → 0.14 | none to remove | 9.7% → 13.7% | 95.8% → 93.9% | 2 of 20 |

### Instrument strength 0.5

| Hidden factor | Datasets | Plain → joint | Error removed | Sent to the worse drug | Link detected |
|---|---|---|---|---|---|
| Linear, 1 | First ten (report 08) | 4.10 → 2.28 | 44% | 36.5% → 23.7% | 2 of 10 |
| Linear, 1 | Second ten | 4.22 → 2.33 | 45% | 37.2% → 24.0% | 2 of 10 |
| Linear, 1 | All twenty | 4.16 → 2.31 | 45% | 36.8% → 23.9% | 4 of 20 |
| Threshold, 1 | First ten (report 08) | 3.25 → 2.29 | 30% | 30.5% → 23.6% | 0 of 10 |
| Threshold, 1 | Second ten | 3.30 → 1.99 | 40% | 30.8% → 22.0% | 2 of 10 |
| Threshold, 1 | All twenty | 3.27 → 2.14 | 35% | 30.6% → 22.8% | 2 of 20 |
| Effect, 1 | First ten (report 08) | 2.91 → 2.45 | 16% | 27.8% → 24.4% | 0 of 10 |
| Effect, 1 | Second ten | 3.04 → 2.35 | 23% | 28.4% → 23.7% | 0 of 10 |
| Effect, 1 | All twenty | 2.97 → 2.40 | 19% | 28.1% → 24.1% | 0 of 20 |
| Off | All twenty | 0.00 → 0.08 | none to remove | 11.4% → 15.6% | 1 of 20 |

"Link detected" counts the datasets in which the joint model's 95% interval
for rho excluded zero. Every setting, including the hidden factor at strength
0.5, is in the table file.

## Reading

1. **The result of report 08 holds.** With the strong instrument, the share
   of the error removed on the second ten datasets is within five points of
   the first ten for every form: 72% against 75% (linear), 68% against 64%
   (threshold), 39% against 40% (effect).

2. **The order of the forms holds.** Linear and threshold are corrected most,
   effect least, in both halves and at both instrument strengths.

3. **The weaker instrument still corrects about half as much.** At strength
   0.5 it removes 45% of the error for the linear form on all twenty
   datasets, against 73% at strength 1.0.

4. **The cost when nothing is hidden holds.** The joint model sends 13.7% of
   patients to the worse drug against the plain regression's 9.7%, over
   twenty datasets.

5. **One thing report 08 did not show: false alarms.** With nothing hidden,
   the first ten datasets gave no case where the joint model reported a link.
   The second ten gave two at instrument strength 1.0 and one at 0.5. Three
   in forty is 7.5%, close to the 5% that a 95% interval allows by chance.
   Report 08's "0 of 10" should not be read as "never".

6. **The joint model's intervals are slightly less honest than report 08
   suggested.** At instrument strength 1.0 and a linear hidden factor of
   strength 1, coverage was 91.9% on the first ten datasets and 84.8% on the
   second ten, 88.4% overall. Part of the bias remains, and the intervals do
   not fully account for it.

## Checks

- **Convergence.** The worst R-hat for any patient's effect in any of the 280
  new fits was 1.008.
- **No duplicates.** 280 rows for datasets 0 to 9 and 280 for datasets 10 to
  19, one row per model, dataset and setting.
- **Report 08's table is unchanged.** `scripts/11_summarise_step3.py` was run
  again with the new rows present and wrote the same file.

## Limits

- The limits of report 08 apply unchanged: an ideal instrument, one simple
  joint model, 5,000 patients per dataset, a hidden factor unrelated to every
  recorded feature.
- Twenty datasets per setting. The standard error of the joint model's
  average error is about 0.3 mmol/mol.
- The two halves were run a day apart at different code commits. The code
  that simulates these datasets and fits these models did not change between
  them.
