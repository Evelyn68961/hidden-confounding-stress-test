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

### 2026-10-12, 18:16 to 18:30: the long fits explained; plan revised

- 18:16. One of the two long fits finished: `no_instrument_20000 linear strength 1.0 repeat 0`, 11,333 s (3 h 9 min). The long fits are the 20,000-patient datasets, not stuck fits. Free memory after it finished: 5.0 GB physical, 8.9 GB commit. Lowest free commit seen: 4.57 GB.
- Job A: 32 datasets done of 660. Ordinary two-fit datasets take about 1,270 to 1,620 s on c0c56a8.
- From the lead (18:30): 40 of the 660 datasets are 20,000-patient ones, two per repeat, adjacent in the list, all inside the first 400. Each needs about 3.2 hours and 3.9 GB. Keep 4 workers. Only if free commit goes under 1.5 GB: stop job A and restart with 3 workers.
- The lead's estimate for the first 400 datasets: about 270 worker-hours, close to 3 days with 4 workers.
- Job B (forest) now waits for the author's decision. It is not to be started without word from the lead.

## Order of work (revised 18:30; replaces the earlier list)

1. Job A with 4 workers until the first 400 datasets are done; then tell the lead and publish.
2. What follows (forest refit, or straight on with the remaining 260 datasets) depends on the lead's word. Without one, job A simply continues.

### 2026-10-12, evening: the forest refit is kept

- The lead passed on the author's decision: the forest refit with warm-up 1,000 is kept.

## Order of work (final, replaces the lists above)

1. Job A with 4 workers until the first 400 datasets are done. Only if free commit goes under 1.5 GB: stop and restart with 3 workers.
2. Then tell the lead, publish, stop job A right after a dataset is saved, and start job B with 2 workers (3 only if memory allows). Report the time and peak memory of the first two forest fits to the lead.
3. When all 140 forest fits are done: tell the lead, publish, and resume job A for the remaining 260 datasets.

### 2026-10-12, 21:27: check

- Job A: 48 datasets done of 660 (88 fit rows of 1,180). [29/641] since the 15:06 restart. No error in the log.
- Recent ordinary datasets: 1,647 to 1,851 s. Two 20,000-patient fits have been running since 18:27 and 18:28 (2.8 and 2.1 GB working set).
- Memory: free physical 1.7 GB; free commit 4.7 GB.
- The scheduled checks at 18:17 and 20:17 did not fire; this entry and the publish after it were done by hand.
- Job B waits for the first 400 datasets.

### 2026-10-12, 23:30: check

- Job A: 59 datasets done of 660 (106 fit rows of 1,180). [40/641] since the 15:06 restart. No error in the log.
- Memory at 23:29: free physical 3.1 GB; free commit 2.6 GB; lowest free commit in the last two hours 2.2 GB (the limit for dropping to 3 workers is 1.5 GB).
- Processes at 23:30: workers: 1939MB/3880MB private, started 22:29; 1772MB/3880MB private, started 22:36; 1643MB/3880MB private, started 18:28; 407MB/1214MB private, started 23:27; 24MB/276MB private, started 15:06; 9MB/4MB private, started 15:06
- Checks are now driven by a two-hour timer inside the runner's watcher, because the scheduled checks never fired.

### 2026-10-13, 01:31: check

- Job A: 66 datasets done of 660 (120 fit rows of 1,180). [47/641] since the 15:06 restart. No error in the log.
- The repeat 1 linear 20,000-patient fit finished after 18,680 s (5 h 11 min); it overlapped with two other long fits. Long fits so far: 11,333, 11,481, 12,015 and 18,680 s.
- Running: the repeat 2 pair of long fits (started 22:29 and 22:36, 3.88 GB private each) and two ordinary workers.
- Memory: free physical 1.5 GB; free commit 5.7 GB; lowest free commit in the last two hours 2.5 GB.

### 2026-10-13, 03:35: check

- Job A: 77 datasets done of 660 (138 fit rows of 1,180). [58/641] since the 15:06 restart. No error in the log.
- Five 20,000-patient fits done so far (the latest: repeat 2, hidden factor off, 12,100 s). The repeat 2 linear fit, started 22:36, is still running after 5 hours. Two more long fits started at 03:04 and 03:23 (the repeat 3 pair).
- Memory: free physical 2.6 GB; free commit 5.4 GB; lowest free commit in the last two hours 4.9 GB.
- 02:1x. Pulled the lead's text-only commit d2cf152 with rebase (README and report files only; nothing under `src/` or `scripts/`), and published as d6a9f80. The run was not restarted.

### 2026-10-13, 05:40: check

- Job A: 82 datasets done of 660 (148 fit rows of 1,180). [63/641] since the 15:06 restart. No error in the log.
- Six 20,000-patient fits done. The repeat 2 linear fit took 18,405 s (5 h 7 min). The repeat 3 pair (started 03:04 and 03:23) is running, with two ordinary workers.
- Memory: free physical 1.5 GB; free commit 4.6 GB; lowest free commit in the last two hours 4.0 GB.
- Measured rate: about 80 datasets (four repeats of the first block) in the 17.5 hours since 12:07 on 12 October, so about 4.4 hours per repeat. At that rate the first 400 datasets (20 repeats) need about 88 hours in all, ending around 04:00 on 16 October. This is slower than the lead's estimate of about 3 days. Reported to the lead.

### 2026-10-13, 07:43: check

- Job A: 98 datasets done of 660 (176 fit rows of 1,180). No error in the log.
- Running workers: 2595 MB private, started 07:32; 2596 MB private, started 07:37; 1215 MB private, started 07:37; 705 MB private, started 07:42. Free physical 5.6 GB; free commit 8.3 GB. Lowest free commit in the last two hours: 4497 MB.

### 2026-10-13, 09:46: check

- Job A: 104 datasets done of 660 (188 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 07:32; 3878 MB private, started 07:37; 1097 MB private, started 09:35; 817 MB private, started 09:21. Free physical 2.6 GB; free commit 5.8 GB. Lowest free commit in the last two hours: 4633 MB.

### 2026-10-13, 11:50: check

- Job A: 119 datasets done of 660 (214 fit rows of 1,180). No error in the log.
- Running workers: 3212 MB private, started 11:21; 3211 MB private, started 11:24; 1588 MB private, started 11:29; 691 MB private, started 11:49. Free physical 1.8 GB; free commit 6.7 GB. Lowest free commit in the last two hours: 4681 MB.

### 2026-10-13, 13:54: check

- Job A: 126 datasets done of 660 (228 fit rows of 1,180). No error in the log.
- Running workers: 3882 MB private, started 11:24; 3879 MB private, started 11:21; 1588 MB private, started 13:39; 1092 MB private, started 13:43. Free physical 1.3 GB; free commit 5 GB. Lowest free commit in the last two hours: 4612 MB.

### 2026-10-13, 15:58: check

- Job A: 140 datasets done of 660 (252 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 15:08; 3880 MB private, started 15:09; 1587 MB private, started 15:39; 1214 MB private, started 15:52. Free physical 3.7 GB; free commit 5 GB. Lowest free commit in the last two hours: 4609 MB.

### 2026-10-13, 18:01: check

- Job A: 147 datasets done of 660 (266 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 15:08; 3880 MB private, started 15:09; 1588 MB private, started 17:49; 1123 MB private, started 17:51. Free physical 2 GB; free commit 4.9 GB. Lowest free commit in the last two hours: 4658 MB.

### 2026-10-13, 20:00: check

- Job A: 156 datasets done of 660 (280 fit rows of 1,180). No error in the log.
- Running workers: 3272 MB private, started 15:08; 3879 MB private, started 19:23; 3881 MB private, started 19:23; 3880 MB private, started 15:09. Free physical 3.3 GB; free commit 0.7 GB. Lowest free commit in the last two hours: 759 MB.

### 2026-10-13, 19:59 to 20:32: commit limit reached; job A restarted with 3 workers

- 19:59. Free commit fell to 759 MB (limit 1.5 GB). Four 20,000-patient fits were running at once: the repeat 6 pair (started 15:08 and 15:09) and the repeat 7 pair (started 19:23). Each held 3.88 GB private memory. No error in the log.
- The runner did not stop at once, because the repeat 6 pair was about five hours in. A watcher checked every 20 seconds, with an immediate stop set for free commit under 300 MB or any error.
- About 20:00 and 20:29. The repeat 6 pair finished and was saved: 17,528 s (hidden factor off) and 19,207 s (linear). Lowest free commit while waiting: 2.4 GB.
- 20:31:09. Job A stopped, as the rule requires. Lost: the repeat 7 pair of long fits (67 minutes in) and two ordinary datasets a few minutes in. 159 datasets done at the stop.
- Job A restarted with 3 workers (see the next line of the machine log for the time). With 3 workers at most three long fits can overlap (about 11.6 GB).
- Note on the `code_commit` column: rows written from here on record the repository HEAD at this restart, which is a results-only commit made by this runner on top of the lead's text-only commit d2cf152. Nothing under `src/` or `scripts/` differs from c0c56a8.

### 2026-10-13, 22:35: check

- Job A (3 workers): 163 datasets done of 660 (294 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 20:31; 3878 MB private, started 20:31; 1585 MB private, started 22:10. Free physical 3.1 GB; free commit 6.1 GB. Lowest free commit in the last two hours: 6205 MB.

### 2026-10-14, 00:39: check

- Job A (3 workers): 169 datasets done of 660 (306 fit rows of 1,180). No error in the log.
- Running workers: 3878 MB private, started 20:31; 3270 MB private, started 20:31; 1588 MB private, started 00:28. Free physical 2 GB; free commit 6.6 GB. Lowest free commit in the last two hours: 6211 MB.

### 2026-10-14, 02:43: check

- Job A (3 workers): 179 datasets done of 660 (322 fit rows of 1,180). No error in the log.
- Running workers: 3881 MB private, started 01:30; 3880 MB private, started 01:34; 1439 MB private, started 02:16. Free physical 2.4 GB; free commit 6 GB. Lowest free commit in the last two hours: 5954 MB.

### 2026-10-14, 04:44: check

- Job A (3 workers): 183 datasets done of 660 (330 fit rows of 1,180). No error in the log.
- Running workers: 3881 MB private, started 01:30; 3880 MB private, started 01:34; 1584 MB private, started 04:30. Free physical 1.4 GB; free commit 6 GB. Lowest free commit in the last two hours: 5036 MB.

### 2026-10-14, 06:48: check

- Job A (3 workers): 199 datasets done of 660 (358 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 06:15; 3880 MB private, started 06:16; 1603 MB private, started 06:34. Free physical 3.5 GB; free commit 5.9 GB. Lowest free commit in the last two hours: 6075 MB.

### 2026-10-14, 08:51: check

- Job A (3 workers): 204 datasets done of 660 (368 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 06:15; 3881 MB private, started 06:16; 1213 MB private, started 08:47. Free physical 1.3 GB; free commit 6.4 GB. Lowest free commit in the last two hours: 6058 MB.

### 2026-10-14, 10:53: check

- Job A (3 workers): 215 datasets done of 660 (389 fit rows of 1,180). No error in the log.
- Running workers: 1215 MB private, started 10:50; 1215 MB private, started 10:51; 1215 MB private, started 10:52. Free physical 5.7 GB; free commit 10.6 GB. Lowest free commit in the last two hours: 6248 MB.

### 2026-10-14, 12:54: check

- Job A (3 workers): 222 datasets done of 660 (400 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 11:06; 3880 MB private, started 11:04; 1585 MB private, started 12:24. Free physical 1.7 GB; free commit 5.9 GB. Lowest free commit in the last two hours: 5852 MB.

### 2026-10-14, 14:57: check

- Job A (3 workers): 233 datasets done of 660 (422 fit rows of 1,180). No error in the log.
- Running workers: 1371 MB private, started 14:49; 1588 MB private, started 14:48; 1215 MB private, started 14:55. Free physical 5.8 GB; free commit 11.1 GB. Lowest free commit in the last two hours: 6112 MB.

### 2026-10-14, 16:58: check

- Job A (3 workers): 242 datasets done of 660 (436 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 15:06; 3880 MB private, started 15:10; 1585 MB private, started 16:31. Free physical 1.9 GB; free commit 5.8 GB. Lowest free commit in the last two hours: 5366 MB.

### 2026-10-14, 19:00: check

- Job A (3 workers): 246 datasets done of 660 (444 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 15:10; 1588 MB private, started 18:42; 1215 MB private, started 18:54. Free physical 2.5 GB; free commit 8 GB. Lowest free commit in the last two hours: 5663 MB.

### 2026-10-14, 21:01: check

- Job A (3 workers): 259 datasets done of 660 (466 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 20:13; 3880 MB private, started 20:17; 1588 MB private, started 20:48. Free physical 3.5 GB; free commit 5.8 GB. Lowest free commit in the last two hours: 5949 MB.

### 2026-10-14, 23:04: check

- Job A (3 workers): 263 datasets done of 660 (474 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 20:13; 3880 MB private, started 20:17; 1584 MB private, started 22:54. Free physical 1.3 GB; free commit 5.7 GB. Lowest free commit in the last two hours: 4373 MB.

### 2026-10-15, 01:07: check

- Job A (3 workers): 280 datasets done of 660 (504 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 00:14; 3881 MB private, started 00:15; 1214 MB private, started 01:03. Free physical 3.1 GB; free commit 6.1 GB. Lowest free commit in the last two hours: 5803 MB.

### 2026-10-15, 03:11: check

- Job A (3 workers): 285 datasets done of 660 (514 fit rows of 1,180). No error in the log.
- Running workers: 1585 MB private, started 02:32; 1588 MB private, started 02:57; 577 MB private, started 03:10. Free physical 6.5 GB; free commit 11.3 GB. Lowest free commit in the last two hours: 5943 MB.

### 2026-10-15, 05:14: check

- Job A (3 workers): 300 datasets done of 660 (540 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 04:24; 3881 MB private, started 04:27; 1371 MB private, started 05:08. Free physical 3.4 GB; free commit 5.5 GB. Lowest free commit in the last two hours: 5380 MB.

### 2026-10-15, 07:17: check

- Job A (3 workers): 308 datasets done of 660 (556 fit rows of 1,180). No error in the log.
- Running workers: 1587 MB private, started 07:04; 1588 MB private, started 07:08; 747 MB private, started 07:17. Free physical 6.6 GB; free commit 11.1 GB. Lowest free commit in the last two hours: 5443 MB.

### 2026-10-15, 09:21: check

- Job A (3 workers): 321 datasets done of 660 (578 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 07:56; 3881 MB private, started 07:57; 1589 MB private, started 09:02. Free physical 3 GB; free commit 5.7 GB. Lowest free commit in the last two hours: 5318 MB.

### 2026-10-15, 11:23: check

- Job A (3 workers): 323 datasets done of 660 (582 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 07:56; 3881 MB private, started 07:57; 1435 MB private, started 10:05. Free physical 2.1 GB; free commit 5.8 GB. Lowest free commit in the last two hours: 3790 MB.

### 2026-10-15, 13:26: check

- Job A (3 workers): 339 datasets done of 660 (610 fit rows of 1,180). No error in the log.
- Running workers: 3213 MB private, started 13:03; 3879 MB private, started 12:57; 1215 MB private, started 13:21. Free physical 2.9 GB; free commit 6.7 GB. Lowest free commit in the last two hours: 5850 MB.

### 2026-10-15, 15:27: check

- Job A (3 workers): 342 datasets done of 660 (616 fit rows of 1,180). No error in the log.
- Running workers: 3879 MB private, started 12:57; 3879 MB private, started 13:03; 1585 MB private, started 15:12. Free physical 1.7 GB; free commit 4.7 GB. Lowest free commit in the last two hours: 4277 MB.

### 2026-10-15, 17:30: check

- Job A (3 workers): 344 datasets done of 660 (620 fit rows of 1,180). No error in the log.
- Running workers: 3879 MB private, started 13:03; 1585 MB private, started 16:28; 1588 MB private, started 17:15. Free physical 3.1 GB; free commit 7.1 GB. Lowest free commit in the last two hours: 4105 MB.

### 2026-10-15, 19:31: check

- Job A (3 workers): 358 datasets done of 660 (644 fit rows of 1,180). No error in the log.
- Running workers: 3211 MB private, started 19:13; 2005 MB private, started 19:07; 1438 MB private, started 19:14. Free physical 2.5 GB; free commit 8.4 GB. Lowest free commit in the last two hours: 7240 MB.

### 2026-10-15, 21:34: check

- Job A (3 workers): 367 datasets done of 660 (662 fit rows of 1,180). No error in the log.
- Running workers: 3881 MB private, started 19:13; 1371 MB private, started 21:29; 1215 MB private, started 21:30. Free physical 4.2 GB; free commit 8.7 GB. Lowest free commit in the last two hours: 5954 MB.

### 2026-10-15, 23:37: check

- Job A (3 workers): 380 datasets done of 660 (684 fit rows of 1,180). No error in the log.
- Running workers: 3880 MB private, started 22:47; 3879 MB private, started 22:47; 1214 MB private, started 23:36. Free physical 4.5 GB; free commit 6.3 GB. Lowest free commit in the last two hours: 6166 MB.

### 2026-10-16, 01:41: check

- Job A (3 workers): 383 datasets done of 660 (690 fit rows of 1,180). No error in the log.
- Running workers: 3879 MB private, started 22:47; 3880 MB private, started 22:47; 1583 MB private, started 01:21. Free physical 1.9 GB; free commit 6 GB. Lowest free commit in the last two hours: 6083 MB.

### 2026-10-16, 03:43: check

- Job A (3 workers): 392 datasets done of 660 (708 fit rows of 1,180). No error in the log.
- Running workers: 1588 MB private, started 03:21; 1588 MB private, started 03:28; 753 MB private, started 03:42. Free physical 5.5 GB; free commit 10.7 GB. Lowest free commit in the last two hours: 6035 MB.

### 2026-10-16, 04:44: check

- Job A (3 workers): 400 datasets done of 660 (720 fit rows of 1,180). No error in the log.
- Running workers: . Free physical 8 GB; free commit 15.5 GB. Lowest free commit in the last two hours:  MB.

### 2026-10-16, 04:44: phase 2 begins

- 04:43:29: the 400th dataset was saved (720 fit rows). 04:44:05: job A stopped by the runner. Work in progress and lost: two `no_instrument_20000` fits started 03:58 and 03:59, and one regular fit started 04:42; they will be redone in phase 3. The 260 datasets left therefore include those two 20,000-patient datasets.
- The check above shows "Running workers: ." because job A had already stopped. The `=== exited` line it counted is the runner's own stop, not an error.
- 04:44:52: job B started alone, 2 workers, `--warmup 1000`, code label 280e27f. `git diff --stat c0c56a8 HEAD -- src scripts pyproject.toml uv.lock` is empty. Rule: stop job B if free physical memory goes under 0.5 GB.

### 2026-10-16, 05:32: first two forest fits saved

- Job B (2 workers): fit 1 (linear, strength 0.5, repeat 0) took 2,687 s; fit 2 (none, strength 0.0, repeat 0) took 2,783 s. Both saved by 05:32.
- Peak private memory of one worker: 5,131 MB. Lowest free physical memory since the start at 04:44: 703 MB (the stop rule is 500 MB). Free physical 8.3 GB and free commit 13.6 GB at 05:32.

### 2026-10-16, 06:18: forest stopped for memory, restarted with 1 worker

- 06:18:52: the runner's watcher stopped job B because free physical memory was 381 MB (rule: stop under 500 MB). Two fits in progress since about 05:32 were lost. Two fits are saved.
- Afterwards, with job B stopped, nothing else large was running (VS Code about 1.6 GB, all other programs smaller). Two forest workers at about 5.1 GB each, plus about 4 GB for Windows and other programs, fill the 15.7 GB of this computer.
- 06:20: job B restarted with 1 worker, following order of work item 2 (as many workers as memory allows). `git diff --stat c0c56a8 HEAD -- src scripts pyproject.toml uv.lock` is empty; code label 50d272b.

### 2026-10-16, 08:20: check

- Job B (1 worker): 6 forest fits saved of 140. The four fits since the 06:19 restart took 1,468 to 1,556 s each (about 25 minutes), so one worker alone saves fits as fast as two workers in parallel did (about 46 minutes each). No error in the log.
- Peak private memory of the worker: 5,141 MB. Lowest free physical memory in the last two hours: 3,689 MB. Free commit at 08:20: 12.3 GB.

### 2026-10-16, 10:22: check

- Job B (1 worker): 8 forest fits saved of 140. No error in the log. The two fits since the last check took 3,811 s and 4,010 s, against about 1,500 s for the four before. The lowest free physical memory, 2,486 MB, suggests other programs were in use on the computer at the same time.
- Peak private memory of the worker: 5,161 MB. Free physical 6.6 GB and free commit 13.1 GB at 10:22.

### 2026-10-16, 12:23: check

- Job B (1 worker): 10 forest fits saved of 140. No error in the log. Fits since about 08:30 take 3,600 to 4,000 s, against about 1,500 s before.
- Cause found: four Stan chains from another project (`C:\ics_stan_build\engine_locked_v2_benefit_triple_dose.exe`, the latest set started 12:00) each use a full processor thread, so the forest worker shares the 4 cores. They are not part of this run, and the runner leaves them alone.
- Peak private memory of the worker: 5,167 MB. Lowest free physical memory in the last two hours: 2,625 MB. Free commit 14.0 GB at 12:23.

### 2026-10-16, 14:25: check

- Job B (1 worker): 11 forest fits saved of 140. No error in the log. One fit saved in the last two hours (3,840 s). Stan chains from the other project are still running (a new set of three started 13:56).
- Peak private memory of the worker: 6,092 MB, higher than the 5.1 GB seen before. Lowest free physical memory in the last two hours: 1,834 MB. Free commit 11.0 GB at 14:25.

### 2026-10-16, 16:26: check

- Job B (1 worker): 13 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,228 s and 3,566 s). At 16:26 no Stan chains from the other project were running.
- Peak private memory of the worker: 5,168 MB. Lowest free physical memory in the last two hours: 2,419 MB. Free commit 10.5 GB at 16:26.

### 2026-10-16, 18:27: check

- Job B (1 worker): 15 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,037 s and 4,387 s). Four Stan chains from the other project (`engine_locked_v2_benefit_triple_dose_refclass.exe`) started at 18:23.
- Peak private memory of the worker: 5,168 MB. Lowest free physical memory in the last two hours: 2,522 MB. Free commit 11.4 GB at 18:27.

### 2026-10-16, 20:29: check

- Job B (1 worker): 17 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,001 s and 4,101 s). At 20:29 no Stan chains from the other project were running.
- Peak private memory of the worker: 5,180 MB. Lowest free physical memory in the last two hours: 2,264 MB. Free commit 12.3 GB at 20:29.

### 2026-10-16, 22:30: check

- Job B (1 worker): 18 forest fits saved of 140. No error in the log. One fit saved in the last two hours (4,291 s). Two Stan chains from the other project started at 22:16.
- Peak private memory of the worker: 5,163 MB. Lowest free physical memory in the last two hours: 2,212 MB. Free commit 9.6 GB at 22:30.

### 2026-10-17, 00:31: check

- Job B (1 worker): 20 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,667 s and 4,139 s). Four Stan chains from the other project started at 00:29.
- Peak private memory of the worker: 5,776 MB. Lowest free physical memory in the last two hours: 2,110 MB. Free commit 11.0 GB at 00:31.

### 2026-10-17, 02:33: check

- Job B (1 worker): 22 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,278 s and 4,052 s). Four Stan chains from the other project started at 02:27.
- Peak private memory of the worker: 5,181 MB. Lowest free physical memory in the last two hours: 2,790 MB. Free commit 11.8 GB at 02:33.

### 2026-10-17, 04:34: check

- Job B (1 worker): 26 forest fits saved of 140. No error in the log. Four fits saved in the last two hours (4,032, 1,562, 1,538 and 1,656 s). No Stan chains from the other project were running at 04:34, and fits are back to about 26 minutes.
- Peak private memory of the worker: 5,188 MB. Lowest free physical memory in the last two hours: 2,243 MB. Free commit 13.1 GB at 04:34.

### 2026-10-17, 06:35: check

- Job B (1 worker): 30 forest fits saved of 140. No error in the log. Four fits saved in the last two hours (1,648, 1,540, 1,554 and 1,572 s). No Stan chains from the other project were running at 06:35.
- Peak private memory of the worker: 5,197 MB. Lowest free physical memory in the last two hours: 3,057 MB. Free commit 11.6 GB at 06:35.

### 2026-10-17, 08:36: check

- Job B (1 worker): 35 forest fits saved of 140. No error in the log. Five fits saved in the last two hours (1,508 to 1,616 s). No Stan chains from the other project were running at 08:36.
- Peak private memory of the worker: 5,198 MB. Lowest free physical memory in the last two hours: 2,990 MB. Free commit 13.0 GB at 08:36.

### 2026-10-17, 10:37: check

- Job B (1 worker): 37 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (2,018 s and 2,535 s), slower than the morning's 1,500 to 1,600 s. No Stan chains from the other project were running at 10:37; the computer was probably in other use.
- Peak private memory of the worker: 5,184 MB. Lowest free physical memory in the last two hours: 2,157 MB. Free commit 11.1 GB at 10:37.

### 2026-10-17, 12:39: check

- Job B (1 worker): 39 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,978 s and 3,830 s). Four Stan chains from the other project started at 12:36.
- Peak private memory of the worker: 5,193 MB. Lowest free physical memory in the last two hours: 1,955 MB. Free commit 11.7 GB at 12:39.

### 2026-10-17, 14:41: check

- Job B (1 worker): 41 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (3,960 s and 4,071 s). No Stan chains from the other project were running at 14:41.
- Peak private memory of the worker: 5,811 MB. Lowest free physical memory in the last two hours: 1,349 MB, the lowest since phase 2 began apart from the 06:18 stop on 16 Oct. Free commit 12.2 GB at 14:41.

### 2026-10-17, 16:41: check

- Job B (1 worker): 43 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (3,904 s and 4,175 s). No Stan chains from the other project were running, but an Rscript process was using a full processor thread at 16:42.
- Peak private memory of the worker: 5,196 MB. Lowest free physical memory in the last two hours: 2,073 MB. Free commit 13.0 GB at 16:41.

### 2026-10-17, 18:43: check

- Job B (1 worker): 44 forest fits saved of 140. No error in the log. One fit saved in the last two hours (4,233 s). The Rscript processes from the other project, started 09:30, were still running.
- Peak private memory of the worker: 5,172 MB. Lowest free physical memory in the last two hours: 1,919 MB. Free commit 10.1 GB at 18:43.

### 2026-10-17, 20:43: check

- Job B (1 worker): 46 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,054 s and 4,325 s). The Rscript processes from the other project (since 09:30) and four new Stan chains (`engine_locked_v2_benefit_triple.exe`, started 20:37) were running.
- Peak private memory of the worker: 5,180 MB. Lowest free physical memory in the last two hours: 1,888 MB. Free commit 11.6 GB at 20:43.

### 2026-10-17, 22:45: check

- Job B (1 worker): 48 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (3,835 s and 3,915 s). The Rscript processes from the other project (since 09:30) and four Stan chains (started 22:23) were running.
- Peak private memory of the worker: 5,184 MB. Lowest free physical memory in the last two hours: 2,171 MB. Free commit 12.5 GB at 22:45.

### 2026-10-18, 00:47: check

- Job B (1 worker): 50 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,175 s and 4,376 s). The Rscript processes from the other project (since 09:30 on 17 Oct) were still running; no Stan chains at 00:47.
- Peak private memory of the worker: 5,191 MB. Lowest free physical memory in the last two hours: 2,593 MB. Free commit 13.0 GB at 00:47.

### 2026-10-18, 02:48: check

- Job B (1 worker): 51 forest fits saved of 140. No error in the log. One fit saved in the last two hours (3,944 s). The Rscript processes from the other project (since 09:30 on 17 Oct) were still running.
- Peak private memory of the worker: 4,728 MB. Lowest free physical memory in the last two hours: 2,625 MB. Free commit 9.7 GB at 02:48.

### 2026-10-18, 04:49: check

- Job B (1 worker): 53 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,190 s and 4,013 s). The Rscript processes from the other project (since 09:30 on 17 Oct) were still running.
- Peak private memory of the worker: 5,185 MB. Lowest free physical memory in the last two hours: 1,939 MB. Free commit 9.7 GB at 04:49.

### 2026-10-18, 06:50: check

- Job B (1 worker): 55 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (3,628 s and 3,658 s). The Rscript processes from the other project (since 09:30 on 17 Oct) and four Stan chains (`engine_locked_v2_benefit.exe`, started 06:41) were running.
- Peak private memory of the worker: 5,180 MB. Lowest free physical memory in the last two hours: 2,037 MB. Free commit 10.4 GB at 06:50.

### 2026-10-18, 08:52: check

- Job B (1 worker): 57 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,029 s and 2,925 s). The Rscript processes from the other project (since 09:30 on 17 Oct) and four Stan chains (started 08:50) were running.
- Peak private memory of the worker: 5,190 MB. Lowest free physical memory in the last two hours: 2,391 MB. Free commit 10.0 GB at 08:52.

### 2026-10-18, 10:53: check

- Job B (1 worker): 59 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (3,554 s and 3,912 s). The Rscript processes from the other project (since 09:30 on 17 Oct) were still running; no Stan chains at 10:53.
- Peak private memory of the worker: 5,193 MB. Lowest free physical memory in the last two hours: 1,891 MB. Free commit 10.2 GB at 10:53.

### 2026-10-18, 12:55: check

- Job B (1 worker): 62 forest fits saved of 140. No error in the log. Three fits saved in the last two hours (3,846, 3,560 and 1,666 s). The Rscript processes from 09:30 on 17 Oct have ended; new Rscript processes started at 12:43.
- Peak private memory of the worker: 6,108 MB. Lowest free physical memory in the last two hours: 1,223 MB, the lowest since the 06:18 stop on 16 Oct but above the 500 MB rule. Free commit 11.9 GB at 12:55.

### 2026-10-18, 14:57: check

- Job B (1 worker): 64 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (3,607 s and 3,928 s). Rscript processes from the other project (since 12:43) and four Stan chains (started 14:54) were running.
- Peak private memory of the worker: 5,203 MB. Lowest free physical memory in the last two hours: 1,859 MB. Free commit 12.4 GB at 14:57.

### 2026-10-18, 16:58: check

- Job B (1 worker): 65 forest fits saved of 140. No error in the log. One fit saved in the last two hours (3,889 s). Rscript processes from the other project (since 12:43) were still running; no Stan chains at 16:58.
- Peak private memory of the worker: 5,197 MB. Lowest free physical memory in the last two hours: 2,279 MB. Free commit 9.9 GB at 16:58.

### 2026-10-18, 18:59: check

- Job B (1 worker): 67 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,423 s and 4,286 s). Rscript processes from the other project (since 12:43) and two Stan chains (started 18:26) were running.
- Peak private memory of the worker: 5,204 MB. Lowest free physical memory in the last two hours: 1,858 MB. Free commit 11.4 GB at 18:59.

### 2026-10-18, 21:00: check

- Job B (1 worker): 69 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,507 s and 4,085 s). Rscript processes from the other project (since 12:43) were still running; no Stan chains at 21:00.
- Peak private memory of the worker: 5,200 MB. Lowest free physical memory in the last two hours: 2,361 MB. Free commit 11.6 GB at 21:00.

### 2026-10-18, 23:01: check

- Job B (1 worker): 71 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (3,934 s and 4,287 s). Rscript processes from the other project (since 12:43) and one Stan chain (`engine_locked_v2_benefit_triple_dose_quad.exe`, started 22:07) were running.
- Peak private memory of the worker: 5,505 MB. Lowest free physical memory in the last two hours: 1,848 MB. Free commit 13.2 GB at 23:01.

### 2026-10-19, 01:03: check

- Job B (1 worker): 73 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (3,349 s and 4,222 s). Rscript processes from the other project (since 12:43 on 18 Oct) were still running; no Stan chains at 01:03.
- Peak private memory of the worker: 5,197 MB. Lowest free physical memory in the last two hours: 2,034 MB. Free commit 13.1 GB at 01:03.

### 2026-10-19, 03:04: check

- Job B (1 worker): 74 forest fits saved of 140. No error in the log. One fit saved in the last two hours (4,165 s). Rscript processes from the other project (since 12:43 on 18 Oct) and four Stan chains (started 03:00) were running.
- Peak private memory of the worker: 5,197 MB. Lowest free physical memory in the last two hours: 2,235 MB. Free commit 10.2 GB at 03:04.

### 2026-10-19, 05:05: check

- Job B (1 worker): 76 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,440 s and 4,166 s). Rscript processes from the other project (since 12:43 on 18 Oct) were still running; no Stan chains at 05:05.
- Peak private memory of the worker: 5,496 MB. Lowest free physical memory in the last two hours: 1,307 MB. Free commit 10.5 GB at 05:05.

### 2026-10-19, 07:06: check

- Job B (1 worker): 78 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,401 s and 3,765 s). Rscript processes from the other project (since 12:43 on 18 Oct) were still running; no Stan chains at 07:06.
- Peak private memory of the worker: 5,187 MB. Lowest free physical memory in the last two hours: 1,887 MB. Free commit 12.0 GB at 07:06.

### 2026-10-19, 09:08: check

- Job B (1 worker): 80 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (3,943 s and 4,048 s). Rscript processes from the other project (since 12:43 on 18 Oct) and four Stan chains (`engine_locked_v2_benefit_triple_dose_factor.exe`, started 08:47) were running.
- Peak private memory of the worker: 5,202 MB. Lowest free physical memory in the last two hours: 2,155 MB. Free commit 13.4 GB at 09:08.

### 2026-10-19, 11:09: check

- Job B (1 worker): 81 forest fits saved of 140. No error in the log. One fit saved in the last two hours (3,937 s). Rscript processes from the other project (since 12:43 on 18 Oct) and four Stan chains (started 11:09) were running.
- Peak private memory of the worker: 5,196 MB. Lowest free physical memory in the last two hours: 2,236 MB. Free commit 9.5 GB at 11:09.

### 2026-10-19, 13:10: check

- Job B (1 worker): 83 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,048 s and 3,788 s). Rscript processes from the other project (since 12:43 on 18 Oct) were still running; no Stan chains at 13:10.
- Peak private memory of the worker: 5,200 MB. Lowest free physical memory in the last two hours: 2,141 MB. Free commit 9.9 GB at 13:10.

### 2026-10-19, 15:11: check

- Job B (1 worker): 85 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,214 s and 4,117 s). Rscript processes from the other project (since 12:43 on 18 Oct) were still running; no Stan chains at 15:11.
- Peak private memory of the worker: 5,194 MB. Lowest free physical memory in the last two hours: 1,977 MB. Free commit 11.3 GB at 15:11.

### 2026-10-19, 17:11: check

- Job B (1 worker): 87 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,646 s and 4,323 s). Rscript processes from the other project (since 12:43 on 18 Oct) were still running; no Stan chains at 17:11.
- Peak private memory of the worker: 5,191 MB. Lowest free physical memory in the last two hours: 2,241 MB. Free commit 12.8 GB at 17:11.

### 2026-10-19, 19:13: check

- Job B (1 worker): 88 forest fits saved of 140. No error in the log. One fit saved in the last two hours (4,837 s). The Rscript processes from 12:43 on 18 Oct have ended; new Rscript processes started at 18:17. No Stan chains at 19:13.
- Peak private memory of the worker: 5,182 MB. Lowest free physical memory in the last two hours: 1,875 MB. Free commit 10.4 GB at 19:13.

### 2026-10-19, 21:14: check

- Job B (1 worker): 91 forest fits saved of 140. No error in the log. Three fits saved in the last two hours (3,203, 2,174 and 3,635 s). Rscript processes from the other project (since 18:17) were still running; no Stan chains at 21:14.
- Peak private memory of the worker: 5,199 MB. Lowest free physical memory in the last two hours: 2,147 MB. Free commit 12.3 GB at 21:14.

### 2026-10-19, 23:15: check

- Job B (1 worker): 92 forest fits saved of 140. No error in the log. One fit saved in the last two hours (6,730 s, the longest so far). Rscript processes from the other project (since 18:17) and four Stan chains (started 23:09) were running.
- Peak private memory of the worker: 5,198 MB. Lowest free physical memory in the last two hours: 2,295 MB. Free commit 11.9 GB at 23:15.

### 2026-10-20, 01:17: check

- Job B (1 worker): 93 forest fits saved of 140. No error in the log. One fit saved in the last two hours (4,372 s). Rscript processes from the other project (since 18:17 on 19 Oct) and four Stan chains (started 01:16) were running.
- Peak private memory of the worker: 5,209 MB. Lowest free physical memory in the last two hours: 2,162 MB. Free commit 12.5 GB at 01:17.

### 2026-10-20, 03:19: check

- Job B (1 worker): 95 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,544 s and 3,902 s). Rscript processes from the other project (since 18:17 on 19 Oct) were still running; no Stan chains at 03:19.
- Peak private memory of the worker: 5,199 MB. Lowest free physical memory in the last two hours: 2,369 MB. Free commit 9.3 GB at 03:19.

### 2026-10-20, 05:20: check

- Job B (1 worker): 97 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,111 s and 3,940 s). Rscript processes from the other project (since 18:17 on 19 Oct) and four Stan chains (`engine_locked_v2_benefit_triple_dose_bystratum.exe`, started 05:16) were running.
- Peak private memory of the worker: 5,197 MB. Lowest free physical memory in the last two hours: 1,658 MB. Free commit 8.7 GB at 05:20.

### 2026-10-20, 07:21: check

- Job B (1 worker): 100 forest fits saved of 140. No error in the log. Three fits saved in the last two hours (2,749, 2,849 and 3,084 s). Rscript processes from the other project (since 18:17 on 19 Oct) were still running; no Stan chains at 07:21.
- Peak private memory of the worker: 5,199 MB. Lowest free physical memory in the last two hours: 2,039 MB. Free commit 11.4 GB at 07:21.

### 2026-10-20, 09:22: check

- Job B (1 worker): 102 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (3,445 s and 2,728 s). Rscript processes from the other project (since 18:17 on 19 Oct) and four Stan chains (started 09:08) were running.
- Peak private memory of the worker: 5,203 MB. Lowest free physical memory in the last two hours: 2,058 MB. Free commit 11.0 GB at 09:22.

### 2026-10-20, 11:23: check

- Job B (1 worker): 104 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,285 s and 4,543 s). Rscript processes from the other project (since 18:17 on 19 Oct) and two Stan chains (started 11:06) were running.
- Peak private memory of the worker: 5,202 MB. Lowest free physical memory in the last two hours: 2,370 MB. Free commit 12.7 GB at 11:23.

### 2026-10-20, 13:25: check

- Job B (1 worker): 105 forest fits saved of 140. No error in the log. One fit saved in the last two hours (4,181 s). Rscript processes from the other project (since 18:17 on 19 Oct) and four Stan chains (started 13:16) were running.
- Peak private memory of the worker: 5,193 MB. Lowest free physical memory in the last two hours: 2,685 MB. Free commit 9.8 GB at 13:25.

### 2026-10-20, 15:26: check

- Job B (1 worker): 108 forest fits saved of 140. No error in the log. Three fits saved in the last two hours (4,421, 2,777 and 2,189 s). The Rscript processes from 18:17 on 19 Oct have ended; new ones started at 14:43. Four Stan chains from the other project started at 15:08.
- Peak private memory of the worker: 5,190 MB. Lowest free physical memory in the last two hours: 2,493 MB. Free commit 12.2 GB at 15:26.

### 2026-10-20, 17:28: check

- Job B (1 worker): 110 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (4,139 s and 4,192 s). Rscript processes from the other project (since 14:43) and four Stan chains (started 17:22) were running.
- Peak private memory of the worker: 5,196 MB. Lowest free physical memory in the last two hours: 1,875 MB. Free commit 12.3 GB at 17:28.

### 2026-10-20, 19:29: check

- Job B (1 worker): 111 forest fits saved of 140. No error in the log. One fit saved in the last two hours (4,164 s). Rscript processes from the other project (since 14:43) and four Stan chains (started 19:27) were running.
- Peak private memory of the worker: 5,202 MB. Lowest free physical memory in the last two hours: 2,171 MB. Free commit 9.6 GB at 19:29.

### 2026-10-20, 21:30: check

- Job B (1 worker): 114 forest fits saved of 140. No error in the log. Three fits saved in the last two hours (4,387, 3,057 and 2,588 s). Rscript processes from the other project (since 14:43) and four Stan chains (started 21:30) were running.
- Peak private memory of the worker: 5,187 MB. Lowest free physical memory in the last two hours: 1,400 MB. Free commit 11.3 GB at 21:30.

### 2026-10-20, 23:31: check

- Job B (1 worker): 116 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (2,779 s and 2,618 s). Rscript processes from the other project (since 14:43) were still running; no Stan chains at 23:31.
- Peak private memory of the worker: 5,188 MB. Lowest free physical memory in the last two hours: 2,099 MB. Free commit 9.9 GB at 23:31.

### 2026-10-21, 01:33: check

- Job B (1 worker): 118 forest fits saved of 140. No error in the log. Two fits saved in the last two hours (3,438 s and 4,349 s). Rscript processes from the other project (since 14:43 on 20 Oct) were still running; no Stan chains at 01:33.
- Peak private memory of the worker: 5,189 MB. Lowest free physical memory in the last two hours: 2,066 MB. Free commit 10.6 GB at 01:33.

### 2026-10-21, 03:34: check

- Job B (1 worker): 121 forest fits saved of 140. No error in the log. Three fits saved in the last two hours (4,047, 1,520 and 2,814 s). No Rscript or Stan processes from the other project were running at 03:34.
- Peak private memory of the worker: 5,224 MB. Lowest free physical memory in the last two hours: 1,988 MB. Free commit 10.0 GB at 03:34.

### 2026-10-21, 05:35: check

- Job B (1 worker): 126 forest fits saved of 140. No error in the log. Five fits saved in the last two hours (1,462 to 1,983 s). No Rscript or Stan processes from the other project were running at 05:35.
- Peak private memory of the worker: 5,211 MB. Lowest free physical memory in the last two hours: 2,045 MB. Free commit 12.7 GB at 05:35.

### 2026-10-21, 07:36: check

- Job B (1 worker): 130 forest fits saved of 140. No error in the log. Four fits saved in the last two hours (1,540 to 1,843 s). No Rscript or Stan processes from the other project were running at 07:36.
- Peak private memory of the worker: 5,206 MB. Lowest free physical memory in the last two hours: 2,505 MB. Free commit 10.8 GB at 07:36.

### 2026-10-21, 09:36: check

- Job B (1 worker): 134 forest fits saved of 140. No error in the log. Four fits saved in the last two hours (1,437, 1,521, 1,542 and 2,904 s). No Rscript or Stan processes from the other project were running at 09:36.
- Peak private memory of the worker: 5,214 MB. Lowest free physical memory in the last two hours: 2,557 MB. Free commit 11.7 GB at 09:36.

### 2026-10-21, 11:38: check

- Job B (1 worker): 137 forest fits saved of 140. No error in the log. Three fits saved in the last two hours (1,564, 1,589 and 1,425 s). New Rscript processes and four Stan chains from the other project (`engine_sens_S19_withintrial_benefit.exe`) started at 11:36.
- Peak private memory of the worker: 5,183 MB. Lowest free physical memory in the last two hours: 2,655 MB. Free commit 10.1 GB at 11:38.

### 2026-10-21, 13:00: phase 2 done, phase 3 begins

- 13:00:02: job B finished: 140 of 140 forest fits saved, "finished" printed, exit code 0, no Traceback or MemoryError in its log. Total time for phase 2: 16 Oct 04:44 to 21 Oct 13:00, slowed by the other project's R and Stan jobs on this computer.
- Job A resumes for the remaining 260 datasets with 3 workers (rule: restart with 3 workers if free commit goes under 1.5 GB). The 260 include the two `no_instrument_20000` datasets lost at the 16 Oct 04:44 stop.

### 2026-10-21, 13:01: check (corrected)

- Job A (3 workers): 400 datasets done of 660 (720 fit rows of 1,180); the restarted job had not yet saved its first dataset. No error in the log.
- Correction: this entry first said "660 datasets done of 660" and listed no workers. That was wrong. The runner's helper scripts read the count from the last progress line, and the new run had not printed one yet. The watcher stopped at once for the same reason, which triggered this early check. Both scripts were fixed to handle this case.
- Workers starting at 13:01 (595 MB private each). Free physical 6.3 GB; free commit 13.3 GB.

### 2026-10-21, 15:03: check

- Job A (3 workers): 404 datasets done of 660 (728 fit rows of 1,180). No error in the log.
- Running workers: 3879 MB private, started 13:01; 3880 MB private, started 13:01; 1587 MB private, started 14:41. Free physical 0.6 GB; free commit 5.2 GB. Lowest free commit in the last two hours: 5207 MB.

### 2026-10-21, 17:04: check

- Job A (3 workers): 419 datasets done of 660 (755 fit rows of 1,180). No error in the log.
- Running workers: 1372 MB private, started 16:57; 1587 MB private, started 16:50; 1065 MB private, started 16:56. Free physical 5.3 GB; free commit 10.4 GB. Lowest free commit in the last two hours: 4159 MB.

### 2026-10-21, 19:05: check

- Job A (3 workers): 435 datasets done of 660 (784 fit rows of 1,180). No error in the log.
- Running workers: 1372 MB private, started 18:56; 1215 MB private, started 18:59; 1083 MB private, started 18:56. Free physical 5 GB; free commit 10.4 GB. Lowest free commit in the last two hours: 9530 MB.

### 2026-10-21, 21:07: check

- Job A (3 workers): 455 datasets done of 660 (818 fit rows of 1,180). No error in the log.
- Running workers: 1214 MB private, started 21:00; 1115 MB private, started 20:58; 1215 MB private, started 21:03. Free physical 5.1 GB; free commit 10.6 GB. Lowest free commit in the last two hours: 9587 MB.

### 2026-10-21, 23:08: check

- Job A (3 workers): 478 datasets done of 660 (858 fit rows of 1,180). No error in the log.
- Running workers: 1370 MB private, started 23:04; 1587 MB private, started 23:02; 1215 MB private, started 23:05. Free physical 4.8 GB; free commit 10.1 GB. Lowest free commit in the last two hours: 9531 MB.

### 2026-10-22, 01:09: check

- Job A (3 workers): 497 datasets done of 660 (893 fit rows of 1,180). No error in the log.
- Running workers: 1587 MB private, started 00:53; 1587 MB private, started 00:59; 1587 MB private, started 00:58. Free physical 4.6 GB; free commit 9.5 GB. Lowest free commit in the last two hours: 9651 MB.
