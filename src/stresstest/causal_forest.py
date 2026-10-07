"""Fit a Bayesian causal forest (Hahn, Murray and Carvalho 2020) with stochtree."""

import numpy as np
from stochtree import BCFModel

from stresstest.generator import Patients

CHAINS = 4  # independent runs, compared with each other to check the answer is stable
WARMUP = 500  # draws thrown away at the start of each chain
DRAWS = 2000  # draws kept from each chain


def fit_causal_forest(patients: Patients, seed: int = 0) -> np.ndarray:
    """Return posterior draws of each patient's drug effect.

    The result has three dimensions: patient, chain, draw.
    The forest is given only the recorded features, the drug and the outcome.
    It estimates the chance of each drug from the features itself.
    """
    model = BCFModel()
    model.sample(
        X_train=patients.features,
        Z_train=patients.treated,
        y_train=patients.outcome,
        num_gfr=10,  # fast sweeps that give each chain its own starting point
        num_burnin=WARMUP,
        num_mcmc=DRAWS,
        general_params={"random_seed": seed, "num_chains": CHAINS},
    )
    # stochtree stores the chains one after another: chain 1 first, then chain 2, and so on.
    n_patients = len(patients.outcome)
    return model.tau_hat_train.reshape(n_patients, CHAINS, DRAWS)
