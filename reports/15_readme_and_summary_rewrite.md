# 15. README and summary rewritten to match the slide deck

**Date:** 2026-10-12. **Kind:** text only. No code, result file or earlier
report was changed, and nothing was refitted.

## Why

A 22-slide deck of these results was sent to a reader on 2026-10-12. The
README still showed the tables of the first joint model, which reports 13 and
14 had superseded, and it used different words from the deck for the same
quantities. A reader going from the slides to the README would have met
different numbers.

## What changed

| File | Change |
|---|---|
| `README.md` | Rewritten in the order of the deck. Every joint-model number is from the corrected model (reports 13 and 14). Status changed to "preliminary results". |
| `reports/SUMMARY.md` | Rewritten as eleven findings in the same order and terms, with a section on how the joint-model findings changed. |
| `reports/README.md` | One sentence: SUMMARY.md now covers all the reports. |
| `results/README.md` | One row for the uniform run in progress (`uniform_2000`). |

## Terms

| Before | Now |
|---|---|
| Error in the average effect | Bias |
| (not reported) | RMSE of the average effect |
| 95% intervals containing the truth | Coverage |
| Patients sent to the worse drug | Misclassification rate |

The column "typical error per patient" was dropped from the README. It is
still in `reports/tables/step2_causal_forest.csv` and in report 03.

## Statements removed because they were not measured

- "Nothing in its output signals the problem." The scores record how often
  the intervals contain the truth, and nothing else about them.
- "Honest" as a description of intervals.
- "The hardest case" for a hidden factor unrelated to every recorded feature.
  No run used a hidden factor related to the features.

## Checks

- Every bias, RMSE, coverage and misclassification figure in the README was
  recomputed from the per-dataset files in `results/generator-v2/` by an
  independent check on 2026-10-12, with no mismatch.
- One figure in report 14 differs from the data in its last digit: it prints
  −0.04 for the practice-level instrument with 100 practices and no hidden
  factor, and the data give −0.035. The README shows −0.03. Report 14 is left
  as it was written.

## Number of datasets behind each README table

| Table | Datasets per setting |
|---|---|
| Causal forest | 20 |
| Joint model, ideal instrument, strength 1 and 0.5 | 20 |
| Joint model, no instrument | 10 |
| Less-than-ideal instruments, with and without a hidden factor | 20 for the ideal row, 10 for the others |
| Instrument as a feature | 10 |

The uniform run (script 14) will bring every setting to 20.

## The next step named in the README

Allow ρ to differ by drug (an endogenous switching regression). In the effect
shape the hidden factor acts on the outcome of GLP-1 patients only, and the
joint model has one ρ for both drugs. This is a reading of the code. No run
has tested it.
