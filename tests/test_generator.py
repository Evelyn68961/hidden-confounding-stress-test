"""Checks that the simulated patients behave as the generator says they do."""

import numpy as np
import pytest

from stresstest.generator import (
    AGE,
    BMI,
    EGFR,
    HBA1C,
    HBA1C_PER_UNIT,
    OTHER_DRUGS,
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
    typical_man = f.assign(
        female=0, age=AGE, hba1c=HBA1C, egfr=EGFR, bmi=BMI, other_drugs=OTHER_DRUGS
    )
    assert np.allclose(true_effect(typical_man), 1.67)
    # Women do 4.4 mmol/mol better on the GLP-1 drug than otherwise identical men.
    assert np.allclose(true_effect(f.assign(female=1)) - true_effect(f.assign(female=0)), -4.4)
    # Older patients do better on the GLP-1 drug.
    assert np.allclose(true_effect(f.assign(age=f["age"] + 10)) - true_effect(f), -1.2)


def test_no_feature_moves_drug_choice_alone():
    """A feature that moved drug choice but not the outcome would act as an instrument."""
    patients = make_patients(N, strength=0.0)
    f = patients.features
    for name in f.columns:
        related_to_choice = abs(np.corrcoef(f[name], patients.treated)[0, 1]) > 0.01
        related_to_outcome = abs(np.corrcoef(f[name], patients.outcome)[0, 1]) > 0.01
        assert related_to_outcome or not related_to_choice, name


def test_cohort_resembles_the_published_one():
    """Compare with Table 1 and the Results of Cardoso et al., Diabetologia 2024."""
    patients = make_patients(N, strength=0.0)
    f, glp1 = patients.features, patients.treated == 1
    assert glp1.mean() == pytest.approx(0.25, abs=0.01)
    assert f["female"][glp1].mean() == pytest.approx(0.467, abs=0.01)
    assert f["female"][~glp1].mean() == pytest.approx(0.391, abs=0.01)
    assert f["age"][glp1].mean() == pytest.approx(57.7, abs=0.3)
    assert f["age"][~glp1].mean() == pytest.approx(58.4, abs=0.3)
    assert f["bmi"][glp1].mean() == pytest.approx(37.3, abs=0.4)
    assert f["bmi"][~glp1].mean() == pytest.approx(33.7, abs=0.4)
    assert f["egfr"][glp1].mean() == pytest.approx(92.0, abs=0.5)
    assert f["hba1c"][glp1].mean() == pytest.approx(78.6, abs=0.5)
    assert f["hba1c"][~glp1].mean() == pytest.approx(76.9, abs=0.5)
    # Five or more drug classes ever: 28.1% of the GLP-1 group, 17.4% of the SGLT2 group.
    assert (f["drug_classes"][glp1] == 5).mean() == pytest.approx(0.281, abs=0.02)
    assert (f["drug_classes"][~glp1] == 5).mean() == pytest.approx(0.174, abs=0.02)
    # Three or more other current drugs: 14.6% and 11.2%.
    assert (f["other_drugs"][glp1] >= 3).mean() == pytest.approx(0.146, abs=0.02)
    assert (f["other_drugs"][~glp1] >= 3).mean() == pytest.approx(0.112, abs=0.02)


def test_outcome_resembles_the_published_one_on_both_drugs():
    """HbA1c change: -12.0 (SD 15.3) on the SGLT2 drug, -11.7 (SD 17.6) on the GLP-1 drug."""
    patients = make_patients(N, strength=0.0)
    glp1 = patients.treated == 1
    assert patients.outcome[~glp1].mean() == pytest.approx(-12.0, abs=0.2)
    assert patients.outcome[~glp1].std() == pytest.approx(15.3, abs=0.3)
    assert patients.outcome[glp1].mean() == pytest.approx(-11.7, abs=0.3)
    assert patients.outcome[glp1].std() == pytest.approx(17.6, abs=0.4)


def test_true_effects_resemble_the_published_ones():
    patients = make_patients(N, strength=0.0)
    effect, hba1c = patients.true_effect, patients.features["hba1c"]
    # Average 0.1 in favour of the GLP-1 drug.
    assert effect.mean() == pytest.approx(-0.1, abs=0.1)
    # SGLT2 better by more than 3 for 17.5%; GLP-1 better by more than 3 for 20.3%.
    assert (effect > 3).mean() == pytest.approx(0.175, abs=0.015)
    assert (effect < -3).mean() == pytest.approx(0.203, abs=0.015)
    # SGLT2 the better drug for 32% with a low starting HbA1c and 67% with a high one.
    assert (effect[hba1c < 64] > 0).mean() == pytest.approx(0.32, abs=0.04)
    assert (effect[hba1c >= 86] > 0).mean() == pytest.approx(0.67, abs=0.05)


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
