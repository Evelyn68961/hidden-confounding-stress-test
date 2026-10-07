"""Make artificial type 2 diabetes patients whose true drug effects are known.

Each patient starts one of two drugs:

    treated = 0  ->  SGLT2 inhibitor
    treated = 1  ->  GLP-1 receptor agonist

The outcome is the change in HbA1c after 12 months, in mmol/mol.
A more negative number is a better result.

A hidden factor (think of frailty) can push both the choice of drug and the
outcome. The models never see it. Two settings control it:

    strength  how strong the hidden factor is (0 switches it off)
    shape     how it acts on the outcome: "linear", "threshold" or "effect"

Where the numbers come from
---------------------------
The patients are tuned to resemble the published UK cohort in Cardoso et al.,
Diabetologia 2024;67:822-836 (people starting an SGLT2 inhibitor or a GLP-1
receptor agonist in CPRD). No patient data were used, only figures printed in
that paper. See docs/calibration.md for each number, its source and how
closely the simulation reproduces it. Numbers marked "chosen" there have no
published source.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

SHAPES = ("linear", "threshold", "effect")

# Typical patient, used as the reference point in the formulas below.
AGE, HBA1C, BMI, EGFR = 58, 77, 34.6, 94

# What one unit of `strength` means.
LOG_ODDS_PER_UNIT = 1.0  # shift in the log-odds of getting the GLP-1 drug, per SD of the hidden factor
HBA1C_PER_UNIT = 5.0  # shift in the outcome (mmol/mol), per SD of the hidden factor

NOISE_SD = 12.5  # unexplained variation in HbA1c change (mmol/mol)


@dataclass
class Patients:
    """One simulated dataset.

    `features` is what a model is allowed to see. Everything under
    "truth" is known only because the data are simulated.
    """

    features: pd.DataFrame
    treated: np.ndarray
    outcome: np.ndarray
    # truth
    true_effect: np.ndarray  # GLP-1 minus SGLT2, given the recorded features
    true_propensity: np.ndarray  # chance of getting the GLP-1 drug, hidden factor included
    hidden: np.ndarray


def true_effect(features: pd.DataFrame) -> np.ndarray:
    """Difference in HbA1c change, GLP-1 minus SGLT2, for each patient.

    Negative means the GLP-1 drug lowers HbA1c more for that patient.
    Women do better on the GLP-1 drug. A higher starting HbA1c, better kidney
    function and a higher BMI each favour the SGLT2 drug.
    """
    return (
        1.7
        - 4.4 * features["female"]
        + 0.08 * (features["hba1c"] - HBA1C)
        + 0.08 * (features["egfr"] - EGFR)
        + 0.15 * (features["bmi"] - BMI)
    ).to_numpy()


def baseline_response(features: pd.DataFrame) -> np.ndarray:
    """HbA1c change on the SGLT2 drug, before noise and the hidden factor.

    A higher starting HbA1c falls further. Older patients respond a little more.
    """
    return (
        -12.0
        - 0.5 * (features["hba1c"] - HBA1C)
        - 0.05 * (features["age"] - AGE)
    ).to_numpy()


def hidden_effect_on_outcome(hidden, treated, strength, shape):
    """What the hidden factor adds to the outcome, in mmol/mol."""
    size = strength * HBA1C_PER_UNIT
    if shape == "linear":
        # Every extra SD of the hidden factor worsens the result by the same amount.
        return size * hidden
    if shape == "threshold":
        # Only the top 16% (more than 1 SD above average) are affected.
        # Scaled so the effect has the same spread as the linear shape.
        hit = (hidden > 1.0).astype(float)
        return size * (hit - hit.mean()) / hit.std()
    if shape == "effect":
        # The hidden factor changes how well the GLP-1 drug works,
        # not the response on the SGLT2 drug.
        return size * hidden * treated
    raise ValueError(f"shape must be one of {SHAPES}, got {shape!r}")


def make_patients(n: int, strength: float, shape: str = "linear", seed: int = 0) -> Patients:
    """Simulate `n` patients."""
    rng = np.random.default_rng(seed)

    features = pd.DataFrame(
        {
            "age": rng.normal(AGE, 11, n).clip(25, 90),
            "female": rng.binomial(1, 0.41, n),
            "hba1c": 53 + rng.gamma(shape=2.0, scale=12.0, size=n),  # mmol/mol at the start
            "bmi": rng.normal(BMI, 7, n).clip(18, 65),
            "egfr": rng.normal(EGFR, 17, n).clip(30, 140),
        }
    )
    hidden = rng.normal(0, 1, n)

    # Drug choice. About one patient in four gets the GLP-1 drug. Women, heavier
    # patients and patients with a higher HbA1c get it more often; patients with
    # good kidney function get it less often. The hidden factor pushes towards it.
    log_odds = (
        -1.3
        + 0.31 * features["female"]
        + 0.073 * (features["bmi"] - BMI)
        - 0.009 * (features["egfr"] - EGFR)
        + 0.006 * (features["hba1c"] - HBA1C)
        + strength * LOG_ODDS_PER_UNIT * hidden
    ).to_numpy()
    propensity = 1 / (1 + np.exp(-log_odds))
    treated = rng.binomial(1, propensity)

    effect = true_effect(features)
    outcome = (
        baseline_response(features)
        + effect * treated
        + hidden_effect_on_outcome(hidden, treated, strength, shape)
        + rng.normal(0, NOISE_SD, n)
    )

    return Patients(
        features=features,
        treated=treated,
        outcome=outcome,
        true_effect=effect,
        true_propensity=propensity,
        hidden=hidden,
    )
