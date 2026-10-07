"""Compare a model's estimated drug effects with the known truth."""

import arviz as az
import numpy as np


def score(effect_draws: np.ndarray, true_effect: np.ndarray) -> dict:
    """Score one fitted model.

    `effect_draws` has three dimensions: patient, chain, draw.
    Each value is an estimate of GLP-1 minus SGLT2 for that patient
    (mmol/mol; negative means the GLP-1 drug is better).
    """
    # Pool the chains: one row per patient, one column per draw.
    pooled = effect_draws.reshape(len(effect_draws), -1)
    estimate = pooled.mean(axis=1)
    lower, upper = np.percentile(pooled, [2.5, 97.5], axis=1)

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


def convergence(effect_draws: np.ndarray) -> dict:
    """Check that the chains agree, using R-hat (the same check Stan reports).

    R-hat is close to 1 when the chains give the same answer.
    Values above 1.01 mean the chains have not settled on one answer.
    """
    # arviz wants the dimensions in the order chain, draw, patient.
    by_chain = effect_draws.transpose(1, 2, 0)
    rhat_each_patient = az.rhat(by_chain)
    # The average effect across patients, one value per chain and draw.
    rhat_average = float(az.rhat(by_chain.mean(axis=2)))

    return {
        "rhat_average_effect": rhat_average,
        "rhat_worst_patient": float(rhat_each_patient.max()),
        "share_patients_rhat_above_1.01": float(np.mean(rhat_each_patient > 1.01)),
    }
