# Report 04: do the two computers agree?

**Date:** 2026-10-07
**Script:** `scripts/04_cross_check.py`
**Files:** `results/generator-v2/crosscheck/`
**Rules for the second computer:** `docs/RUNNER.md`. Its own account of the
run is `results/generator-v2/EVELYN68961PC_RUNLOG.md`.

## Question

The step 2 fits were shared between two computers by repeat number. If the
computers differed in some hidden way, it would look like a difference between
ranges of repeats and nothing would reveal it. Do the two computers simulate
the same patients, and does the sampler give the same answer on both?

## The two computers

| | Lead: `EVELYN68961` | Second: `EVELYN68961PC` |
|---|---|---|
| Processor | Intel, family 6 model 189 | Intel Core i5-1135G7 (family 6 model 140) |
| Python | 3.12.13 | 3.12.15 |
| numpy | 2.5.3 | 2.5.3 |
| stochtree | 0.4.5 | 0.4.5 |
| Repeats run | 0 to 9 and 13 to 19 (119 fits) | 10 to 12 (21 fits) |

The second computer was first given repeats 10 to 19. Each fit there took
about 46 minutes against about 13 on the lead computer, so after two fits its
range was cut to 10 to 12 and the lead computer took 13 to 19. Only the
allocation of repeats changed.

## Check 1: are the simulated patients identical?

Each computer simulated the same 14 datasets (all seven settings of repeats 0
and 10) and saved a SHA-256 hash of the features, the treatment and the
outcome.

**Result: 14 datasets compared, 0 differ.** This was done before the long run
started on the second computer.

## Check 2: does the sampler give the same answer?

The lead computer refitted three datasets from the second computer's repeat 10
and compared the scores with the second computer's own fits.

| Dataset | Typical error per patient: lead / second | Sent to the worse drug: lead / second | Verdict |
|---|---|---|---|
| Hidden factor off, repeat 10 | 1.5477 / 1.5477 | 13.60% / 13.60% | identical |
| Linear, strength 1, repeat 10 | 5.6914 / 5.6914 | 45.92% / 45.92% | identical |
| Effect, strength 1, repeat 10 | 4.4340 / 4.4340 | 38.68% / 38.68% | identical |

"Identical" means all five scores agree to within 0.000000001.

The mirror-image check (the second computer refitting three of the lead's
datasets) was cancelled. It would have tested the same pair of computers
running the same code, at a cost of about two and a half hours.

## Check 3: scores by computer

Typical error per patient, mean (SD across repeats):

| Setting | Lead (n = 17) | Second (n = 3) |
|---|---|---|
| Hidden factor off | 1.86 (0.25) | 1.60 (0.14) |
| Linear, 0.5 | 2.16 (0.49) | 2.52 (0.29) |
| Linear, 1 | 4.75 (0.43) | 5.04 (0.69) |
| Threshold, 0.5 | 1.99 (0.47) | 2.27 (0.29) |
| Threshold, 1 | 3.94 (0.45) | 4.16 (0.74) |
| Effect, 0.5 | 2.00 (0.43) | 2.28 (0.31) |
| Effect, 1 | 3.67 (0.39) | 3.85 (0.67) |

The two computers ran different repeats, so these means differ by chance. With
three repeats on the second computer, a difference of about 0.3 is well within
what the spreads allow. Given check 2, any difference here comes from which
datasets each computer happened to run, not from the computers.

## Reading

- The two computers simulate identical patients and produce identical fits
  from them, despite different processors and different Python patch versions.
- The 140 fits can be pooled as one experiment.
- The results are reproducible across machines to the last printed digit, at
  least for this pair.

## How the results were kept apart

- Each computer wrote only a file named after itself.
- Results are filed by generator version, and every row records the generator
  version, the computer and the code commit.
- The fitting script refuses to run on uncommitted code.
- The summary script refuses mixed generator versions and refuses any dataset
  that appears twice. On the final 140 rows it reported neither.
- The 24 fits from the stopped first run (generator version 1) are kept under
  `results/generator-v1/` and are used nowhere.

## Limits

- One pair of computers, both Windows, both Intel. A different operating
  system or processor family was not tested.
- Three datasets were refitted, not all of them.
