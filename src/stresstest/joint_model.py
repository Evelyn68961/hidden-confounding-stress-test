"""A joint model of drug choice and outcome, fitted with PyMC.

The causal forest models the outcome and treats drug choice as given. This
model describes both at once and lets their unexplained parts be linked:

    outcome     = baseline(features) + effect(features) x drug + outcome error
    drug choice = 1 if  choice(features) + choice error > 0

    the two errors are jointly normal with correlation rho

If nothing hidden drives both, rho is 0 and the two parts are separate
regressions. A hidden factor that pushes drug choice and outcome together
shows up as a non-zero rho, and the model then adjusts the estimated effect.

This is the classic "endogenous treatment" model. Here baseline, effect and
choice are all straight-line functions of the recorded features, which is the
simplest version. The data contain no instrument, so rho can only be learned
from the shape of the outcome's distribution within each drug group.
"""

import numpy as np
import pymc as pm
import pytensor.tensor as pt

from stresstest.generator import Patients

CHAINS = 4
WARMUP = 1000
DRAWS = 1000


def standardise(features):
    """Put every feature on the same scale: mean 0, SD 1."""
    values = features.to_numpy(dtype="float64")
    return (values - values.mean(axis=0)) / values.std(axis=0)


def fit_joint_model(
    patients: Patients, seed: int = 0, link_errors: bool = True, use_instrument: bool = False
):
    """Fit the joint model.

    Returns (effect_draws, rho_draws). `effect_draws` has dimensions
    patient, chain, draw, like the causal forest's. `rho_draws` has
    dimensions chain, draw.

    With `link_errors=False`, rho is fixed at 0. The model is then an ordinary
    regression with interactions, which serves as the comparison.

    With `use_instrument=True`, the instrument enters the drug-choice part and
    is left out of the outcome part. That exclusion is what lets the model
    tell a hidden factor from a real drug effect.
    """
    x = standardise(patients.features)
    n_features = x.shape[1]
    y_centre, y_scale = patients.outcome.mean(), patients.outcome.std()
    y = (patients.outcome - y_centre) / y_scale
    treated = patients.treated.astype("float64")

    with pm.Model():
        # Outcome: baseline response and drug effect, each a straight line in the features.
        baseline_level = pm.Normal("baseline_level", 0, 1)
        baseline_slopes = pm.Normal("baseline_slopes", 0, 1, shape=n_features)
        effect_level = pm.Normal("effect_level", 0, 1)
        effect_slopes = pm.Normal("effect_slopes", 0, 1, shape=n_features)
        noise = pm.HalfNormal("noise", 1)

        # Drug choice: a probit regression on the same features.
        choice_level = pm.Normal("choice_level", 0, 1.5)
        choice_slopes = pm.Normal("choice_slopes", 0, 1, shape=n_features)

        # The link between the two unexplained parts.
        if link_errors:
            rho = pm.Uniform("rho", -0.95, 0.95)
        else:
            rho = pm.Deterministic("rho", pt.zeros(()))

        effect = effect_level + pt.dot(x, effect_slopes)
        expected = baseline_level + pt.dot(x, baseline_slopes) + effect * treated
        residual = (y - expected) / noise

        pm.Normal("outcome", expected, noise, observed=y)

        # Given a patient's outcome error, the chance of the GLP-1 drug shifts by rho.
        choice = choice_level + pt.dot(x, choice_slopes)
        if use_instrument:
            instrument_slope = pm.Normal("instrument_slope", 0, 1)
            choice = choice + instrument_slope * patients.instrument
        shifted = (choice + rho * residual) / pt.sqrt(1 - rho**2)
        chance = pm.math.invprobit(shifted)
        pm.Bernoulli("drug", p=pt.clip(chance, 1e-9, 1 - 1e-9), observed=treated)

        pm.Deterministic("effect", effect * y_scale)  # back to mmol/mol

        fit = pm.sample(
            draws=DRAWS,
            tune=WARMUP,
            chains=CHAINS,
            cores=1,
            random_seed=seed,
            progressbar=False,
            target_accept=0.9,
        )

    # pymc gives chain, draw, patient; the scoring wants patient, chain, draw.
    effect_draws = fit.posterior["effect"].to_numpy().transpose(2, 0, 1)
    rho_draws = fit.posterior["rho"].to_numpy()
    return effect_draws, rho_draws
