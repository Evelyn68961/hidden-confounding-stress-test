"""Step 1b: what does each strength and shape of the hidden factor do to the data?

No model is fitted here. The script only describes the simulated patients:
how unevenly the hidden factor is spread between the two drug groups, how much
of the variation in the outcome it explains, and how wrong the crudest method
(comparing the two drug groups directly) becomes.

Run:  uv run python scripts/02_what_the_hidden_factor_does.py
"""

from stresstest.generator import SHAPES, make_patients
from stresstest.scoring import crude_error

N = 400_000  # large, so chance differences are small
STRENGTHS = (0.0, 0.5, 1.0)
SEED = 7

print("shape      strength | top 16% of hidden factor: | outcome variance | extra error of a")
print("                    | GLP-1 group  SGLT2 group  | from hidden      | crude comparison")
for shape in SHAPES:
    # The same seed gives the same patients and features at every strength,
    # so the strength-0 run is the like-for-like reference.
    reference = make_patients(N, strength=0.0, shape=shape, seed=SEED)
    for strength in STRENGTHS:
        patients = make_patients(N, strength=strength, shape=shape, seed=SEED)
        on_glp1 = patients.treated == 1
        high = patients.hidden > 1.0
        variance_share = 1 - reference.outcome.var() / patients.outcome.var()
        # The crude comparison is already a little wrong at strength 0, because the
        # groups differ in recorded features. Subtract that to isolate the hidden factor.
        extra_error = crude_error(patients) - crude_error(reference)
        print(
            f"{shape:10s} {strength:8.1f} | "
            f"{high[on_glp1].mean():10.0%} {high[~on_glp1].mean():12.0%}  | "
            f"{variance_share:15.1%}  | {extra_error:6.2f} mmol/mol"
        )
