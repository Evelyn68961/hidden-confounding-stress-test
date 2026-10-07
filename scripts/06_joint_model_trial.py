"""Step 3, first trial: does a joint model of drug choice and outcome help?

Fits two models to a handful of datasets and scores them against the truth:

  plain   a regression of the outcome with a drug effect that varies with the
          features. Like the causal forest, it assumes nothing is hidden.
  joint   the same regression plus a model of drug choice, with the two
          unexplained parts allowed to be linked (rho).

This is a trial on a few datasets, to see how long a fit takes and whether the
joint model can detect a hidden factor at all. It is not the full grid.

Run:  uv run python scripts/06_joint_model_trial.py
"""

import time
import warnings

import numpy as np

from stresstest.generator import make_patients
from stresstest.joint_model import fit_joint_model
from stresstest.scoring import score

warnings.filterwarnings("ignore")

N_PATIENTS = 5000
SEED = 0
SETTINGS = (("none", 0.0), ("linear", 1.0), ("threshold", 1.0), ("effect", 1.0))

print("setting          model | rho: mean (95% interval)  | error in avg  typical error  95% int.  worse  | seconds")
print("                       |                            | effect        per patient    cover     drug   |")
for shape, strength in SETTINGS:
    patients = make_patients(
        N_PATIENTS, strength, "linear" if shape == "none" else shape, seed=SEED
    )
    for name, link_errors in (("plain", False), ("joint", True)):
        start = time.time()
        effect_draws, rho_draws = fit_joint_model(patients, seed=SEED, link_errors=link_errors)
        scores = score(effect_draws, patients.true_effect)
        low, high = np.percentile(rho_draws, [2.5, 97.5])
        print(
            f"{shape:9s} {strength:3.1f}    {name} | {rho_draws.mean():5.2f} ({low:5.2f} to {high:5.2f})    | "
            f"{scores['bias_average']:6.2f}        {scores['rmse_individual']:5.2f}          "
            f"{scores['coverage_95']:5.1%}    {scores['wrong_drug']:5.1%}  | {time.time() - start:5.0f}",
            flush=True,
        )
