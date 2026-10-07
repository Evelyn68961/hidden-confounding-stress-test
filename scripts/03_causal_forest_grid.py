"""Step 2: how wrong does the causal forest get as the hidden factor is switched on?

Fits the Bayesian causal forest to many simulated datasets:
two strengths of the hidden factor, three shapes, 20 datasets per setting.
At strength 0 the shape makes no difference, so that setting is run once.
That is 140 fits in all.

The work can be shared between computers. Each computer runs its own range of
repeats and writes its own file:

    results/generator-v<version>/<COMPUTER NAME>.csv

Each finished fit is added to that file straight away. If the script is
stopped, running it again continues where it left off. Fits that any computer
has already saved are skipped.

Run:  uv run python scripts/03_causal_forest_grid.py --repeats 0-9
See docs/RUNNER.md for running it on a second computer.
"""

import argparse
import csv
import socket
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from stresstest.generator import GENERATOR_VERSION, SHAPES

N_PATIENTS = 5000
STRENGTHS = (0.5, 1.0)
REPEATS = 20

REPO = Path(__file__).parent.parent
HOST = socket.gethostname().upper()
FOLDER = REPO / "results" / f"generator-v{GENERATOR_VERSION}"
RESULTS = FOLDER / f"{HOST}.csv"


def git(*args):
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()


def code_commit():
    """The commit the code is at. Stops if the code has been edited since."""
    edited = git("status", "--porcelain", "--", "src", "scripts", "pyproject.toml", "uv.lock")
    if edited:
        raise SystemExit(
            "The code has changes that are not committed:\n"
            f"{edited}\n"
            "Results must come from committed code. Commit or discard the changes first."
        )
    return git("rev-parse", "--short", "HEAD")


def all_settings(first_repeat, last_repeat):
    """Every (shape, strength, repeat) to run, one whole repeat at a time."""
    settings = []
    for repeat in range(first_repeat, last_repeat + 1):
        settings.append(("none", 0.0, repeat))
        for shape in SHAPES:
            for strength in STRENGTHS:
                settings.append((shape, strength, repeat))
    return settings


def run_one(shape, strength, repeat, commit):
    """Simulate one dataset, fit the forest, and return one row of results."""
    from stresstest.causal_forest import fit_causal_forest
    from stresstest.generator import make_patients
    from stresstest.scoring import convergence, crude_error, score

    start = time.time()
    # At strength 0 the shape is irrelevant; "linear" is passed only because one is required.
    patients = make_patients(
        N_PATIENTS, strength, "linear" if shape == "none" else shape, seed=repeat
    )
    effect_draws = fit_causal_forest(patients, seed=repeat)

    row = {
        "generator_version": GENERATOR_VERSION,
        "host": HOST,
        "code_commit": commit,
        "shape": shape,
        "strength": strength,
        "repeat": repeat,
    }
    row["crude_error"] = crude_error(patients)
    row.update(score(effect_draws, patients.true_effect))
    row.update(convergence(effect_draws))
    row["seconds"] = round(time.time() - start)
    return row


def already_done():
    """Fits saved by any computer for this generator version."""
    done = set()
    for file in FOLDER.glob("*.csv"):
        with file.open(newline="") as rows:
            done |= {(r["shape"], float(r["strength"]), int(r["repeat"])) for r in csv.DictReader(rows)}
    return done


def save(row):
    is_new_file = not RESULTS.exists()
    FOLDER.mkdir(parents=True, exist_ok=True)
    with RESULTS.open("a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(row))
        if is_new_file:
            writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", default=f"0-{REPEATS - 1}", help="range of repeats, e.g. 0-9")
    parser.add_argument("--workers", type=int, default=4, help="fits to run side by side")
    args = parser.parse_args()
    first_repeat, last_repeat = (int(x) for x in args.repeats.split("-"))
    if not 0 <= first_repeat <= last_repeat < REPEATS:
        raise SystemExit(f"--repeats must lie within 0-{REPEATS - 1}")

    commit = code_commit()
    done = already_done()
    todo = [s for s in all_settings(first_repeat, last_repeat) if s not in done]
    print(
        f"generator v{GENERATOR_VERSION}, code {commit}, computer {HOST}, "
        f"repeats {first_repeat}-{last_repeat}: {len(todo)} fits to run -> {RESULTS.name}",
        flush=True,
    )

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = [pool.submit(run_one, *setting, commit) for setting in todo]
        for count, job in enumerate(as_completed(jobs), start=1):
            row = job.result()
            save(row)
            print(
                f"[{count}/{len(todo)}] {row['shape']:9s} strength {row['strength']:.1f} "
                f"repeat {row['repeat']:2d}: rmse {row['rmse_individual']:.2f}, "
                f"wrong drug {row['wrong_drug']:.1%}, {row['seconds']} s",
                flush=True,
            )
    print("finished", flush=True)
