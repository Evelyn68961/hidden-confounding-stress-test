"""Checks that the simulated patients behave as the generator says they do."""

import numpy as np
import pytest

from stresstest.generator import HBA1C_PER_UNIT, SHAPES, make_patients, true_effect

N = 200_000  # large, so chance differences are small


def difference_in_means(patients):
    """Average outcome on the GLP-1 drug minus average outcome on the SGLT2 drug."""
    on_glp1 = patients.treated == 1
    return patients.outcome[on_glp1].mean() - patients.outcome[~on_glp1].mean()


def test_same_seed_gives_same_patients():
    a = make_patients(1000, strength=1.0, seed=3)
    b = make_patients(1000, strength=1.0, seed=3)
    assert np.array_equal(a.outcome, b.outcome)


def test_true_effect_follows_the_stated_rule():
    patients = make_patients(1000, strength=0.0)
    f = patients.features
    man_average_kidney = (f["female"] == 0) & (abs(f["egfr"] - 85) < 0.5)
    assert np.allclose(true_effect(f[man_average_kidney]), 1.0, atol=0.05)
    # Women do 4 mmol/mol better on the GLP-1 drug than men with the same kidney function.
    women = f.assign(female=1)
    men = f.assign(female=0)
    assert np.allclose(true_effect(women) - true_effect(men), -4.0)


def test_hidden_factor_is_off_at_zero_strength():
    patients = make_patients(N, strength=0.0)
    assert abs(np.corrcoef(patients.hidden, patients.treated)[0, 1]) < 0.01
    assert abs(np.corrcoef(patients.hidden, patients.outcome)[0, 1]) < 0.01


def test_hidden_factor_drives_drug_choice_when_on():
    patients = make_patients(N, strength=1.0)
    assert np.corrcoef(patients.hidden, patients.treated)[0, 1] > 0.3


@pytest.mark.parametrize("shape", ["linear", "threshold"])
def test_hidden_factor_biases_a_naive_comparison(shape):
    """With the hidden factor on, comparing the two drug groups gives the wrong answer."""
    off = make_patients(N, strength=0.0, shape=shape)
    on = make_patients(N, strength=1.0, shape=shape)
    error_off = difference_in_means(off) - off.true_effect[off.treated == 1].mean()
    error_on = difference_in_means(on) - on.true_effect[on.treated == 1].mean()
    assert abs(error_on) > abs(error_off) + 1.0


@pytest.mark.parametrize("shape", ["linear", "threshold"])
def test_shapes_add_the_same_spread_to_the_outcome(shape):
    """The linear and threshold shapes are scaled to be equally strong."""
    off = make_patients(N, strength=0.0, shape=shape)
    on = make_patients(N, strength=1.0, shape=shape)
    added_variance = on.outcome.var() - off.outcome.var()
    # Not exact: drug choice also changes with the hidden factor.
    assert added_variance == pytest.approx(HBA1C_PER_UNIT**2, rel=0.25)


def test_unknown_shape_is_rejected():
    assert "effect" in SHAPES
    with pytest.raises(ValueError):
        make_patients(100, strength=1.0, shape="curved")
