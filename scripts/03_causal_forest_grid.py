"""Step 2: how wrong does the causal forest get as the hidden factor is switched on?

Fits the Bayesian causal forest to many simulated datasets:
three strengths of the hidden factor, three shapes, 20 datasets per setting.
At strength 0 the shape makes no difference, so that setting is run once.

Each finished fit is added to results/causal_forest_grid.csv straight away.
If the script is stopped, running it again continues where it left off.

Run:  uv run python scripts/03_causal_forest_grid.py
"""

import csv
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

N_PATIENTS = 5000
STRENGTHS = (0.5, 1.0)
REPEATS = 20
WORKERS = 4  # fits run side by side

RESULTS = Path(__file__).parent.parent / "results" / "causal_forest_grid.csv"


def all_settings():
    """Every (shape, strength, repeat) to run."""
    from stresstest.generator import SHAPES

    settings = [("none", 0.0, repeat) for repeat in range(REPEATS)]
    for shape in SHAPES:
        for strength in STRENGTHS:
            settings += [(shape, strength, repeat) for repeat in range(REPEATS)]
    return settings


def run_one(shape, strength, repeat):
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

    row = {"shape": shape, "strength": strength, "repeat": repeat}
    row["crude_error"] = crude_error(patients)
    row.update(score(effect_draws, patients.true_effect))
    row.update(convergence(effect_draws))
    row["seconds"] = round(time.time() - start)
    return row


def already_done():
    if not RESULTS.exists():
        return set()
    with RESULTS.open(newline="") as file:
        return {(r["shape"], float(r["strength"]), int(r["repeat"])) for r in csv.DictReader(file)}


def save(row):
    is_new_file = not RESULTS.exists()
    RESULTS.parent.mkdir(exist_ok=True)
    with RESULTS.open("a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(row))
        if is_new_file:
            writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    done = already_done()
    todo = [s for s in all_settings() if s not in done]
    print(f"{len(done)} fits already saved, {len(todo)} to run", flush=True)

    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        jobs = [pool.submit(run_one, *setting) for setting in todo]
        for count, job in enumerate(as_completed(jobs), start=1):
            row = job.result()
            save(row)
            print(
                f"[{count}/{len(todo)}] {row['shape']:9s} strength {row['strength']:.1f} "
                f"repeat {row['repeat']:2d}: rmse {row['rmse_individual']:.2f}, "
                f"wrong drug {row['wrong_drug']:.1%}, {row['seconds']} s",
                flush=True,
            )
