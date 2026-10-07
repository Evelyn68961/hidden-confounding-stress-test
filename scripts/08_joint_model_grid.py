"""Step 3: the joint model on the same 140 datasets as the causal forest.

For every dataset of step 2 (same settings, same seeds) this fits two models:

  plain   a regression with a drug effect that varies with the features;
          it assumes nothing is hidden
  joint   the same, plus a model of drug choice whose unexplained part may be
          linked to the outcome's (rho)

and scores both against the truth, exactly as the forest was scored.

Results go to results/generator-v<version>/joint_model/<COMPUTER NAME>.csv,
two rows per dataset. The subfolder keeps them apart from the forest's
results. Each finished dataset is saved straight away, and running the script
again continues where it left off.

Run:  uv run python scripts/08_joint_model_grid.py   (about an hour and a half)
"""

import argparse
import csv
import importlib.util
import time
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# Settings, seeds and the committed-code check are taken from the forest's
# script, so the two steps cannot drift apart.
_spec = importlib.util.spec_from_file_location(
    "grid", Path(__file__).parent / "03_causal_forest_grid.py"
)
grid = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(grid)

FOLDER = grid.FOLDER / "joint_model"
RESULTS = FOLDER / f"{grid.HOST}.csv"


def run_one(shape, strength, repeat, commit):
    """Simulate one dataset, fit both models, and return two rows of results."""
    import numpy as np

    from stresstest.generator import GENERATOR_VERSION, make_patients
    from stresstest.joint_model import fit_joint_model
    from stresstest.scoring import convergence, crude_error, score

    warnings.filterwarnings("ignore")
    patients = make_patients(
        grid.N_PATIENTS, strength, "linear" if shape == "none" else shape, seed=repeat
    )
    rows = []
    for model, link_errors in (("plain", False), ("joint", True)):
        start = time.time()
        effect_draws, rho_draws = fit_joint_model(patients, seed=repeat, link_errors=link_errors)
        low, high = np.percentile(rho_draws, [2.5, 97.5])
        row = {
            "generator_version": GENERATOR_VERSION,
            "host": grid.HOST,
            "code_commit": commit,
            "model": model,
            "shape": shape,
            "strength": strength,
            "repeat": repeat,
            "crude_error": crude_error(patients),
            "rho_mean": float(rho_draws.mean()),
            "rho_low": float(low),
            "rho_high": float(high),
        }
        row.update(score(effect_draws, patients.true_effect))
        row.update(convergence(effect_draws))
        row["seconds"] = round(time.time() - start)
        rows.append(row)
    return rows


def already_done():
    done = set()
    for file in FOLDER.glob("*.csv"):
        with file.open(newline="") as rows:
            done |= {(r["shape"], float(r["strength"]), int(r["repeat"])) for r in csv.DictReader(rows)}
    return done


def save(rows):
    is_new_file = not RESULTS.exists()
    FOLDER.mkdir(parents=True, exist_ok=True)
    with RESULTS.open("a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        if is_new_file:
            writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", default=f"0-{grid.REPEATS - 1}", help="range of repeats, e.g. 0-9")
    parser.add_argument("--workers", type=int, default=4, help="datasets to run side by side")
    args = parser.parse_args()
    first_repeat, last_repeat = (int(x) for x in args.repeats.split("-"))

    commit = grid.code_commit()
    done = already_done()
    todo = [s for s in grid.all_settings(first_repeat, last_repeat) if s not in done]
    print(f"code {commit}, computer {grid.HOST}: {len(todo)} datasets to run -> joint_model/{RESULTS.name}", flush=True)

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = [pool.submit(run_one, *setting, commit) for setting in todo]
        for count, job in enumerate(as_completed(jobs), start=1):
            rows = job.result()
            save(rows)
            plain, joint = rows
            print(
                f"[{count}/{len(todo)}] {plain['shape']:9s} strength {plain['strength']:.1f} repeat {plain['repeat']:2d}: "
                f"wrong drug plain {plain['wrong_drug']:.1%}, joint {joint['wrong_drug']:.1%}; "
                f"rho {joint['rho_mean']:+.2f}; {plain['seconds'] + joint['seconds']} s",
                flush=True,
            )
    print("finished", flush=True)
