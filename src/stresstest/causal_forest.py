"""Fit a Bayesian causal forest (Hahn, Murray and Carvalho 2020) with stochtree."""

import numpy as np
from stochtree import BCFModel

from stresstest.generator import Patients


def fit_causal_forest(patients: Patients, seed: int = 0, draws: int = 1000) -> np.ndarray:
    """Return posterior draws of each patient's drug effect.

    The result has one row per patient and one column per draw.
    The forest is given only the recorded features, the drug and the outcome.
    It estimates the chance of each drug from the features itself.
    """
    model = BCFModel()
    model.sample(
        X_train=patients.features,
        Z_train=patients.treated,
        y_train=patients.outcome,
        num_gfr=10,  # fast warm-up sweeps
        num_burnin=0,
        num_mcmc=draws,
        general_params={"random_seed": seed},
    )
    return model.tau_hat_train
