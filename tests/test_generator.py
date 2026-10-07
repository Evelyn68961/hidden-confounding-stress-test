"""Checks that the simulated patients behave as the generator says they do."""

import numpy as np
import pytest

from stresstest.generator import (
    BMI,
    EGFR,
    HBA1C,
    HBA1C_PER_UNIT,
    SHAPES,
    make_patients,
    true_effect,
)
from stresstest.scoring import crude_error

N = 200_000  # large, so chance differences are small


def test_same_seed_gives_same_patients():
    a = make_patients(1000, strength=1.0, seed=3)
    b = make_patients(1000, strength=1.0, seed=3)
    assert np.array_equal(a.outcome, b.outcome)


def test_true_effect_follows_the_stated_rule():
    f = make_patients(1000, strength=0.0).features
    typical_man = f.assign(female=0, hba1c=HBA1C, egfr=EGFR, bmi=BMI)
    assert np.allclose(true_effect(typical_man), 1.7)
    # Women do 4.4 mmol/mol better on the GLP-1 drug than otherwise identical men.
    assert np.allclose(true_effect(f.assign(female=1)) - true_effect(f.assign(female=0)), -4.4)


def test_bmi_affects_both_drug_choice_and_outcome():
    """BMI must not move drug choice alone, or it would act as an instrument."""
    patients = make_patients(N, strength=0.0)
    f = patients.features
    assert np.corrcoef(f["bmi"], patients.treated)[0, 1] > 0.1
    assert np.allclose(true_effect(f.assign(bmi=f["bmi"] + 1)) - true_effect(f), 0.15)


def test_cohort_resembles_the_published_one():
    """Compare with Table 1 and the Results of Cardoso et al., Diabetologia 2024."""
    patients = make_patients(N, strength=0.0)
    f, glp1 = patients.features, patients.treated == 1
    assert glp1.mean() == pytest.approx(0.25, abs=0.01)
    assert f["female"][glp1].mean() == pytest.approx(0.467, abs=0.01)
    assert f["female"][~glp1].mean() == pytest.approx(0.391, abs=0.01)
    assert f["bmi"][glp1].mean() == pytest.approx(37.3, abs=0.4)
    assert f["bmi"][~glp1].mean() == pytest.approx(33.7, abs=0.4)
    assert f["egfr"][glp1].mean() == pytest.approx(92.0, abs=0.5)
    assert f["hba1c"][glp1].mean() == pytest.approx(78.6, abs=0.5)
    assert f["hba1c"][~glp1].mean() == pytest.approx(76.9, abs=0.5)
    # HbA1c change on the SGLT2 drug: mean -12.0, SD 15.3.
    assert patients.outcome[~glp1].mean() == pytest.approx(-12.0, abs=0.3)
    assert patients.outcome[~glp1].std() == pytest.approx(15.3, abs=0.5)
    # True effects: average near zero; SGLT2 better by more than 3 for 17.5%,
    # GLP-1 better by more than 3 for 20.3%.
    effect = patients.true_effect
    assert effect.mean() == pytest.approx(-0.1, abs=0.1)
    assert (effect > 3).mean() == pytest.approx(0.175, abs=0.03)
    assert (effect < -3).mean() == pytest.approx(0.203, abs=0.03)


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
    assert crude_error(on) > crude_error(off) + 1.0


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
