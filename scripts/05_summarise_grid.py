"""Step 2 results: summarise the causal forest grid and draw the figure.

Reads every computer's results for the current generator version, checks that
they belong together, and prints one line per setting: the average of each
score across the repeats, and how much it varies.

It can be run while the grid is still going. It reports how many repeats each
setting has so far.

Run:  uv run python scripts/05_summarise_grid.py

Writes:
  reports/tables/step2_causal_forest.csv    one row per setting
  reports/figures/step2_causal_forest.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw to a file; no window needed
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from stresstest.generator import GENERATOR_VERSION, SHAPES

REPO = Path(__file__).parent.parent
FOLDER = REPO / "results" / f"generator-v{GENERATOR_VERSION}"
FIGURE = REPO / "reports" / "figures" / "step2_causal_forest.png"
# Not saved next to the results: the grid script reads every .csv in that
# folder as a list of finished fits.
TABLE = REPO / "reports" / "tables" / "step2_causal_forest.csv"

SCORES = ["crude_error", "bias_average", "rmse_individual", "coverage_95", "wrong_drug", "hba1c_lost"]


def load_results() -> pd.DataFrame:
    """Every fit saved by every computer, after checking they belong together."""
    files = sorted(FOLDER.glob("*.csv"))
    if not files:
        raise SystemExit(f"no results in {FOLDER}")
    fits = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

    wrong_version = fits[fits["generator_version"] != GENERATOR_VERSION]
    if len(wrong_version):
        raise SystemExit(f"{len(wrong_version)} rows come from another generator version")

    # The same dataset must not be counted twice.
    setting = ["shape", "strength", "repeat"]
    twice = fits[fits.duplicated(setting, keep=False)]
    if len(twice):
        raise SystemExit(f"these fits appear more than once:\n{twice[setting + ['host']]}")
    return fits


def summarise(fits: pd.DataFrame) -> pd.DataFrame:
    """One row per setting: mean and SD of each score across the repeats."""
    groups = fits.groupby(["shape", "strength"])
    summary = groups[SCORES].mean()
    for score in ("bias_average", "rmse_individual", "wrong_drug"):
        summary[f"{score}_sd"] = groups[score].std()
    summary["rhat_worst_patient"] = groups["rhat_worst_patient"].max()
    summary["patients_rhat_above_1.01"] = groups["share_patients_rhat_above_1.01"].mean()
    summary.insert(0, "repeats", groups.size())
    order = [("none", 0.0)] + [(s, k) for s in SHAPES for k in (0.5, 1.0)]
    return summary.reindex([o for o in order if o in summary.index]).reset_index()


def print_table(summary: pd.DataFrame, fits: pd.DataFrame) -> None:
    by_host = fits.groupby("host").size()
    print(f"generator v{GENERATOR_VERSION}; fits: {len(fits)} "
          f"({', '.join(f'{h} {n}' for h, n in by_host.items())}); "
          f"code commits: {', '.join(sorted(fits['code_commit'].unique()))}")
    print()
    print("shape     strength  n | crude  | forest: error in     typical error   95% int.  sent to     HbA1c  | worst")
    print("                      | error  | the average effect   per patient     cover     worse drug  lost   | R-hat")
    for r in summary.itertuples():
        print(
            f"{r.shape:9s} {r.strength:7.1f} {r.repeats:3d} | {r.crude_error:5.2f}  | "
            f"{r.bias_average:6.2f} (SD {r.bias_average_sd:4.2f})   "
            f"{r.rmse_individual:5.2f} (SD {r.rmse_individual_sd:4.2f})  "
            f"{r.coverage_95:6.1%}   {r.wrong_drug:5.1%} (SD {r.wrong_drug_sd:4.1%})  "
            f"{r.hba1c_lost:5.2f}  | {r.rhat_worst_patient:5.3f}"
        )


def draw_figure(fits: pd.DataFrame) -> None:
    """Three panels, one per shape. Each dot is one simulated dataset."""
    surface, ink, muted, grid, blue = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6"
    titles = {
        "linear": "Linear\neach step worsens the result equally",
        "threshold": "Threshold\nonly the top 16% are affected",
        "effect": "Effect\nit blunts the GLP-1 drug only",
    }
    rows = [("wrong_drug", "Patients sent to the worse drug", 100, "{:.0f}%"),
            ("rmse_individual", "Typical error per patient (mmol/mol)", 1, "{:.1f}")]

    fig, axes = plt.subplots(len(rows), 3, figsize=(10.5, 7.2), sharey="row", facecolor=surface)
    rng = np.random.default_rng(0)
    off = fits[fits["shape"] == "none"]
    # Leave headroom above the highest dot in each row.
    panel_top = {score: fits[score].max() * scale * 1.12 for score, _, scale, _ in rows}

    for i, (score, label, scale, fmt) in enumerate(rows):
        for j, shape in enumerate(SHAPES):
            ax = axes[i, j]
            ax.set_facecolor(surface)
            # The strength-0 datasets are the same in every panel.
            panel = pd.concat([off, fits[fits["shape"] == shape]])
            means = panel.groupby("strength")[score].mean() * scale
            for strength, group in panel.groupby("strength"):
                jitter = rng.uniform(-0.035, 0.035, len(group))
                ax.scatter(strength + jitter, group[score] * scale, s=22, color=blue,
                           alpha=0.28, linewidths=0, zorder=2)
            ax.plot(means.index, means.values, color=blue, linewidth=2, zorder=3)
            ax.scatter(means.index, means.values, s=70, color=blue, edgecolors=surface,
                       linewidths=2, zorder=4)
            for strength, value in means.items():
                ax.annotate(fmt.format(value), (strength, value), textcoords="offset points",
                            xytext=(11, -4), ha="left", fontsize=10, color=ink, zorder=5)

            ax.set_xticks([0, 0.5, 1.0])
            ax.set_xticklabels(["off", "0.5", "1"], color=muted)
            ax.set_xlim(-0.18, 1.32)
            ax.set_ylim(0, panel_top[score])
            ax.grid(axis="y", color=grid, linewidth=0.8, zorder=0)
            ax.tick_params(colors=muted, length=0)
            for side in ("top", "right", "left"):
                ax.spines[side].set_visible(False)
            ax.spines["bottom"].set_color(grid)
            if i == 0:
                ax.set_title(titles[shape], fontsize=10.5, color=ink, loc="left")
            if i == len(rows) - 1:
                ax.set_xlabel("Strength of the hidden factor", color=muted, fontsize=9.5)
            if j == 0:
                ax.set_ylabel(label, color=muted, fontsize=9.5)

    repeats = int(fits.groupby(["shape", "strength"]).size().min())
    fig.suptitle("A Bayesian causal forest gets worse as a hidden factor gets stronger",
                 x=0.06, y=0.975, ha="left", fontsize=13.5, color=ink, fontweight="bold")
    fig.text(0.06, 0.915,
             "Each small dot is one simulated dataset of 5,000 patients. "
             f"Large dots are averages (at least {repeats} datasets per setting).",
             fontsize=9.5, color=muted)
    fig.tight_layout(rect=(0.03, 0, 1, 0.90), h_pad=2.0)
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE, dpi=160, facecolor=surface)
    print(f"\nfigure saved to {FIGURE.relative_to(REPO)}")


if __name__ == "__main__":
    fits = load_results()
    summary = summarise(fits)
    print_table(summary, fits)
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(TABLE, index=False, float_format="%.4f")
    draw_figure(fits)
