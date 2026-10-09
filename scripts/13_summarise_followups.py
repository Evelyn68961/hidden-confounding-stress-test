"""Summarise the follow-up runs (reports 09 to 14).

Reads the saved results and writes one table per follow-up run to
reports/tables/. Each table sets the new result beside the earlier result it
extends, on the same simulated datasets wherever that is possible. No earlier
table is changed.

  followup_instrument_twenty.csv   script 10, repeats 10 to 19, beside repeats 0 to 9
  followup_realistic.csv           script 12 --run realistic, beside the ideal instrument
  followup_as_feature.csv          script 12 --run as_feature, beside plain and joint
  followup_more_patients.csv       script 12 --run more_patients, beside 5,000 patients
  followup_per_drug_noise.csv      script 12 --run per_drug_noise, beside the joint model
                                   with one noise level and the plain regression
  followup_per_drug_noise_instruments.csv
                                   the same model on every other instrument setting

A run whose results are not there yet is skipped.

Run:  uv run python scripts/13_summarise_followups.py
"""

from pathlib import Path

import pandas as pd

from stresstest.generator import GENERATOR_VERSION

REPO = Path(__file__).resolve().parents[1]
FOLDER = REPO / "results" / f"generator-v{GENERATOR_VERSION}"
TABLES = REPO / "reports" / "tables"

SCORES = ["bias_average", "rmse_individual", "coverage_95", "wrong_drug", "hba1c_lost"]


def load(subfolder):
    files = sorted((FOLDER / subfolder).glob("*.csv"))
    if not files:
        return None
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True)


def summarise(rows, by):
    """Average the scores over datasets; add the spread of the error and how often rho excluded zero."""
    rows = rows.assign(link_detected=(rows["rho_low"] > 0) | (rows["rho_high"] < 0))
    table = rows.groupby(by, sort=False).agg(
        datasets=("repeat", "nunique"),
        rho=("rho_mean", "mean"),
        rho_low=("rho_low", "mean"),
        rho_high=("rho_high", "mean"),
        link_detected=("link_detected", "sum"),
        bias_average=("bias_average", "mean"),
        bias_sd=("bias_average", "std"),
        rmse_individual=("rmse_individual", "mean"),
        coverage_95=("coverage_95", "mean"),
        wrong_drug=("wrong_drug", "mean"),
        hba1c_lost=("hba1c_lost", "mean"),
        rhat_worst_patient=("rhat_worst_patient", "max"),
    )
    return table.reset_index()


def save(table, name):
    table.to_csv(TABLES / name, index=False, float_format="%.4f")
    print(f"\n=== {name}")
    print(table.to_string(index=False, float_format=lambda v: f"{v:.3f}"))


def instrument_twenty(instrument):
    blocks = []
    for label, part in (
        ("first ten (report 08)", instrument[instrument["repeat"] < 10]),
        ("second ten", instrument[instrument["repeat"] >= 10]),
        ("all twenty", instrument),
    ):
        if len(part):
            blocks.append(
                summarise(part, ["instrument_strength", "shape", "strength", "model"]).assign(datasets_used=label)
            )
    table = pd.concat(blocks, ignore_index=True)
    return table.sort_values(["instrument_strength", "shape", "strength", "model"], kind="stable")


def realistic(rows, instrument):
    ideal = instrument[
        (instrument["instrument_strength"] == 1.0)
        & (instrument["repeat"] < 10)
        & (((instrument["shape"] == "none")) | ((instrument["shape"] == "linear") & (instrument["strength"] == 1.0)))
    ].assign(variant="ideal (report 08)")
    both = pd.concat([ideal, rows], ignore_index=True)
    return summarise(both, ["shape", "strength", "variant", "model"]).sort_values(
        ["strength", "model"], kind="stable"
    )


def as_feature(rows, instrument):
    same = instrument[(instrument["instrument_strength"] == 1.0) & (instrument["repeat"] < 10)]
    both = pd.concat([same, rows], ignore_index=True)
    return summarise(both, ["shape", "strength", "model"]).sort_values(["shape", "strength"], kind="stable")


def more_patients(rows, joint_model):
    small = joint_model[
        (joint_model["repeat"] < 10)
        & ((joint_model["shape"] == "none") | ((joint_model["shape"] == "linear") & (joint_model["strength"] == 1.0)))
    ].assign(patients=5000)
    both = pd.concat([small, rows], ignore_index=True)
    return summarise(both, ["shape", "strength", "patients", "model"]).sort_values(
        ["strength", "model", "patients"], kind="stable"
    )


def per_drug_noise(rows, instrument, joint_model, more):
    """The joint model with a noise level per drug, beside the earlier models on the same datasets."""
    off_or_linear = lambda d: (d["shape"] == "none") | ((d["shape"] == "linear") & (d["strength"] == 1.0))
    # Report 13 covers the first part of the run: datasets 0 to 9 of three variants.
    rows = rows[
        rows["variant"].isin(["ideal_instrument", "no_instrument", "no_instrument_20000"]) & (rows["repeat"] < 10)
    ]
    parts = [
        instrument[(instrument["instrument_strength"] == 1.0) & (instrument["repeat"] < 10)].assign(
            setting="ideal instrument, 5,000 patients"
        ),
        joint_model[(joint_model["repeat"] < 10) & off_or_linear(joint_model)].assign(
            setting="no instrument, 5,000 patients"
        ),
        rows.assign(
            setting=rows["variant"].map(
                {
                    "ideal_instrument": "ideal instrument, 5,000 patients",
                    "no_instrument": "no instrument, 5,000 patients",
                    "no_instrument_20000": "no instrument, 20,000 patients",
                }
            )
        ),
    ]
    if more is not None:
        parts.append(more.assign(setting="no instrument, 20,000 patients"))
    both = pd.concat(parts, ignore_index=True)
    table = summarise(both, ["setting", "shape", "strength", "model"])
    # How far a single dataset's answer is from the truth, bias and spread together.
    rms = both.groupby(["setting", "shape", "strength", "model"], sort=False)["bias_average"].apply(
        lambda errors: float((errors**2).mean() ** 0.5)
    )
    table["rms_error"] = rms.to_numpy()
    not_settled = both.assign(flag=both["rhat_worst_patient"] > 1.01).groupby(
        ["setting", "shape", "strength", "model"], sort=False
    )["flag"].sum()
    table["fits_rhat_above_1.01"] = not_settled.to_numpy()
    return table.sort_values(["setting", "shape", "strength", "model"], kind="stable")


def add_rms(table, rows, by):
    rms = rows.groupby(by, sort=False)["bias_average"].apply(lambda errors: float((errors**2).mean() ** 0.5))
    table["rms_error"] = rms.to_numpy()
    return table


def per_drug_noise_instruments(rows, instrument, realistic_rows):
    """The per-drug noise model on every instrument setting, beside the earlier models (report 14)."""
    by = ["setting", "shape", "strength", "model"]
    parts = []

    ideal = rows[rows["variant"] == "ideal_instrument"]
    earlier = instrument[instrument["instrument_strength"] == 1.0]
    for label, keep in (
        ("ideal 1.0, datasets 0-9", lambda d: d["repeat"] < 10),
        ("ideal 1.0, datasets 10-19", lambda d: d["repeat"] >= 10),
        ("ideal 1.0, all twenty", lambda d: d["repeat"] >= 0),
    ):
        parts.append(pd.concat([earlier[keep(earlier)], ideal[keep(ideal)]]).assign(setting=label))

    weak = rows[rows["variant"] == "ideal_instrument_0.5"]
    earlier = instrument[(instrument["instrument_strength"] == 0.5) & (instrument["repeat"] < 10)]
    parts.append(pd.concat([earlier, weak]).assign(setting="ideal 0.5, datasets 0-9"))

    for variant in ("practice_100", "practice_25", "flaw_0.5", "flaw_1.0"):
        new = rows[rows["variant"] == variant]
        old = realistic_rows[realistic_rows["variant"] == variant]
        parts.append(pd.concat([old, new]).assign(setting=variant))

    both = pd.concat(parts, ignore_index=True)
    return add_rms(summarise(both, by), both, by)


if __name__ == "__main__":
    TABLES.mkdir(parents=True, exist_ok=True)
    instrument = load("instrument")
    joint_model = load("joint_model")

    if instrument is not None and (instrument["repeat"] >= 10).any():
        save(instrument_twenty(instrument), "followup_instrument_twenty.csv")

    realistic_rows = load("realistic")
    if realistic_rows is not None:
        save(realistic(realistic_rows, instrument), "followup_realistic.csv")

    rows = load("as_feature")
    if rows is not None:
        save(as_feature(rows, instrument), "followup_as_feature.csv")

    more = load("more_patients")
    if more is not None:
        save(more_patients(more, joint_model), "followup_more_patients.csv")

    rows = load("per_drug_noise")
    if rows is not None:
        save(per_drug_noise(rows, instrument, joint_model, more), "followup_per_drug_noise.csv")
        if (rows["variant"] == "ideal_instrument_0.5").any():
            save(
                per_drug_noise_instruments(rows, instrument, realistic_rows),
                "followup_per_drug_noise_instruments.csv",
            )
