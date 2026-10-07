"""Step 3 results: summarise the joint model, the instrument and the validation check.

Reads whichever of these result folders exist for the current generator version:

  joint_model/   plain and joint model, no instrument      (script 08)
  validation/    the concordant-against-discordant check   (script 09)
  instrument/    plain and joint model, with an instrument (script 10)

For each it prints one line per setting, saves the table under
reports/tables/ and draws a figure under reports/figures/.

Run:  uv run python scripts/11_summarise_step3.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from stresstest.generator import GENERATOR_VERSION, SHAPES

REPO = Path(__file__).parent.parent
FOLDER = REPO / "results" / f"generator-v{GENERATOR_VERSION}"
TABLES = REPO / "reports" / "tables"
FIGURES = REPO / "reports" / "figures"

SETTINGS = [("none", 0.0)] + [(shape, strength) for shape in SHAPES for strength in (0.5, 1.0)]
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TITLES = {
    "linear": "Linear\neach step worsens the result equally",
    "threshold": "Threshold\nonly the top 16% are affected",
    "effect": "Effect\nit blunts the GLP-1 drug only",
}


def load(subfolder: str, keys: list[str]) -> pd.DataFrame | None:
    """Every row saved in one results subfolder, after the same checks as step 2."""
    files = sorted((FOLDER / subfolder).glob("*.csv"))
    if not files:
        return None
    rows = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    if (rows["generator_version"] != GENERATOR_VERSION).any():
        raise SystemExit(f"{subfolder}: rows from another generator version")
    if rows.duplicated(keys).any():
        raise SystemExit(f"{subfolder}: a dataset appears more than once")
    print(f"\n=== {subfolder}: {len(rows)} rows, code commit(s) {', '.join(sorted(rows['code_commit'].unique()))}")
    return rows


def style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.tick_params(colors=MUTED, length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.set_xticks([0, 0.5, 1.0])
    ax.set_xticklabels(["off", "0.5", "1"], color=MUTED)
    ax.set_xlim(-0.18, 1.34)


def lines_by_strength(ax, table, shape, series):
    """One line per series across the three strengths, with the last value written beside each line."""
    ends = []
    for column, label, colour in series:
        points = pd.concat([table[table["shape"] == "none"], table[table["shape"] == shape]])
        ax.plot(points["strength"], points[column], color=colour, linewidth=2, zorder=3)
        ax.scatter(points["strength"], points[column], s=55, color=colour, edgecolors=SURFACE, linewidths=2, zorder=4)
        ends.append((points.iloc[-1][column], points.iloc[-1]["strength"]))
    # Write the end values. Where two lines finish close together, lift the upper label.
    top = max(ax.get_ylim()[1], 1e-9)
    previous = None
    for value, strength in sorted(set(ends)):
        lift = 10 if previous is not None and (value - previous) / top < 0.07 else 0
        ax.annotate(f"{value:.1f}", (strength, value), textcoords="offset points",
                    xytext=(9, -4 + lift), fontsize=9.5, color=INK)
        previous = value


def summarise_joint(rows):
    table = (
        rows.groupby(["shape", "strength", "model"])
        .agg(repeats=("repeat", "size"), rho=("rho_mean", "mean"), rho_low=("rho_low", "mean"),
             rho_high=("rho_high", "mean"), bias_average=("bias_average", "mean"),
             rmse_individual=("rmse_individual", "mean"), coverage_95=("coverage_95", "mean"),
             wrong_drug=("wrong_drug", "mean"), hba1c_lost=("hba1c_lost", "mean"),
             rhat_worst_patient=("rhat_worst_patient", "max"))
        .reset_index()
    )
    print("shape     strength model |  rho (average 95% interval) | error in avg  typical   95% int.  worse   HbA1c")
    print("                         |                             | effect        error     cover     drug    lost")
    for shape, strength in SETTINGS:
        for model in ("plain", "joint"):
            r = table[(table["shape"] == shape) & (table["strength"] == strength) & (table["model"] == model)].iloc[0]
            print(f"{shape:9s} {strength:7.1f} {model:5s} | {r.rho:+.2f} ({r.rho_low:+.2f} to {r.rho_high:+.2f})    | "
                  f"{r.bias_average:6.2f}      {r.rmse_individual:5.2f}    {r.coverage_95:6.1%}   {r.wrong_drug:5.1%}   {r.hba1c_lost:4.2f}")
    joint = rows[rows["model"] == "joint"]
    excludes = ((joint["rho_low"] > 0) | (joint["rho_high"] < 0)).sum()
    print(f"joint fits whose 95% interval for rho excludes zero: {excludes} of {len(joint)}")
    return table


def summarise_validation(rows):
    table = (
        rows.groupby(["shape", "strength", "model"])
        .agg(repeats=("repeat", "size"), pairs=("pairs", "mean"), share_concordant=("share_concordant", "mean"),
             predicted_benefit=("predicted_benefit", "mean"), observed_benefit=("observed_benefit", "mean"),
             true_benefit=("true_benefit", "mean"), observed_sd=("observed_benefit", "std"),
             wrong_drug=("wrong_drug", "mean"))
        .reset_index()
    )
    for model, heading in (("truth", "a model that is exactly right"), ("plain", "the plain regression")):
        print(f"--- the check applied to {heading}")
        print("shape     strength | pairs | predicted  observed (SD)   true    | observed-predicted | sent to worse drug")
        for shape, strength in SETTINGS:
            r = table[(table["shape"] == shape) & (table["strength"] == strength) & (table["model"] == model)].iloc[0]
            print(f"{shape:9s} {strength:7.1f}  | {r.pairs:5.0f} | {r.predicted_benefit:8.2f}  {r.observed_benefit:6.2f} ({r.observed_sd:4.2f})  "
                  f"{r.true_benefit:5.2f}   | {r.observed_benefit - r.predicted_benefit:+18.2f} | {r.wrong_drug:6.1%}")
    return table


def draw_validation(table):
    series = [("predicted_benefit", "Predicted by the model", BLUE),
              ("observed_benefit", "Observed in the check", ORANGE),
              ("true_benefit", "True", AQUA)]
    rows = [("plain", "The plain regression\nHbA1c benefit (mmol/mol)"),
            ("truth", "A model that is exactly right\nHbA1c benefit (mmol/mol)")]
    fig, axes = plt.subplots(2, 3, figsize=(10.5, 7.4), sharey=True, facecolor=SURFACE)
    for i, (model, label) in enumerate(rows):
        for j, shape in enumerate(SHAPES):
            ax = axes[i, j]
            style(ax)
            ax.set_ylim(0, table[[s[0] for s in series]].max().max() * 1.15)
            lines_by_strength(ax, table[table["model"] == model], shape, series)
            if i == 0:
                ax.set_title(TITLES[shape], fontsize=10.5, color=INK, loc="left")
            if i == 1:
                ax.set_xlabel("Strength of the hidden factor", color=MUTED, fontsize=9.5)
            if j == 0:
                ax.set_ylabel(label, color=MUTED, fontsize=9.5)
    handles = [plt.Line2D([], [], color=c, linewidth=2, marker="o", markersize=6, label=l) for _, l, c in series]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.055, 0.925), ncol=3, frameon=False,
               fontsize=9.5, labelcolor=INK, handlelength=1.6, columnspacing=1.8)
    fig.text(0.06, 0.012, "Bottom row: the model's predictions are the true effects, so the predicted line lies under the true line.",
             fontsize=9, color=MUTED)
    fig.suptitle("The validation check agrees with a misled model and disagrees with a correct one",
                 x=0.06, y=0.975, ha="left", fontsize=13, color=INK, fontweight="bold")
    fig.tight_layout(rect=(0.03, 0.03, 1, 0.885), h_pad=2.0)
    fig.savefig(FIGURES / "step3_validation_check.png", dpi=160, facecolor=SURFACE)
    print("figure saved: reports/figures/step3_validation_check.png")


def summarise_instrument(rows):
    table = (
        rows.groupby(["instrument_strength", "shape", "strength", "model"])
        .agg(repeats=("repeat", "size"), rho=("rho_mean", "mean"), rho_low=("rho_low", "mean"),
             rho_high=("rho_high", "mean"), bias_average=("bias_average", "mean"),
             bias_sd=("bias_average", "std"), rmse_individual=("rmse_individual", "mean"),
             coverage_95=("coverage_95", "mean"), wrong_drug=("wrong_drug", "mean"),
             hba1c_lost=("hba1c_lost", "mean"), predicted_benefit=("predicted_benefit", "mean"),
             observed_benefit=("observed_benefit", "mean"), true_benefit=("true_benefit", "mean"),
             rhat_worst_patient=("rhat_worst_patient", "max"))
        .reset_index()
    )
    for instrument_strength in sorted(table["instrument_strength"].unique()):
        print(f"--- instrument strength {instrument_strength}")
        print("shape     strength model |  rho (average 95% interval) | error in avg (SD)  typical  95% int.  worse  | check: predicted observed true")
        for shape, strength in SETTINGS:
            for model in ("plain", "joint"):
                r = table[(table["instrument_strength"] == instrument_strength) & (table["shape"] == shape)
                          & (table["strength"] == strength) & (table["model"] == model)].iloc[0]
                print(f"{shape:9s} {strength:7.1f} {model:5s} | {r.rho:+.2f} ({r.rho_low:+.2f} to {r.rho_high:+.2f})    | "
                      f"{r.bias_average:6.2f} ({r.bias_sd:4.2f})   {r.rmse_individual:5.2f}   {r.coverage_95:6.1%}   {r.wrong_drug:5.1%} | "
                      f"{r.predicted_benefit:9.2f} {r.observed_benefit:8.2f} {r.true_benefit:5.2f}")
    return table


def draw_instrument(table, no_instrument):
    """Share sent to the worse drug: plain model, and joint model at each instrument strength."""
    series = [("plain", "Plain regression", BLUE)]
    strengths = sorted(table["instrument_strength"].unique())
    colours = [ORANGE, AQUA]
    fig, axes = plt.subplots(2, 3, figsize=(10.5, 7.4), sharey="row", facecolor=SURFACE)
    measures = [("wrong_drug", "Patients sent to the worse drug (%)", 100), ("coverage_95", "95% intervals containing the truth (%)", 100)]
    for i, (measure, label, scale) in enumerate(measures):
        for j, shape in enumerate(SHAPES):
            ax = axes[i, j]
            style(ax)
            scaled = table.assign(value=table[measure] * scale)
            frames = [(scaled[(scaled["model"] == "plain") & (scaled["instrument_strength"] == strengths[-1])], "Plain regression", BLUE)]
            if no_instrument is not None:
                base = no_instrument.assign(value=no_instrument[measure] * scale)
                frames.append((base[base["model"] == "joint"], "Joint model, no instrument", MUTED))
            for strength_value, colour in zip(strengths, colours):
                frames.append((scaled[(scaled["model"] == "joint") & (scaled["instrument_strength"] == strength_value)],
                               f"Joint model, instrument {strength_value:g}", colour))
            for frame, _, colour in frames:
                lines_by_strength(ax, frame.rename(columns={"value": "v"}), shape, [("v", "", colour)])
            ax.set_ylim(0, 105 if measure == "coverage_95" else None)
            if i == 0:
                ax.set_title(TITLES[shape], fontsize=10.5, color=INK, loc="left")
            if i == 1:
                ax.set_xlabel("Strength of the hidden factor", color=MUTED, fontsize=9.5)
            if j == 0:
                ax.set_ylabel(label, color=MUTED, fontsize=9.5)
    handles = [plt.Line2D([], [], color=c, linewidth=2, marker="o", markersize=6, label=l) for _, l, c in frames]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.055, 0.925), ncol=4, frameon=False,
               fontsize=9.5, labelcolor=INK, handlelength=1.6, columnspacing=1.6)
    fig.suptitle("With an instrument, a joint model can correct for a hidden factor",
                 x=0.06, y=0.975, ha="left", fontsize=13, color=INK, fontweight="bold")
    fig.tight_layout(rect=(0.03, 0, 1, 0.885), h_pad=2.0)
    fig.savefig(FIGURES / "step3_instrument.png", dpi=160, facecolor=SURFACE)
    print("figure saved: reports/figures/step3_instrument.png")


if __name__ == "__main__":
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    joint_table = None
    joint = load("joint_model", ["model", "shape", "strength", "repeat"])
    if joint is not None:
        joint_table = summarise_joint(joint)
        joint_table.to_csv(TABLES / "step3_joint_model.csv", index=False, float_format="%.4f")

    validation = load("validation", ["model", "shape", "strength", "repeat"])
    if validation is not None:
        validation_table = summarise_validation(validation)
        validation_table.to_csv(TABLES / "step3_validation_check.csv", index=False, float_format="%.4f")
        draw_validation(validation_table)

    instrument = load("instrument", ["model", "instrument_strength", "shape", "strength", "repeat"])
    if instrument is not None:
        instrument_table = summarise_instrument(instrument)
        instrument_table.to_csv(TABLES / "step3_instrument.csv", index=False, float_format="%.4f")
        draw_instrument(instrument_table, joint_table)
