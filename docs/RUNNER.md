# Running the long jobs on a second computer

This file is for a Claude Code session (or a person) asked to run part of the
simulation on a computer other than the author's laptop.

## The two roles

| | Lead (author's laptop, `EVELYN68961`) | Runner (any other computer) |
|---|---|---|
| Writes code, tests, docs, reports | Yes | **No** |
| Runs fits | Yes, its own range of repeats | Yes, the range it is given |
| Writes to | everything | **only** files named after itself: `results/generator-v<N>/<ITS COMPUTER NAME>.csv`, `results/generator-v<N>/<ITS COMPUTER NAME>_RUNLOG.md`, and the two check files `results/generator-v<N>/crosscheck/<ITS COMPUTER NAME>_fingerprints.csv` and `..._refits.csv` |
| Decides what a result means | Yes | No. It reports numbers and problems. |

The runner never edits code, tests, docs, reports, the README, or another
computer's result files. If something looks wrong, it stops and reports.

## Why results cannot get mixed up

- **One file per computer.** Each computer writes only a file named after
  itself, so two computers never edit the same file and git never has to merge
  result rows.
- **One folder per generator version.** `GENERATOR_VERSION` in
  `src/stresstest/generator.py` is raised whenever the simulated patients
  change. Results go to `results/generator-v<N>/`. Results from different
  versions are never pooled.
- **Every row names its source.** Each row records the generator version, the
  computer, and the commit of the code that produced it.
- **Committed code only.** The script refuses to run if the code has
  uncommitted changes, so the recorded commit always matches the code that ran.
- **Disjoint ranges.** Each computer is given its own range of repeats. A
  repeat number is also the random seed, so repeat 7 means the same simulated
  patients on every computer. The script also skips any fit that is already
  saved in any computer's file.

## Checking that the computers agree

Because each computer has its own range of repeats, a hidden difference
between the computers would look like a difference between the two ranges.
Three checks guard against that (`scripts/04_cross_check.py`):

- **Fingerprints.** Each computer simulates the same 14 datasets and saves a
  short code for each. Equal codes mean the two computers simulate identical
  patients. This takes seconds and is done before the long run.
- **Refits.** Each computer fits three datasets from the other computer's
  range. The scores are compared with the other computer's own results for
  those datasets. This shows whether the sampler gives the same answer on
  both. The refits go to a separate file and never enter the main results.
- **Scores by computer.** The comparison prints each setting's scores
  separately for each computer.

## Steps for the runner

1. **Get the code.**
   ```
   git clone https://github.com/Evelyn68961/hidden-confounding-stress-test.git
   ```
   or, if it is already cloned, `git pull` on the `main` branch. Do not create
   a branch.

2. **Install.** Requires [uv](https://docs.astral.sh/uv/).
   ```
   uv sync
   ```
   If the computer is borrowed, install uv and its Python only where the owner
   allows. Do not install anything system-wide without asking the author.

3. **Check the installation.**
   ```
   uv run pytest
   ```
   All tests must pass. If any fails, stop and report (see "If something goes
   wrong").

   On Windows with Smart App Control, a command may fail the first time with
   "An Application Control policy has blocked this file". Run the same command
   again. Do not change any security setting.

4. **Save your fingerprints and push them before the long run.** It takes
   seconds, and it shows early whether your computer simulates the same
   patients as the lead's.
   ```
   uv run python scripts/04_cross_check.py fingerprint
   uv run python scripts/04_cross_check.py compare
   ```
   If `compare` reports any dataset that differs between computers, do not
   start the long run. Stop and report. Otherwise commit and push the
   fingerprints file (see step 6 for how).

5. **Run the range you were given.** Example for repeats 10 to 19:
   ```
   uv run python scripts/03_causal_forest_grid.py --repeats 10-19
   ```
   - It prints one line per finished fit and saves each one immediately.
   - Each fit takes roughly 5 to 15 minutes. Seventy fits take several hours.
   - It uses four processes and about 7 GB of memory. On a smaller computer
     add `--workers 2`.
   - If it stops for any reason, run the same command again. It continues
     where it left off.
   - Do not change `CHAINS`, `WARMUP`, `DRAWS`, `N_PATIENTS` or any other
     setting.

6. **Report by committing only your own files.** About once an hour while it
   runs, and once more when it prints `finished`:
   ```
   git add results/generator-v2/<YOUR COMPUTER NAME>.csv results/generator-v2/<YOUR COMPUTER NAME>_RUNLOG.md results/generator-v2/crosscheck/<YOUR COMPUTER NAME>_*.csv
   git commit -m "Results: <YOUR COMPUTER NAME>, generator v2, <number> fits"
   git pull --rebase
   git push
   ```
   Replace `v2` with the folder the script reports if it differs. Use
   `git add` with those exact paths. Never `git add -A` or `git add .`.

7. **After the long run, refit three of the other computer's datasets.** The
   lead tells you which repeat. For the lead's repeat 0:
   ```
   uv run python scripts/04_cross_check.py refit --repeat 0
   ```
   It takes about 20 to 40 minutes and saves to your `_refits.csv` file.
   Commit and push it as in step 6. Do not run `refit` while the long run is
   still going; it would compete for memory.

8. **Keep a run log** in `results/generator-v<N>/<YOUR COMPUTER NAME>_RUNLOG.md`:
   - the command you ran, and the first line the script printed (it states the
     generator version, code commit, computer and range);
   - start and end time;
   - the number of fits saved;
   - anything unusual: a crash, a restart, a warning, a fit much slower than
     the others.

## If something goes wrong

Stop. Do not fix the code. Write what happened in your run log (the command,
the full error text, what you had already tried), commit and push the run log,
and tell the author.

If `git pull --rebase` reports a conflict, something has broken the
one-file-per-computer rule. Run `git rebase --abort`, do not force anything,
and tell the author.

## What the runner must not do

- Edit or delete any file outside its own two files.
- Run with uncommitted code changes, or try to get round the script's check.
- Lower the chain settings to finish sooner.
- Describe a number as a finding. The lead checks the combined results first.
- Force-push, rewrite history, or create branches.
