"""Step 3 with an instrument: can the joint model correct for a hidden factor now?

Without an instrument the joint model could not detect the hidden factor
(scripts 06 and 08). The approach it belongs to relies on an instrument:
something that moves drug choice and affects the outcome in no other way, such
as a practice's prescribing habit (Conley et al., J Econometrics 2008).

This script adds one to the simulated patients, at two strengths, and fits
two models to each dataset:

  plain   a regression with a drug effect that varies with the features;
          it assumes nothing is hidden and does not use the instrument
  joint   the same, plus a model of drug choice that includes the instrument,
          with the two unexplained parts allowed to be linked (rho)

Settings: the seven hidden-factor settings of step 2, two instrument
strengths, twenty datasets each (280 datasets). The first ten were run
on 2026-10-07 and the second ten on 2026-10-08.

An instrument strength of 0.5 moves drug choice about as much as BMI does;
1.0 moves it twice as much.

Results go to results/generator-v<version>/instrument/<COMPUTER NAME>.csv,
two rows per dataset.

Run:  uv run python scripts/10_instrument_grid.py   (about two and a half hours for ten datasets per setting)
"""

import argparse
import csv
import importlib.util
import time
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "grid", Path(__file__).parent / "03_causal_forest_grid.py"
)
grid = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(grid)

INSTRUMENT_STRENGTHS = (0.5, 1.0)
REPEATS = 20

FOLDER = grid.FOLDER / "instrument"
RESULTS = FOLDER / f"{grid.HOST}.csv"


def run_one(instrument_strength, shape, strength, repeat, commit):
    """Simulate one dataset with an instrument, fit both models, return two rows."""
    import numpy as np

    from stresstest.generator import GENERATOR_VERSION, make_patients
    from stresstest.joint_model import fit_joint_model
    from stresstest.scoring import convergence, crude_error, score
    from stresstest.validation import concordance_validation

    warnings.filterwarnings("ignore")
    patients = make_patients(
        grid.N_PATIENTS,
        strength,
        "linear" if shape == "none" else shape,
        seed=repeat,
        instrument_strength=instrument_strength,
    )
    rows = []
    for model, link_errors in (("plain", False), ("joint", True)):
        start = time.time()
        effect_draws, rho_draws = fit_joint_model(
            patients, seed=repeat, link_errors=link_errors, use_instrument=link_errors
        )
        low, high = np.percentile(rho_draws, [2.5, 97.5])
        row = {
            "generator_version": GENERATOR_VERSION,
            "host": grid.HOST,
            "code_commit": commit,
            "model": model,
            "instrument_strength": instrument_strength,
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
        estimate = effect_draws.reshape(len(effect_draws), -1).mean(axis=1)
        row.update(
            concordance_validation(
                patients.features, patients.treated, patients.outcome,
                estimate, patients.true_effect,
            )
        )
        row["seconds"] = round(time.time() - start)
        rows.append(row)
    return rows


def all_settings():
    return [
        (instrument_strength, shape, strength, repeat)
        for repeat in range(REPEATS)
        for instrument_strength in INSTRUMENT_STRENGTHS
        for shape, strength, _ in grid.all_settings(repeat, repeat)
    ]


def already_done():
    done = set()
    for file in FOLDER.glob("*.csv"):
        with file.open(newline="") as rows:
            done |= {
                (float(r["instrument_strength"]), r["shape"], float(r["strength"]), int(r["repeat"]))
                for r in csv.DictReader(rows)
            }
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
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    commit = grid.code_commit()
    done = already_done()
    todo = [s for s in all_settings() if s not in done]
    print(f"code {commit}, computer {grid.HOST}: {len(todo)} datasets to run -> instrument/{RESULTS.name}", flush=True)

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = [pool.submit(run_one, *setting, commit) for setting in todo]
        for count, job in enumerate(as_completed(jobs), start=1):
            rows = job.result()
            save(rows)
            plain, joint = rows
            print(
                f"[{count}/{len(todo)}] instrument {plain['instrument_strength']:.1f} {plain['shape']:9s} "
                f"strength {plain['strength']:.1f} repeat {plain['repeat']:2d}: "
                f"error in average effect plain {plain['bias_average']:+.2f}, joint {joint['bias_average']:+.2f}; "
                f"rho {joint['rho_mean']:+.2f}; {plain['seconds'] + joint['seconds']} s",
                flush=True,
            )
    print("finished", flush=True)
