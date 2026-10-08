# Report 10: less ideal instruments

**Date:** 2026-10-09
**Scripts:** `scripts/12_followup_runs.py --run realistic` (the run), `scripts/13_summarise_followups.py` (the table)
**Results:** `results/generator-v2/realistic/EVELYN68961.csv` (160 rows: two models × 80 datasets)
**Table:** `reports/tables/followup_realistic.csv`
**Code commit recorded in every row:** ca71a11

## Question

The instrument of report 08 is ideal: one independent value per patient, with
no effect on the outcome except through the choice of drug. A real instrument,
such as a practice's prescribing habit, is shared by all patients of a
practice, and may be slightly related to how its patients do. Does the joint
model still correct the bias?

## What was run

Four instruments, each of strength 1.0 on drug choice, beside the ideal one of
report 08:

| Name | What differs from the ideal instrument |
|---|---|
| `practice_100` | Patients are spread at random over 100 practices. The instrument is one value per practice (about 50 patients each). |
| `practice_25` | The same with 25 practices (about 200 patients each). |
| `flaw_0.5` | One value per patient, but it also acts on the outcome directly: 0.5 mmol/mol of HbA1c per SD of the instrument. |
| `flaw_1.0` | The same with 1.0 mmol/mol per SD. |

- The flaw breaks the one rule an instrument must obey. Its direction is the
  same as the hidden factor's: a higher value makes the GLP-1 drug more likely
  and the result worse.
- For scale, a typical fall in HbA1c on either drug is about 12 mmol/mol, and
  the unexplained spread of the outcome is 13 to 15 mmol/mol. A flaw of 1.0
  is small beside both.
- Hidden factor off, and linear at strength 1. Ten datasets each, with the
  same seeds as report 08. Plain regression and joint model, fitted as in
  report 08. The joint model is not told that an instrument is shared within
  a practice, or that it is flawed.

## Result

Averages across ten datasets. Errors in the average effect, in mmol/mol.

### Linear hidden factor at strength 1

| Instrument | Plain → joint | Error removed | Sent to the worse drug | Coverage of 95% intervals | Link detected |
|---|---|---|---|---|---|
| Ideal (report 08) | 3.77 → 0.95 | 75% | 34.8% → 16.5% | 13.6% → 91.9% | 7 of 10 |
| 100 practices | 3.90 → 0.82 | 79% | 36.3% → 15.3% | 14.0% → 92.8% | 8 of 10 |
| 25 practices | 3.77 → 0.65 | 83% | 34.4% → 14.5% | 16.8% → 89.2% | 8 of 10 |
| Flaw of 0.5 | 4.14 → 3.40 | 18% | 37.1% → 31.2% | 8.6% → 45.5% | 1 of 10 |
| Flaw of 1.0 | 4.51 → 5.90 | made worse | 39.4% → 44.0% | 5.2% → 6.7% | 3 of 10 |

### Nothing hidden

| Instrument | Plain → joint | Sent to the worse drug | Coverage of 95% intervals | Link reported, wrongly |
|---|---|---|---|---|
| Ideal (report 08) | 0.15 → 0.08 | 10.2% → 13.4% | 94.0% → 93.9% | 0 of 10 |
| 100 practices | −0.07 → −0.07 | 10.8% → 13.3% | 92.4% → 93.5% | 0 of 10 |
| 25 practices | −0.01 → −0.22 | 11.8% → 15.9% | 90.4% → 90.1% | 1 of 10 |
| Flaw of 0.5 | 0.57 → 2.32 | 11.4% → 23.8% | 91.4% → 67.9% | 5 of 10 |
| Flaw of 1.0 | 0.99 → 4.55 | 13.6% → 39.1% | 86.2% → 14.4% | 10 of 10 |

## Reading

1. **An instrument shared within a practice works as well as an ideal one.**
   With 100 or with 25 practices the joint model removes about 80% of the
   error, as it does with one value per patient. Sharing the instrument
   between patients is not, in this simulation, what limits the correction.

2. **A small flaw defeats the correction.** With a direct effect of 0.5
   mmol/mol per SD the joint model removes 18% of the error, against 75% with
   the ideal instrument. With 1.0 it does worse than the plain regression,
   which ignores the instrument altogether.

3. **A flawed instrument creates a bias where there was none.** With nothing
   hidden, the plain regression's error is 0.57 and 0.99; the joint model's is
   2.32 and 4.55. At a flaw of 1.0 the joint model sends 39% of patients to
   the worse drug, where the plain regression sends 14%.

4. **Why so small a flaw does so much.** The joint model reads the effect of
   the drug from how outcomes change as the instrument moves drug choice. One
   SD of the instrument changes the chance of the GLP-1 drug by roughly a
   fifth. So any direct effect of the instrument on the outcome is credited
   to the drug at about five times its size: 1.0 mmol/mol becomes an error of
   about 4.5, which is what the table shows.

5. **The model gives no warning, and its warning sign misleads.** With
   nothing hidden and a flaw of 1.0, it reports a link between drug choice
   and outcome in all ten datasets, with rho near −0.18. A reader would take
   that as evidence of a hidden factor and trust the corrected estimate more.
   Coverage of its intervals falls to 14%.

6. **The plain regression is hurt much less.** A flawed instrument that is
   left out of the outcome model acts as a weak extra confounder: errors of
   0.57 and 0.99 with nothing hidden.

## Checks

- **Convergence.** The worst R-hat for any patient's effect in any of the 160
  fits was 1.006.
- **The options change nothing else.** Two tests check that the flaw adds
  exactly its size times the instrument to the outcome, and that a
  practice-level instrument leaves the features, the hidden factor and every
  other simulated number as they were.
- **Earlier datasets are unchanged.** The 14 fingerprints of report 04 are
  identical after the generator change.

## Limits

- **The practices differ only in the instrument.** Real practices also differ
  in their patients and in how they treat them. A habit that goes with sicker
  patients is exactly the flaw tested here, so in practice the two issues come
  together.
- **The joint model ignores the grouping.** It treats 5,000 patients as
  independent. Its averages were not harmed here; whether its intervals are
  too narrow with few practices was not examined beyond the coverage shown.
- **One kind of flaw.** The instrument acts on the outcome directly. An
  instrument related to the hidden factor was not simulated; it would act in
  a similar way.
- **Two flaw sizes, one instrument strength.** The damage depends on the
  ratio of the flaw to how much the instrument moves drug choice, so a
  stronger instrument would tolerate a larger flaw.
- Ten datasets per setting. The limits of report 08 apply.
