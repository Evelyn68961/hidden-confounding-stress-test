"""Second independent check: the corrected joint model against a classical
two-step correction, for every hidden-factor setting, on the same ten datasets
(ideal instrument of strength 1.0). numpy and scipy only."""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

from stresstest.generator import make_patients


def design(p):
    x = p.features.to_numpy(float)
    return (x - x.mean(0)) / x.std(0)


def ols_effect(p, x, more=None):
    d = p.treated.astype(float)
    cols = [np.ones(len(d)), x, d, d[:, None] * x] + ([more] if more is not None else [])
    beta, *_ = np.linalg.lstsq(np.column_stack(cols), p.outcome, rcond=None)
    k = x.shape[1]
    return (beta[1 + k] + x @ beta[2 + k: 2 + 2 * k]).mean()


def control_function(p):
    x, d = design(p), p.treated.astype(float)
    z = np.column_stack([np.ones(len(d)), x, p.instrument])
    nll = lambda g: -(d * np.log(norm.cdf(z @ g).clip(1e-10, 1)) + (1 - d) * np.log((1 - norm.cdf(z @ g)).clip(1e-10, 1))).sum()
    index = z @ minimize(nll, np.zeros(z.shape[1]), method="BFGS").x
    pdf, cdf = norm.pdf(index), norm.cdf(index).clip(1e-10, 1 - 1e-10)
    return ols_effect(p, x, more=d * pdf / cdf - (1 - d) * pdf / (1 - cdf))


saved = pd.read_csv("results/generator-v2/per_drug_noise/EVELYN68961.csv")
saved = saved[saved.variant == "ideal_instrument"].groupby(["shape", "strength"]).bias_average.mean()
rows = []
for shape, strength in [("none", 0.0), ("linear", 0.5), ("linear", 1.0), ("threshold", 0.5), ("threshold", 1.0), ("effect", 0.5), ("effect", 1.0)]:
    plain, two_step = [], []
    for seed in range(10):
        p = make_patients(5000, strength, "linear" if shape == "none" else shape, seed=seed, instrument_strength=1.0)
        truth = p.true_effect.mean()
        plain.append(ols_effect(p, design(p)) - truth)
        two_step.append(control_function(p) - truth)
    rows.append({"shape": shape, "strength": strength, "least_squares": np.mean(plain), "two_step": np.mean(two_step),
                 "two_step_sd": np.std(two_step, ddof=1), "corrected_joint_model": saved[(shape, strength)]})
print(pd.DataFrame(rows).round(2).to_string(index=False))
