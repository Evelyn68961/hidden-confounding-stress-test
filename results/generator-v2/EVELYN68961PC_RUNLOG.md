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
| 2026-10-07 16:03 | Hourly commit: 2 fits saved (commit bf0b09f). Slow speed reported to the lead and to Evelyn; see "Unusual" below. |
| 2026-10-07 16:04 | Run stopped on the lead's decision (processes ended with `taskkill`). The two fits in progress, repeat 10 threshold 0.5 and threshold 1.0, were about 16 minutes in and are lost. The two saved rows are intact. |
| 2026-10-07 16:05 | Run restarted with the new command below. First line printed: `generator v2, code bf0b09f, computer EVELYN68961PC, repeats 10-12: 19 fits to run -> EVELYN68961PC.csv` |

| 2026-10-07 17:02 | Fits 1 to 3 of 19 finished (repeat 10: threshold 1.0, linear 1.0, threshold 0.5), in 3,339 s, 3,341 s and 3,385 s: about 56 minutes each with three workers, against about 46 minutes with two. |
| 2026-10-07 17:05 | Hourly commit: 5 fits saved in total. Free memory 8.9 GB just after the workers started their next fits. No error or warning. |

| 2026-10-07 18:00 | Fits 4 to 6 of 19 finished (repeat 10: effect 0.5, effect 1.0; repeat 11: none 0.0), in 3,468 s, 3,470 s and 3,424 s. Repeat 10 is complete. |
| 2026-10-07 18:06 | Hourly commit: 8 fits saved in total. Free memory 8.1 GB. No error or warning. |

| 2026-10-07 18:59 | Fits 7 to 9 of 19 finished (repeat 11: threshold 0.5, linear 1.0, linear 0.5), in 3,512 s, 3,524 s and 3,536 s. |
| 2026-10-07 19:07 | Hourly commit: 11 fits saved in total. Free memory 7.3 GB. No error or warning. |

## Restart (2026-10-07 16:05)

- New command: `uv run python scripts/03_causal_forest_grid.py --repeats 10-12 --workers 3`
- Reason: a fit takes about 46 minutes on this computer against about 13 minutes on the lead's with four workers. The lead moved repeats 13 to 19 to its own computer so that both finish at about the same time. This computer must not run anything in repeats 13 to 19.
- Three workers because 8.2 GB of memory was free after the stop, and each worker holds about 2.2 GB. If free memory falls below about 1 GB, the lead's instruction is to stop and restart with two workers.
- Rows from the first start record code commit b468ead. Rows from the restart record bf0b09f. The two commits differ only by this computer's own result files.

## Unusual: fits are about eight times slower than on the lead's computer

- Each fit takes about 46 minutes here. `docs/RUNNER.md` expects 5 to 15 minutes, and the lead reports about 5.5 minutes.
- Measured at 16:03: each worker process had used 3,585 s of processor time in about 3,600 s of running, so each fit uses one core fully and no more. Total processor load was about 30% of 8 threads. The processor was running at 64% of its maximum frequency under the "ASUS Recommended" power plan.
- Each worker holds about 2.2 GB of memory. Free memory with two workers running: 4.0 GB.
- No error, no warning, no restart. Nothing was changed.
- At this speed, 70 fits with two workers take about 27 hours, ending around 18:00 on 2026-10-08.
- Reported to the lead and to Evelyn at 16:03. The lead decided to shorten this computer's range; see "Restart".
