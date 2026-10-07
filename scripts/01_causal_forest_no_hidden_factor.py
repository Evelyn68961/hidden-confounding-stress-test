"""Step 1: can a Bayesian causal forest recover the truth when nothing is hidden?

With the hidden factor switched off, the forest sees everything that drives
drug choice. It should estimate each patient's drug effect well. This is the
reference point for the later runs where the hidden factor is switched on.

Run:  uv run python scripts/01_causal_forest_no_hidden_factor.py
"""

import numpy as np

from stresstest.causal_forest import fit_causal_forest
from stresstest.generator import make_patients
from stresstest.scoring import convergence, score

patients = make_patients(n=5000, strength=0.0, seed=1)
effect_draws = fit_causal_forest(patients, seed=1)
n_patients, n_chains, n_draws = effect_draws.shape

print(f"patients: {n_patients}, chains: {n_chains}, draws per chain: {n_draws}")
print(f"true average effect:      {patients.true_effect.mean():6.2f} mmol/mol")
print(f"estimated average effect: {effect_draws.mean():6.2f} mmol/mol")
print(f"spread of true effects (SD): {np.std(patients.true_effect):.2f} mmol/mol")

print("\nscores against the truth")
for name, value in score(effect_draws, patients.true_effect).items():
    print(f"{name:>32}: {value:6.3f}")

print("\ndo the chains agree?")
for name, value in convergence(effect_draws).items():
    print(f"{name:>32}: {value:6.3f}")
