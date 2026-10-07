"""Compare a model's estimated drug effects with the known truth."""

import numpy as np


def score(effect_draws: np.ndarray, true_effect: np.ndarray) -> dict:
    """Score one fitted model.

    `effect_draws` has one row per patient and one column per posterior draw.
    Each value is an estimate of GLP-1 minus SGLT2 for that patient
    (mmol/mol; negative means the GLP-1 drug is better).
    """
    estimate = effect_draws.mean(axis=1)
    lower, upper = np.percentile(effect_draws, [2.5, 97.5], axis=1)

    # The better drug is the one that lowers HbA1c more.
    truly_glp1 = true_effect < 0
    chosen_glp1 = estimate < 0
    wrong = truly_glp1 != chosen_glp1

    return {
        # Error in the average effect across all patients.
        "bias_average": estimate.mean() - true_effect.mean(),
        # Typical error in one patient's effect.
        "rmse_individual": np.sqrt(np.mean((estimate - true_effect) ** 2)),
        # Share of patients whose 95% interval contains their true effect.
        "coverage_95": np.mean((lower <= true_effect) & (true_effect <= upper)),
        # Share of patients the model would send to the worse drug.
        "wrong_drug": wrong.mean(),
        # HbA1c lowering lost per patient by following the model (mmol/mol).
        "hba1c_lost": np.mean(np.abs(true_effect) * wrong),
    }
