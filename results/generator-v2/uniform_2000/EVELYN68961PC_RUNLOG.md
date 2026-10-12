# Run log: EVELYN68961PC (runner), uniform_2000 and forest_warmup_1000

Runner for two jobs requested by the lead session on 2026-10-12:

- **Job A, uniform:** `uv run python scripts/14_uniform_runs.py --workers 4`. 660 datasets (1,180 fits), 2,000 draws per chain. Results: `results/generator-v2/uniform_2000/EVELYN68961PC.csv`, one row per fit.
- **Job B, forest:** `uv run python scripts/03_causal_forest_grid.py --warmup 1000 --workers N`. 140 causal forest fits with a warm-up of 1,000 draws. Results: `results/generator-v2/forest_warmup_1000/EVELYN68961PC.csv`.

This one file covers both jobs. Times are local to this computer (UTC+08:00).

## Computer

- Name: EVELYN68961PC. 11th Gen Intel Core i5-1135G7, 4 cores, 8 threads. 15.7 GB memory.
- Libraries from `uv.lock` at commit 91a1180: pymc 6.3.2, pytensor 3.3.3, numba 0.67.0.
- No C compiler: every start prints "g++ not available, if using conda: `conda install gxx`". The lead said on 2026-10-12 that the laptop EVELYN68961 has the same set-up and that no compiler is to be installed, so the two computers use the same backend.
- The computer is in use by the author while the jobs run.

## Where things are

- Machine output of job A: `C:\Git\_logs\uniform_2000_Evelyn68961PC.log`
- Machine output of job B: `C:\Git\_logs\forest_warmup_1000_Evelyn68961PC.log`
- Both logs are outside the repository. Lines beginning `===` in them were written by the runner (started, restarted, stopped, exited).

## How to continue if the session that started the jobs has ended

Both commands continue where they left off. From the repository root:

1. `git status` must show no change under `src/`, `scripts/`, `pyproject.toml` or `uv.lock`.
2. Check which phase applies (see "Order of work") and start the job or jobs for that phase with the commands above.
3. Publish about every two hours: `git add results/generator-v2/uniform_2000/ results/generator-v2/forest_warmup_1000/`, commit, `git pull --rebase`, `git push`.

## Order of work (agreed with the lead, 2026-10-12 13:20)

1. Job A with 4 workers; job B with 1 worker. Stop job B at once if free memory goes under 0.5 GB.
2. When job A has finished 400 datasets: publish, stop job A, and give the computer to job B, with as many workers as memory allows while leaving 2 GB free.
3. When job B has finished all 140 fits: publish, and resume job A for the remaining 260 datasets.

## Timeline

### 2026-10-12

- 11:5x. `git pull` to ea46fe8, `uv sync`. Import check printed "ok" after the g++ warning. `--list` printed "660 datasets (1180 fits) left of 660 datasets".
- 12:05:10. Job A started with 4 workers on ea46fe8. The lead had asked for 6; the runner chose 4 because the processor was at 31% and 5.9 GB was free, with the author working on the computer. The lead agreed afterwards.
- About 12:06. The lead's second message asked for job B, which needs commit 91a1180. That commit changes `src/stresstest/causal_forest.py`. The runner stopped job A (no dataset finished, nothing written), pulled, ran `uv sync`, and restarted it, so that the commit recorded in each row matches the code on disk. The lead's reply asking not to interrupt job A arrived after this.
- 12:07:34. Job A restarted with 4 workers on 91a1180. Job B started with 2 workers (the lead had suggested 3; free memory was 5.1 GB). Job B printed "140 fits to run".
- 13:17. Job A: 6 datasets done. Wall time per dataset on one worker: 2162, 2165, 2170, 2172, 1901, 1916 s (two fits each), so about 950 to 1,090 s per fit. PyMC "Sampling ... took" lines: n=14, min 496 s, median 528 s, max 992 s. Estimate at this rate: 1,180 fits in about 82 hours; the first 400 datasets (720 fits) in about 50 hours.
- 13:17. Memory: 1.2 GB free. Python held 7.2 GB: the two forest workers 2.17 and 2.22 GB, the four uniform workers 0.46 to 0.95 GB.
- 13:22:55. Free memory fell to 491 MB. Job B stopped under the 0.5 GB rule. It had run for 75 minutes and no forest fit had finished, so both fits in progress were lost. Job A was not touched. Free memory after the stop: 5.0 GB.
- 13:23:16. Job B restarted with 1 worker. A watcher stops it again under 0.5 GB free and records the lowest free memory seen.

## Open points

- Peak memory of one forest worker with `--warmup 1000` is not known yet; it was above 2.2 GB and still growing when job B was stopped.
- Minutes per forest fit: not known yet; no fit has finished.

### 2026-10-12, 14:46: job B stopped a second time and left stopped

- 14:44. With job B on 1 worker and job A on 4, free memory fell to 279 MB (lowest seen), 530 MB when checked.
- The single forest worker was at 3.1 GB working set and 4.0 GB private memory after 81 minutes, and had not finished its first fit.
- The four uniform workers had grown to 0.91, 1.00, 1.41 and 1.70 GB (they were 0.46 to 0.95 GB at 13:17).
- 14:46:01. Job B stopped under the 0.5 GB rule. Under the agreed order of work it now stays stopped until phase 2. Job A was not touched.
- Free memory after the stop: 3.8 GB. After the first stop at 13:23 it was 5.0 GB, so job A's workers hold about 1.2 GB more than 80 minutes earlier.
- Job A at 14:44: 18 datasets done of 660. Datasets with one fit take about 670 to 680 s; datasets with two fits about 1,900 to 2,300 s.
- First results published to GitHub after this entry.

## Open points (updated 14:46)

- A forest fit with `--warmup 1000` has never finished on this computer: 75 minutes with 2 workers and 81 minutes with 1 worker were not enough, and one worker needs more than 4 GB. Phase 2 cannot assume several forest workers on 15.7 GB.
- Job A's workers grow over time. If that continues, job A alone may reach the memory limit; a watcher now fires under 0.8 GB free.

### 2026-10-12, 15:05: planned restart of job A on c0c56a8

- The lead found the cause of job A's growing memory: worker processes lived for the whole run. Commit c0c56a8 starts a fresh worker process for every dataset (one changed line in `scripts/14_uniform_runs.py`).
- 15:05:35. A dataset was saved (34 rows, 19 datasets). Job A stopped at that moment; the other three fits in progress will be redone.
- `git pull` to c0c56a8. 15:05:59. Job A restarted with 4 workers. It printed "641 datasets (1146 fits) to run". Rows from here on record c0c56a8.
- 15:07. The four new workers were at 333 to 356 MB each. Free memory 7.1 GB (it was 3.8 GB before the restart).
- Job B remains stopped until phase 2. The lead confirmed that more than 4 GB per forest fit is expected, and asked for 2 forest workers in phase 2, 3 only if memory allows.

## Open points (updated 15:07)

- Confirm at the next check that job A's workers fall back to a few hundred MB each time a dataset finishes.
- Minutes per forest fit with `--warmup 1000`: still unknown; no fit has finished on this computer.

### 2026-10-12, 17:31: check

- Job A: 27 datasets done of 660 (50 fit rows). Since the 15:06 restart: 8 datasets, at 1273, 1331, 1465, 3188, 3265, 1617, 1507 and 1497 s. The two slow ones were both `no_instrument` (none 0.0 repeat 1; linear 1.0 repeat 1).
- The fresh-worker change works for ordinary datasets: two workers started at 17:12 and 17:15 hold 1.0 GB working set (1.6 GB private).
- Two workers started at 15:06 are still on their first dataset after 145 minutes, at 3.0 GB working set and 3.88 GB private memory each. The log does not say which datasets they are. No error in the log.
- Memory: free physical 0.62 GB; free commit 4.55 GB of 31.2 GB; page file 1.4 GB in use.
- The lead was asked whether this is expected and whether to drop to 3 workers. The lead's session was offline at the time; the message is queued.
- Rule until the lead answers: if free commit goes under 1.5 GB, stop job A and restart it with 3 workers.
- The scheduled 16:17 check did not fire in the runner's session; this entry and the publish after it were done by hand.
- Job B remains stopped.
