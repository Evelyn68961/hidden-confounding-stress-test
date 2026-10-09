"""Re-compute the key results with methods that share no code with the PyMC models.

  OLS            least squares with drug x feature terms  -> should match the "plain" model
  control fn     probit first stage by maximum likelihood, then the generalised
                 residual added to the outcome regression (Heckman's two-step
                 correction)                                -> should match the "joint" model
  Wald           cov(outcome, instrument) / cov(drug, instrument), a textbook check
                 on how much a direct effect of the instrument is magnified

Only numpy and scipy are used. The patients come from the repo's generator.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

from stresstest.generator import make_patients

N = 5000


def design(patients, extra=None):
    x = patients.features.to_numpy(float)
    x = (x - x.mean(0)) / x.std(0)
    if extra is not None:
        e = (extra - extra.mean()) / extra.std()
        x = np.column_stack([x, e])
    return x


def ols_effect(patients, x, more=None):
    """Average of the estimated effect over patients, from y ~ 1 + x + d + d*x (+ more)."""
    d = patients.treated.astype(float)
    cols = [np.ones(len(d)), x, d, d[:, None] * x]
    if more is not None:
        cols.append(more)
    a = np.column_stack(cols)
    beta, *_ = np.linalg.lstsq(a, patients.outcome, rcond=None)
    k = x.shape[1]
    effect = beta[1 + k] + x @ beta[2 + k: 2 + 2 * k]
    return effect.mean()


def probit(z, d):
    def nll(g):
        p = norm.cdf(z @ g).clip(1e-10, 1 - 1e-10)
        return -(d * np.log(p) + (1 - d) * np.log(1 - p)).sum()
    return minimize(nll, np.zeros(z.shape[1]), method="BFGS").x


def control_function(patients):
    x = design(patients)
    d = patients.treated.astype(float)
    z = np.column_stack([np.ones(N if len(d) == N else len(d)), x, patients.instrument])
    index = z @ probit(z, d)
    pdf, cdf = norm.pdf(index), norm.cdf(index).clip(1e-10, 1 - 1e-10)
    residual = d * pdf / cdf - (1 - d) * pdf / (1 - cdf)
    return ols_effect(patients, x, more=residual)


def errors(n, strength, **options):
    rows = []
    for seed in range(10):
        p = make_patients(n, strength, "linear", seed=seed, **options)
        truth = p.true_effect.mean()
        x = design(p)
        row = {"ols": ols_effect(p, x) - truth}
        if options.get("instrument_strength"):
            row["ols_instrument_as_feature"] = ols_effect(p, design(p, p.instrument)) - truth
            row["control_function"] = control_function(p) - truth
            z, d, y = p.instrument, p.treated.astype(float), p.outcome
            row["first_stage_dP_per_SD"] = np.cov(d, z)[0, 1] / z.var()
        rows.append(row)
    return pd.DataFrame(rows).mean()


pymc = {
    "ideal instrument, linear 1": ("plain 3.77, joint 0.95, as feature 4.26", dict(strength=1.0, instrument_strength=1.0)),
    "ideal instrument, nothing hidden": ("plain 0.15, joint 0.08", dict(strength=0.0, instrument_strength=1.0)),
    "flaw 1.0, linear 1": ("plain 4.51, joint 5.90", dict(strength=1.0, instrument_strength=1.0, instrument_flaw=1.0)),
    "flaw 1.0, nothing hidden": ("plain 0.99, joint 4.55", dict(strength=0.0, instrument_strength=1.0, instrument_flaw=1.0)),
    "flaw 0.5, linear 1": ("plain 4.14, joint 3.40", dict(strength=1.0, instrument_strength=1.0, instrument_flaw=0.5)),
    "practice 25, linear 1": ("plain 3.77, joint 0.65", dict(strength=1.0, instrument_strength=1.0, instrument_groups=25)),
    "no instrument, linear 1, 5,000": ("plain 4.20 (repeats 0-9)", dict(strength=1.0)),
}
pd.set_option("display.width", 200)
for name, (reported, opts) in pymc.items():
    strength = opts.pop("strength")
    r = errors(N, strength, **opts)
    print(f"\n{name}\n  reported (PyMC): {reported}\n  independent:     " + ", ".join(f"{k} {v:.2f}" for k, v in r.items()))

N = 20000
r = errors(20000, 1.0)
print(f"\nno instrument, linear 1, 20,000\n  reported (PyMC): plain 4.32, joint 4.23\n  independent:     " + ", ".join(f"{k} {v:.2f}" for k, v in r.items()))
