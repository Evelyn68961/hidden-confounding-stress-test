"""Check that two computers sharing the step 2 run agree with each other.

The run is split by repeat: one computer does repeats 0-9, another 10-19. If
the computers differed in some hidden way, it would look like a difference
between those two ranges and nothing would reveal it. This script closes that
gap in three ways.

  fingerprint  Simulates a fixed set of datasets and saves a short code
               (a hash) for each. Takes seconds. If two computers save the
               same codes, they are simulating identical patients.

  refit        Fits three datasets that belong to the OTHER computer's range
               and saves the scores in a separate file. Takes about 20 to 40
               minutes. Comparing them with the other computer's own results
               for the same three datasets shows whether the sampler gives
               the same answer on both.

  compare      Reads everything saved so far and prints the comparison:
               the fingerprints, the refits, and the scores by computer.

Run:
  uv run python scripts/04_cross_check.py fingerprint
  uv run python scripts/04_cross_check.py refit --repeat 0
  uv run python scripts/04_cross_check.py compare

The first two write only files named after this computer. They never touch
the main results file. See docs/RUNNER.md.
"""

import argparse
import csv
import hashlib
import importlib.metadata
import importlib.util
import platform
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

from stresstest.generator import GENERATOR_VERSION, SHAPES, make_patients

# The grid script is loaded as a module so that a refit goes through exactly
# the same code as a fit in the main run.
_spec = importlib.util.spec_from_file_location(
    "grid", Path(__file__).parent / "03_causal_forest_grid.py"
)
grid = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(grid)

FOLDER = grid.FOLDER
HOST = grid.HOST
# Kept in a subfolder so the main run, which reads every file in FOLDER to see
# what is already done, never mistakes a check for a finished fit.
CHECKS = FOLDER / "crosscheck"
FINGERPRINTS = CHECKS / f"{HOST}_fingerprints.csv"
REFITS = CHECKS / f"{HOST}_refits.csv"

# Datasets fingerprinted on every computer: one repeat from each range.
FINGERPRINT_REPEATS = (0, 10)
# Settings refitted: nothing hidden, and the two most different shapes at full strength.
REFIT_SETTINGS = (("none", 0.0), ("linear", 1.0), ("effect", 1.0))
SCORES = ("bias_average", "rmse_individual", "coverage_95", "wrong_drug", "hba1c_lost")


def environment():
    return {
        "python": platform.python_version(),
        "numpy": importlib.metadata.version("numpy"),
        "stochtree": importlib.metadata.version("stochtree"),
        "system": platform.platform(),
        "processor": platform.processor(),
    }


def fingerprint(shape, strength, repeat):
    """A short code that changes if any simulated number changes."""
    patients = make_patients(
        grid.N_PATIENTS, strength, "linear" if shape == "none" else shape, seed=repeat
    )
    digest = hashlib.sha256()
    digest.update(patients.features.to_numpy(dtype="float64").tobytes())
    digest.update(patients.treated.astype("int64").tobytes())
    digest.update(patients.outcome.astype("float64").tobytes())
    return digest.hexdigest()[:16]


def write_rows(file, rows):
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_rows(folder, pattern):
    """All rows from the files matching a pattern, keyed by computer."""
    by_host = {}
    for file in sorted(folder.glob(pattern)):
        with file.open(newline="") as rows:
            by_host[file.stem.split("_")[0]] = list(csv.DictReader(rows))
    return by_host


def do_fingerprint():
    rows = []
    for repeat in FINGERPRINT_REPEATS:
        for shape, strength, _ in grid.all_settings(repeat, repeat):
            rows.append(
                {
                    "generator_version": GENERATOR_VERSION,
                    "host": HOST,
                    "shape": shape,
                    "strength": strength,
                    "repeat": repeat,
                    "fingerprint": fingerprint(shape, strength, repeat),
                    **environment(),
                }
            )
    write_rows(FINGERPRINTS, rows)
    print(f"{len(rows)} fingerprints saved to {FINGERPRINTS.name}")


def do_refit(repeat):
    commit = grid.code_commit()
    rows = []
    for shape, strength in REFIT_SETTINGS:
        print(f"refitting {shape} strength {strength} repeat {repeat} ...", flush=True)
        rows.append(grid.run_one(shape, strength, repeat, commit))
        write_rows(REFITS, rows)  # saved after each fit
    print(f"{len(rows)} refits saved to {REFITS.name}")


def do_compare():
    problems = 0

    print("1. Do the computers simulate identical patients?")
    prints = read_rows(CHECKS, "*_fingerprints.csv")
    if len(prints) < 2:
        print(f"   only {len(prints)} computer(s) have saved fingerprints; nothing to compare yet")
    else:
        codes = defaultdict(dict)
        for host, rows in prints.items():
            for r in rows:
                codes[(r["shape"], r["strength"], r["repeat"])][host] = r["fingerprint"]
        different = [key for key, by_host in codes.items() if len(set(by_host.values())) > 1]
        print(f"   computers: {', '.join(prints)}; datasets compared: {len(codes)}")
        print(f"   datasets that differ: {len(different)}")
        problems += len(different)
        for host, rows in prints.items():
            print(f"   {host}: python {rows[0]['python']}, numpy {rows[0]['numpy']}, "
                  f"stochtree {rows[0]['stochtree']}, {rows[0]['processor']}")

    print("\n2. Does the sampler give the same answer on both computers?")
    refits = read_rows(CHECKS, "*_refits.csv")
    # Every fit in the main results, keyed by setting.
    owners = {}
    for rows in read_rows(FOLDER, "*.csv").values():
        for r in rows:
            owners[(r["shape"], float(r["strength"]), int(r["repeat"]))] = r
    pairs = 0
    for host, rows in refits.items():
        for r in rows:
            key = (r["shape"], float(r["strength"]), int(r["repeat"]))
            own = owners.get(key)
            if own is None or own["host"] == host:
                continue
            pairs += 1
            gaps = {s: float(r[s]) - float(own[s]) for s in SCORES}
            largest = max(gaps, key=lambda s: abs(gaps[s]))
            same = all(abs(g) < 1e-9 for g in gaps.values())
            print(f"   {key[0]:9s} strength {key[1]:.1f} repeat {key[2]:2d}: "
                  f"{host} against {own['host']}: "
                  + ("identical" if same else f"largest gap {gaps[largest]:+.4f} in {largest}"))
            print(f"      rmse {float(r['rmse_individual']):.4f} against {float(own['rmse_individual']):.4f}; "
                  f"wrong drug {float(r['wrong_drug']):.4f} against {float(own['wrong_drug']):.4f}")
    if pairs == 0:
        print("   no dataset has been fitted on two computers yet")

    print("\n3. Scores by computer, for each setting (mean, SD across repeats)")
    by_setting = defaultdict(lambda: defaultdict(list))
    commits = defaultdict(set)
    for key, r in owners.items():
        by_setting[(key[0], key[1])][r["host"]].append(float(r["rmse_individual"]))
        commits[r["host"]].add(r["code_commit"])
    for (shape, strength), hosts in sorted(by_setting.items()):
        parts = []
        for host, values in sorted(hosts.items()):
            spread = f"{stdev(values):.2f}" if len(values) > 1 else "n/a"
            parts.append(f"{host}: {mean(values):.2f} (SD {spread}, n={len(values)})")
        print(f"   {shape:9s} strength {strength:.1f}  rmse  " + " | ".join(parts))
    for host, found in commits.items():
        print(f"   {host}: code commit(s) {', '.join(sorted(found))}")
    print("   The two computers ran different repeats, so their means differ by chance.")
    print("   A gap much larger than the SDs divided by the square root of n would need explaining.")

    print(f"\ndatasets that differ between computers: {problems}")
    return problems


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["fingerprint", "refit", "compare"])
    parser.add_argument("--repeat", type=int, help="for refit: a repeat from the other computer's range")
    args = parser.parse_args()

    if args.action == "fingerprint":
        do_fingerprint()
    elif args.action == "refit":
        if args.repeat is None:
            raise SystemExit("refit needs --repeat, a repeat from the other computer's range")
        do_refit(args.repeat)
    else:
        sys.exit(1 if do_compare() else 0)
