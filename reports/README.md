# Progress reports

One report for each run or analysis, in the order the work was done. Each
report states the question, what was run, the result, how to read it, and its
limits. Numbers are copied from the script output at the commit named in the
report.

| # | Date | Report | Question |
|---|---|---|---|
| 01 | 2026-10-07 | [Causal forest, nothing hidden](01_causal_forest_no_hidden_factor.md) | Does the Bayesian causal forest recover the truth when nothing is hidden? (four runs: first generator, four chains, generator version 1, generator version 2) |
| 02 | 2026-10-07 | [What the hidden factor does](02_what_the_hidden_factor_does.md) | What does each strength and shape of the hidden factor do to the data? |
| 03 | 2026-10-07 | [Causal forest, hidden factor on](03_causal_forest_grid.md) | How wrong does the forest get as the hidden factor gets stronger, and does its form matter? (140 fits) |
| 04 | 2026-10-07 | [Do the two computers agree?](04_cross_computer_check.md) | The fits were shared between two computers. Do they simulate the same patients and give the same answers? |
| 05 | 2026-10-07 | [Joint model: trial and check](05_joint_model_trial_and_check.md) | Does a joint model of drug choice and outcome detect the hidden factor, how long does it take, and does the code work when the task is easy? |
| 06 | 2026-10-07 | [Joint model on all 140 datasets, no instrument](06_joint_model_grid.md) | Without an instrument, does a joint model detect a hidden factor, correct the bias, or report honest uncertainty? |
| 07 | 2026-10-07 | [The published validation check](07_validation_check.md) | Does comparing concordant with matched discordant patients notice a model misled by a hidden factor? |
