"""Step 1: can a Bayesian causal forest recover the truth when nothing is hidden?

With the hidden factor switched off, the forest sees everything that drives
drug choice. It should estimate each patient's drug effect well. This is the
reference point for the later runs where the hidden factor is switched on.

Run:  uv run python scripts/01_causal_forest_no_hidden_factor.py
"""

import numpy as np

from stresstest.causal_forest import fit_causal_forest
from stresstest.generator import make_patients
from stresstest.scoring import score

patients = make_patients(n=5000, strength=0.0, seed=1)
effect_draws = fit_causal_forest(patients, seed=1)
result = score(effect_draws, patients.true_effect)

print(f"patients: {len(patients.outcome)}, posterior draws: {effect_draws.shape[1]}")
print(f"true average effect:      {patients.true_effect.mean():6.2f} mmol/mol")
print(f"estimated average effect: {effect_draws.mean():6.2f} mmol/mol")
print(f"spread of true effects (SD): {np.std(patients.true_effect):.2f} mmol/mol")
for name, value in result.items():
    print(f"{name:>16}: {value:6.3f}")
