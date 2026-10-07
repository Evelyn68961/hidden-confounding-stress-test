"""Does the published validation check notice a model misled by a hidden factor?

Treatment selection models built on health records are validated by comparing
patients who received the model's recommended drug ("concordant") with matched
patients who did not ("discordant"); see src/stresstest/validation.py. The
check passes when the observed benefit matches the predicted one.

That check uses the same records as the model, so a hidden factor can distort
it too. In the simulation the true benefit is known, so this script reports
all three for each dataset: predicted, observed and true.

It is run for two "models" on the 140 datasets of step 2:

  plain   the regression of step 3 (a drug effect that varies with the
          features; nothing assumed hidden). It has the same structure as the
          published models.
  truth   the true effects, used as if they were a model's predictions. This
          shows what the check reports for a model that is exactly right.

Results go to results/generator-v<version>/validation/<COMPUTER NAME>.csv.

Run:  uv run python scripts/09_validation_framework.py   (about 45 minutes)
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

FOLDER = grid.FOLDER / "validation"
RESULTS = FOLDER / f"{grid.HOST}.csv"


def run_one(shape, strength, repeat, commit):
    """Simulate one dataset, fit the plain model, and run the check twice."""
    from stresstest.generator import GENERATOR_VERSION, make_patients
    from stresstest.joint_model import fit_joint_model
    from stresstest.scoring import score
    from stresstest.validation import concordance_validation

    warnings.filterwarnings("ignore")
    start = time.time()
    patients = make_patients(
        grid.N_PATIENTS, strength, "linear" if shape == "none" else shape, seed=repeat
    )
    effect_draws, _ = fit_joint_model(patients, seed=repeat, link_errors=False)
    estimates = {
        "plain": effect_draws.reshape(len(effect_draws), -1).mean(axis=1),
        "truth": patients.true_effect,
    }
    rows = []
    for model, estimated_effect in estimates.items():
        row = {
            "generator_version": GENERATOR_VERSION,
            "host": grid.HOST,
            "code_commit": commit,
            "model": model,
            "shape": shape,
            "strength": strength,
            "repeat": repeat,
        }
        if model == "plain":
            scores = score(effect_draws, patients.true_effect)
            row["wrong_drug"], row["bias_average"] = scores["wrong_drug"], scores["bias_average"]
        else:
            row["wrong_drug"], row["bias_average"] = 0.0, 0.0
        row.update(
            concordance_validation(
                patients.features, patients.treated, patients.outcome,
                estimated_effect, patients.true_effect,
            )
        )
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
    parser.add_argument("--repeats", default=f"0-{grid.REPEATS - 1}")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    first_repeat, last_repeat = (int(x) for x in args.repeats.split("-"))

    commit = grid.code_commit()
    done = already_done()
    todo = [s for s in grid.all_settings(first_repeat, last_repeat) if s not in done]
    print(f"code {commit}, computer {grid.HOST}: {len(todo)} datasets to run -> validation/{RESULTS.name}", flush=True)

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = [pool.submit(run_one, *setting, commit) for setting in todo]
        for count, job in enumerate(as_completed(jobs), start=1):
            rows = job.result()
            save(rows)
            plain = rows[0]
            print(
                f"[{count}/{len(todo)}] {plain['shape']:9s} strength {plain['strength']:.1f} repeat {plain['repeat']:2d}: "
                f"predicted {plain['predicted_benefit']:.2f}, observed {plain['observed_benefit']:.2f}, "
                f"true {plain['true_benefit']:.2f}; {plain['seconds']} s",
                flush=True,
            )
    print("finished", flush=True)
