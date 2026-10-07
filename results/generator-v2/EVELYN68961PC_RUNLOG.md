# Run log: EVELYN68961PC (runner)

Runner for repeats 10 to 19 of the step 2 grid, generator version 2.
Times are local to this computer (UTC+08:00).

## Computer

- Name: EVELYN68961PC
- Processor: 11th Gen Intel Core i5-1135G7, 4 cores, 8 threads
- Memory: 15.7 GB in total; 3.7 GB free before the run
- Python 3.12.15, numpy 2.5.3, stochtree 0.4.5, uv 0.12.23
- The lead's computer (EVELYN68961) runs Python 3.12.13 with the same numpy and stochtree versions. The lead accepted the difference on 2026-10-07 and asked that it be recorded here.
- Sleep is switched off while the computer is on mains power, and it is on mains power.

## Before the run (2026-10-07)

- Code pulled to commit ca0b6ac. `docs/RUNNER.md` read in full.
- `uv sync`: 34 packages. One warning: the project asks for `uv-build>=0.11.26,<0.12.0` and the installed uv is 0.12.23. The package built and the tests ran.
- `uv run pytest`: 13 of 13 tests passed.
- `uv run python scripts/04_cross_check.py fingerprint`: 14 fingerprints saved.
- `uv run python scripts/04_cross_check.py compare`: computers EVELYN68961 and EVELYN68961PC, 14 datasets compared, 0 differ.

## The long run

- Command: `uv run python scripts/03_causal_forest_grid.py --repeats 10-19 --workers 2`
- Two workers instead of four, because only 3.7 GB of memory was free. The lead agreed.
- Approved by Evelyn in the runner session on 2026-10-07.

| Time | Event |
|---|---|
| 2026-10-07 15:01 | Fingerprints and this log committed and pushed (commit b468ead). |
| 2026-10-07 15:02 | Long run started. First line printed: `generator v2, code b468ead, computer EVELYN68961PC, repeats 10-19: 70 fits to run -> EVELYN68961PC.csv` |
| 2026-10-07 15:48 | Fits 1 and 2 of 70 finished (repeat 10: none 0.0, linear 0.5). They took 2,757 s and 2,774 s, about 46 minutes each. |
| 2026-10-07 16:05 | Hourly commit: 2 fits saved. Run continuing. |

## Unusual: fits are about eight times slower than on the lead's computer

- Each fit takes about 46 minutes here. `docs/RUNNER.md` expects 5 to 15 minutes, and the lead reports about 5.5 minutes.
- Measured at 16:03: each worker process had used 3,585 s of processor time in about 3,600 s of running, so each fit uses one core fully and no more. Total processor load was about 30% of 8 threads. The processor was running at 64% of its maximum frequency under the "ASUS Recommended" power plan.
- Each worker holds about 2.2 GB of memory. Free memory with two workers running: 4.0 GB.
- No error, no warning, no restart. Nothing was changed.
- At this speed, 70 fits with two workers take about 27 hours, ending around 18:00 on 2026-10-08.
- Reported to the lead and to Evelyn at 16:05. Waiting for the lead's decision on whether to keep this range, shorten it, or change the number of workers.
