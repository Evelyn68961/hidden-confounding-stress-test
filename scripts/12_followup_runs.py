"""Three follow-up runs on the instrument and on the number of patients.

Each run answers one question left open by reports 06 and 08.

  realistic      Is the correction as good when the instrument is less ideal?
                 Four instruments, all of strength 1.0 on drug choice:
                   practice_100  one value per practice, 100 practices
                   practice_25   one value per practice, 25 practices
                   flaw_0.5      also acts on the outcome directly, 0.5 mmol/mol per SD
                   flaw_1.0      also acts on the outcome directly, 1.0 mmol/mol per SD
                 Hidden factor off, and linear at strength 1. Plain and joint model.

  as_feature     What if the instrument is given to the plain regression as an
                 ordinary feature? The seven hidden-factor settings, with the
                 ideal instrument of strength 1.0. One model.

  more_patients  Without an instrument, does the joint model do better with
                 20,000 patients than with 5,000? Hidden factor off, and
                 linear at strength 1. Plain and joint model.

  per_drug_noise The joint model assumes one noise level for both drugs; the
                 simulated patients have two. This run gives the joint model a
                 noise level per drug: with the ideal instrument of strength
                 1.0 (seven hidden-factor settings), and without an instrument
                 at 5,000 and at 20,000 patients (hidden factor off, and
                 linear at strength 1). One model.
                 A second part, added the same day, covers every other
                 instrument setting of reports 08 to 10 with this model: the
                 ideal instrument at strength 0.5, datasets 10 to 19 at
                 strength 1.0, and the four less ideal instruments.

Ten datasets per setting, with the same seeds as scripts 08 and 10, so each
result can be set beside the earlier one for the same simulated hidden factor.

Results go to results/generator-v<version>/<run>/<COMPUTER NAME>.csv.

Run:  uv run python scripts/12_followup_runs.py --run realistic       (about 1.5 hours)
      uv run python scripts/12_followup_runs.py --run as_feature      (about 30 minutes)
      uv run python scripts/12_followup_runs.py --run more_patients   (about 1 hour)
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

REPEATS = 10
MANY_PATIENTS = 20_000

# variant -> options for the patient generator
INSTRUMENTS = {
    "practice_100": {"instrument_strength": 1.0, "instrument_groups": 100},
    "practice_25": {"instrument_strength": 1.0, "instrument_groups": 25},
    "flaw_0.5": {"instrument_strength": 1.0, "instrument_flaw": 0.5},
    "flaw_1.0": {"instrument_strength": 1.0, "instrument_flaw": 1.0},
}
OFF_AND_LINEAR = (("none", 0.0), ("linear", 1.0))


def settings_for(run):
    """Every (variant, shape, strength, repeat) of one run."""
    if run == "realistic":
        return [
            (variant, shape, strength, repeat)
            for repeat in range(REPEATS)
            for variant in INSTRUMENTS
            for shape, strength in OFF_AND_LINEAR
        ]
    if run == "as_feature":
        return [
            ("ideal_as_feature", shape, strength, repeat)
            for repeat in range(REPEATS)
            for shape, strength, _ in grid.all_settings(repeat, repeat)
        ]
    if run == "more_patients":
        return [
            ("no_instrument", shape, strength, repeat)
            for repeat in range(REPEATS)
            for shape, strength in OFF_AND_LINEAR
        ]
    if run == "per_drug_noise":
        with_instrument = [
            ("ideal_instrument", shape, strength, repeat)
            for repeat in range(REPEATS)
            for shape, strength, _ in grid.all_settings(repeat, repeat)
        ]
        without = [
            (variant, shape, strength, repeat)
            for variant in ("no_instrument", "no_instrument_20000")
            for repeat in range(REPEATS)
            for shape, strength in OFF_AND_LINEAR
        ]
        second_part = (
            [
                ("ideal_instrument", shape, strength, repeat)
                for repeat in range(REPEATS, 2 * REPEATS)
                for shape, strength, _ in grid.all_settings(repeat, repeat)
            ]
            + [
                (variant, shape, strength, repeat)
                for repeat in range(REPEATS)
                for variant in INSTRUMENTS
                for shape, strength in OFF_AND_LINEAR
            ]
            + [
                ("ideal_instrument_0.5", shape, strength, repeat)
                for repeat in range(REPEATS)
                for shape, strength, _ in grid.all_settings(repeat, repeat)
            ]
        )
        return with_instrument + without + second_part
    raise SystemExit(f"unknown run {run!r}")


def run_one(run, variant, shape, strength, repeat, commit):
    """Simulate one dataset, fit the models of this run, return one row per model."""
    import numpy as np

    from stresstest.generator import GENERATOR_VERSION, make_patients
    from stresstest.joint_model import fit_joint_model
    from stresstest.scoring import convergence, crude_error, score

    warnings.filterwarnings("ignore")
    if run == "realistic":
        n, options = grid.N_PATIENTS, INSTRUMENTS[variant]
        fits = (("plain", {"link_errors": False}), ("joint", {"use_instrument": True}))
    elif run == "as_feature":
        n, options = grid.N_PATIENTS, {"instrument_strength": 1.0}
        fits = (("plain_with_instrument", {"link_errors": False, "instrument_as_feature": True}),)
    elif run == "per_drug_noise":
        n = MANY_PATIENTS if variant == "no_instrument_20000" else grid.N_PATIENTS
        with_instrument = not variant.startswith("no_instrument")
        if variant in INSTRUMENTS:
            options = INSTRUMENTS[variant]
        elif variant == "ideal_instrument_0.5":
            options = {"instrument_strength": 0.5}
        elif with_instrument:
            options = {"instrument_strength": 1.0}
        else:
            options = {}
        fits = (("joint_per_drug_noise", {"use_instrument": with_instrument, "noise_per_drug": True}),)
    else:
        n, options = MANY_PATIENTS, {}
        fits = (("plain", {"link_errors": False}), ("joint", {}))

    patients = make_patients(
        n, strength, "linear" if shape == "none" else shape, seed=repeat, **options
    )
    rows = []
    for model, fit_options in fits:
        start = time.time()
        effect_draws, rho_draws = fit_joint_model(patients, seed=repeat, **fit_options)
        low, high = np.percentile(rho_draws, [2.5, 97.5])
        row = {
            "generator_version": GENERATOR_VERSION,
            "host": grid.HOST,
            "code_commit": commit,
            "run": run,
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
    parser.add_argument("--run", required=True, choices=["realistic", "as_feature", "more_patients", "per_drug_noise"])
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    folder = grid.FOLDER / args.run
    results = folder / f"{grid.HOST}.csv"
    commit = grid.code_commit()
    done = already_done(folder)
    todo = [s for s in settings_for(args.run) if s not in done]
    print(f"run {args.run}, code {commit}, computer {grid.HOST}: {len(todo)} datasets to run -> {args.run}/{results.name}", flush=True)

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = [pool.submit(run_one, args.run, *setting, commit) for setting in todo]
        for count, job in enumerate(as_completed(jobs), start=1):
            rows = job.result()
            save(results, rows)
            summary = ", ".join(f"{r['model']} {r['bias_average']:+.2f}" for r in rows)
            first = rows[0]
            print(
                f"[{count}/{len(todo)}] {first['variant']:16s} {first['shape']:9s} strength {first['strength']:.1f} "
                f"repeat {first['repeat']:2d}: error in average effect {summary}; "
                f"{sum(r['seconds'] for r in rows)} s",
                flush=True,
            )
    print("finished", flush=True)
