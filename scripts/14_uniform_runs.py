"""One uniform set of runs: twenty datasets and 2,000 draws per chain for every setting.

The earlier runs grew step by step. Some settings have ten datasets and some
twenty, and the PyMC models kept 1,000 draws per chain where the causal forest
kept 2,000. This script fits the plain regression and the joint model (with a
noise level per drug) again, on twenty datasets per setting and with 2,000
draws per chain, so that all three models rest on the same numbers. The causal
forest already has twenty datasets and 2,000 draws (script 03) and is not
refitted.

Settings, in the order they are run:

  First, the settings shown on the slides:
    ideal instrument, strength 1.0   hidden factor off, and each shape at strength 1
    no instrument, 5,000 patients    hidden factor off, and linear at strength 1
    practice-level instruments       linear at strength 1
    invalid instruments              hidden factor off, and linear at strength 1
    ideal instrument, strength 0.5   hidden factor off, and linear at strength 1
    instrument used as a feature     hidden factor off, and each shape at strength 1
    no instrument, 20,000 patients   hidden factor off, and linear at strength 1

  Then every other setting of reports 08 to 14.

The same seeds are used as before, so dataset r of a setting is the same
simulated patients as in the earlier runs. Earlier results are not touched.

Results go to results/generator-v<version>/uniform_2000/<COMPUTER NAME>.csv,
one row per model and dataset. A finished dataset is saved straight away, and
running the script again continues where it left off.

Run:  uv run python scripts/14_uniform_runs.py --workers 6
      uv run python scripts/14_uniform_runs.py --list     (print what is left to do, fit nothing)
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

REPEATS = 20
DRAWS = 2000
MANY_PATIENTS = 20_000

OFF = ("none", 0.0)
AT_STRENGTH_1 = (("linear", 1.0), ("threshold", 1.0), ("effect", 1.0))
AT_STRENGTH_HALF = (("linear", 0.5), ("threshold", 0.5), ("effect", 0.5))

# variant -> options for the patient generator
GENERATOR = {
    "ideal_instrument": {"instrument_strength": 1.0},
    "ideal_instrument_0.5": {"instrument_strength": 0.5},
    "ideal_as_feature": {"instrument_strength": 1.0},
    "no_instrument": {},
    "no_instrument_20000": {},
    "practice_100": {"instrument_strength": 1.0, "instrument_groups": 100},
    "practice_25": {"instrument_strength": 1.0, "instrument_groups": 25},
    "flaw_0.5": {"instrument_strength": 1.0, "instrument_flaw": 0.5},
    "flaw_1.0": {"instrument_strength": 1.0, "instrument_flaw": 1.0},
}

# (variant, hidden-factor settings), slides first
ON_THE_SLIDES = (
    ("ideal_instrument", (OFF, *AT_STRENGTH_1)),
    ("no_instrument", (OFF, ("linear", 1.0))),
    ("practice_100", (("linear", 1.0),)),
    ("practice_25", (("linear", 1.0),)),
    ("flaw_0.5", (OFF, ("linear", 1.0))),
    ("flaw_1.0", (OFF, ("linear", 1.0))),
    ("ideal_instrument_0.5", (OFF, ("linear", 1.0))),
    ("ideal_as_feature", (OFF, *AT_STRENGTH_1)),
    ("no_instrument_20000", (OFF, ("linear", 1.0))),
)
THE_REST = (
    ("ideal_instrument", AT_STRENGTH_HALF),
    ("ideal_instrument_0.5", (*AT_STRENGTH_HALF, ("threshold", 1.0), ("effect", 1.0))),
    ("practice_100", (OFF,)),
    ("practice_25", (OFF,)),
    ("ideal_as_feature", AT_STRENGTH_HALF),
)


def all_settings():
    """Every (variant, shape, strength, repeat), slides first, one whole repeat at a time."""
    settings = []
    for block in (ON_THE_SLIDES, THE_REST):
        for repeat in range(REPEATS):
            for variant, hidden_settings in block:
                for shape, strength in hidden_settings:
                    settings.append((variant, shape, strength, repeat))
    return settings


def fits_for(variant):
    """The models fitted to one dataset of this variant: (name, options for fit_joint_model)."""
    plain = ("plain", {"link_errors": False})
    if variant == "ideal_as_feature":
        return (("plain_with_instrument", {"link_errors": False, "instrument_as_feature": True}),)
    uses_instrument = not variant.startswith("no_instrument")
    joint = ("joint_per_drug_noise", {"use_instrument": uses_instrument, "noise_per_drug": True})
    return (plain, joint)


def run_one(variant, shape, strength, repeat, commit):
    """Simulate one dataset, fit its models, return one row per model."""
    import numpy as np

    from stresstest.generator import GENERATOR_VERSION, make_patients
    from stresstest.joint_model import fit_joint_model
    from stresstest.scoring import convergence, crude_error, score

    warnings.filterwarnings("ignore")
    n = MANY_PATIENTS if variant == "no_instrument_20000" else grid.N_PATIENTS
    patients = make_patients(
        n, strength, "linear" if shape == "none" else shape, seed=repeat, **GENERATOR[variant]
    )
    rows = []
    for model, fit_options in fits_for(variant):
        start = time.time()
        effect_draws, rho_draws = fit_joint_model(patients, seed=repeat, draws=DRAWS, **fit_options)
        low, high = np.percentile(rho_draws, [2.5, 97.5])
        row = {
            "generator_version": GENERATOR_VERSION,
            "host": grid.HOST,
            "code_commit": commit,
            "draws_per_chain": DRAWS,
            "variant": variant,
            "model": model,
            "patients": n,
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


def already_done(folder):
    """Datasets saved by any computer."""
    done = set()
    for file in folder.glob("*.csv"):
        with file.open(newline="") as rows:
            done |= {
                (r["variant"], r["shape"], float(r["strength"]), int(r["repeat"]))
                for r in csv.DictReader(rows)
            }
    return done


def save(results, rows):
    is_new_file = not results.exists()
    results.parent.mkdir(parents=True, exist_ok=True)
    with results.open("a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        if is_new_file:
            writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4, help="datasets to fit side by side")
    parser.add_argument("--list", action="store_true", help="print what is left to do and stop")
    args = parser.parse_args()

    folder = grid.FOLDER / f"uniform_{DRAWS}"
    results = folder / f"{grid.HOST}.csv"
    done = already_done(folder)
    todo = [s for s in all_settings() if s not in done]
    fits = sum(len(fits_for(s[0])) for s in todo)
    if args.list:
        print(f"{len(todo)} datasets ({fits} fits) left of {len(all_settings())} datasets")
        raise SystemExit

    commit = grid.code_commit()
    print(
        f"code {commit}, computer {grid.HOST}, {DRAWS} draws per chain: "
        f"{len(todo)} datasets ({fits} fits) to run -> uniform_{DRAWS}/{results.name}",
        flush=True,
    )

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = [pool.submit(run_one, *setting, commit) for setting in todo]
        for count, job in enumerate(as_completed(jobs), start=1):
            rows = job.result()
            save(results, rows)
            summary = ", ".join(f"{r['model']} {r['bias_average']:+.2f}" for r in rows)
            first = rows[0]
            print(
                f"[{count}/{len(todo)}] {first['variant']:20s} {first['shape']:9s} strength {first['strength']:.1f} "
                f"repeat {first['repeat']:2d}: error in average effect {summary}; "
                f"{sum(r['seconds'] for r in rows)} s",
                flush=True,
            )
    print("finished", flush=True)
