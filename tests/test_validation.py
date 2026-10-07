"""Checks on the concordant-against-discordant validation."""

import numpy as np
import pytest

from stresstest.generator import make_patients
from stresstest.validation import concordance_validation

N = 100_000


def test_a_perfect_model_passes_when_nothing_is_hidden():
    """Given the true effects as the 'model', predicted, observed and true benefit agree."""
    patients = make_patients(N, strength=0.0, seed=2)
    result = concordance_validation(
        patients.features, patients.treated, patients.outcome,
        estimated_effect=patients.true_effect, true_effect=patients.true_effect,
    )
    assert result["predicted_benefit"] == pytest.approx(result["true_benefit"])
    assert result["observed_benefit"] == pytest.approx(result["true_benefit"], abs=0.4)
    assert result["true_benefit"] > 1.0
    assert result["pairs"] > N * 0.2


def test_a_useless_model_shows_no_benefit():
    """Random 'effects' carry no information, so the true benefit is near zero."""
    patients = make_patients(N, strength=0.0, seed=2)
    noise = np.random.default_rng(0).normal(0, 3, N)
    result = concordance_validation(
        patients.features, patients.treated, patients.outcome,
        estimated_effect=noise, true_effect=patients.true_effect,
    )
    assert abs(result["true_benefit"]) < 0.3
    assert abs(result["observed_benefit"]) < 0.5
