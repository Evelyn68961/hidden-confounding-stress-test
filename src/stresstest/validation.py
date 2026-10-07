"""The concordant-against-discordant validation of a treatment selection model.

In real records nobody observes a patient on both drugs, so predicted effects
cannot be checked one patient at a time. Dennis et al. (Lancet Digit Health
2022; Lancet 2025) check them in groups instead:

  1. Use the model to name each patient's best drug.
  2. Call a patient "concordant" if they received that drug, "discordant" if not.
  3. Match each concordant patient to a similar discordant patient.
  4. In each pair, compare the benefit the model predicted with the benefit
     observed (the difference between the two patients' outcomes).

If the model is right, observed and predicted benefit should agree.

In a simulation the true benefit is also known, so this module can report all
three: predicted, observed and true. That shows whether the check would notice
a model that has been misled by a hidden factor.

The matching follows the published description: exact matching on sex and on
starting HbA1c in twenty equal-sized groups, then the nearest neighbour, with
replacement, on a score built from all features, within a caliper of 0.05.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

CALIPER = 0.05


def concordance_validation(features: pd.DataFrame, treated, outcome, estimated_effect, true_effect) -> dict:
    """Run the check for one dataset and one model.

    `estimated_effect` is the model's estimate of GLP-1 minus SGLT2 for each
    patient (negative means the GLP-1 drug is predicted to be better).
    Benefits are returned in mmol/mol; positive means the patient's own drug
    lowers HbA1c more than the comparator's drug.
    """
    treated = np.asarray(treated)
    outcome = np.asarray(outcome)
    estimated_effect = np.asarray(estimated_effect)
    true_effect = np.asarray(true_effect)

    # Steps 1 and 2: the model's best drug, and who received it.
    best_is_glp1 = estimated_effect < 0
    concordant = (treated == 1) == best_is_glp1

    # A score for how likely a patient with these features is to be concordant.
    # Being concordant means opposite things for the two groups of patients
    # (getting the GLP-1 drug for one, not getting it for the other), so every
    # feature is allowed a different slope in each group.
    scaled = StandardScaler().fit_transform(features.to_numpy(dtype="float64"))
    which = best_is_glp1.astype(float)[:, None]
    design = np.hstack([scaled, which, scaled * which])
    score = LogisticRegression(max_iter=2000).fit(design, concordant).predict_proba(design)[:, 1]

    # Exact-matching groups: sex, and starting HbA1c in twenty equal-sized groups.
    hba1c_group = pd.qcut(features["hba1c"], 20, labels=False, duplicates="drop").to_numpy()
    group = features["female"].to_numpy() * 100 + hba1c_group

    # Step 3: for each concordant patient, the nearest discordant patient in the same group.
    pairs = []
    for g in np.unique(group):
        own = np.flatnonzero((group == g) & concordant)
        pool = np.flatnonzero((group == g) & ~concordant)
        if len(own) == 0 or len(pool) == 0:
            continue
        pool = pool[np.argsort(score[pool])]
        position = np.searchsorted(score[pool], score[own]).clip(1, len(pool) - 1)
        below, above = pool[position - 1], pool[position]
        nearest = np.where(np.abs(score[below] - score[own]) <= np.abs(score[above] - score[own]), below, above)
        close_enough = np.abs(score[nearest] - score[own]) <= CALIPER
        pairs.append(np.column_stack([own[close_enough], nearest[close_enough]]))
    pairs = np.concatenate(pairs)
    own, comparator = pairs[:, 0], pairs[:, 1]

    # Step 4. The comparator took drug treated[comparator]; the patient took treated[own].
    # Benefit of the patient's own drug = outcome on the comparator's drug minus outcome on their own.
    drug_gap = treated[comparator] - treated[own]
    return {
        "share_concordant": float(concordant.mean()),
        "pairs": int(len(own)),
        "predicted_benefit": float(np.mean(drug_gap * estimated_effect[own])),
        "observed_benefit": float(np.mean(outcome[comparator] - outcome[own])),
        "true_benefit": float(np.mean(drug_gap * true_effect[own])),
    }
