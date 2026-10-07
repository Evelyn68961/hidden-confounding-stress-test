"""Step 3 check: can the joint model find a link that is clearly there?

In the diabetes simulation the joint model does not detect the hidden factor
(script 06). Before reading anything into that, the model has to be shown to
work when the task is easy. This script makes data straight from the model's
own assumptions, with a strong, known link (rho) between the unexplained part
of drug choice and the unexplained part of the outcome, and checks that the
fit recovers it.

The data here are abstract: two features, 20,000 patients, a very uneven
choice of drug, and a link of 0 or 0.6. They are not the diabetes patients.

Run:  uv run python scripts/07_joint_model_check.py   (about 20 minutes)
"""

import warnings

import numpy as np
import pandas as pd

from stresstest.generator import Patients
from stresstest.joint_model import fit_joint_model
from stresstest.scoring import score

warnings.filterwarnings("ignore")

N = 20_000
rng = np.random.default_rng(5)

print("true rho  model | estimated rho (95% interval) | error in avg effect | typical error | 95% int. cover")
for true_rho in (0.0, 0.6):
    features = rng.normal(0, 1, (N, 2))
    # Two errors per patient, linked with correlation true_rho.
    errors = rng.multivariate_normal([0, 0], [[1, true_rho], [true_rho, 1]], N)
    treated = (0.2 + 1.5 * features[:, 0] - 0.5 * features[:, 1] + errors[:, 0] > 0).astype(int)
    effect = 1.0 + 2.0 * features[:, 1]
    outcome = 3 + 2 * features[:, 0] + effect * treated + 4 * errors[:, 1]
    patients = Patients(
        features=pd.DataFrame(features, columns=["a", "b"]),
        treated=treated,
        outcome=outcome,
        true_effect=effect,
        true_propensity=np.zeros(N),  # not used here
        hidden=np.zeros(N),  # not used here
    )
    for name, link_errors in (("plain", False), ("joint", True)):
        effect_draws, rho_draws = fit_joint_model(patients, seed=1, link_errors=link_errors)
        scores = score(effect_draws, effect)
        low, high = np.percentile(rho_draws, [2.5, 97.5])
        print(
            f"{true_rho:8.1f}  {name} | {rho_draws.mean():5.2f} ({low:5.2f} to {high:5.2f})        | "
            f"{scores['bias_average']:6.2f}              | {scores['rmse_individual']:5.2f}         | "
            f"{scores['coverage_95']:5.1%}",
            flush=True,
        )
