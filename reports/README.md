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
| 08 | 2026-10-08 | [Joint model with an instrument](08_instrument.md) | Given an instrument, does the joint model correct the bias, and what does it cost? |
| 09 | 2026-10-08 | [The instrument result on ten more datasets](09_instrument_twenty_datasets.md) | Report 08 rests on ten datasets per setting. Does its result hold on ten new ones? |
| 10 | 2026-10-09 | [Less ideal instruments](10_less_ideal_instruments.md) | Does the correction survive an instrument shared within a practice, or one that is slightly flawed? |
| 11 | 2026-10-09 | [The instrument used as an ordinary feature](11_instrument_as_a_feature.md) | What happens if the instrument is added to the plain regression like any other feature? |
| 12 | 2026-10-09 | [The joint model with four times as many patients](12_more_patients.md) | Without an instrument, was 5,000 patients simply too few for the joint model to find the hidden factor? |
| 13 | 2026-10-09 | [Verification, and a joint model with a noise level per drug](13_verification_and_corrected_joint_model.md) | Are the numbers right, and are the explanations right? An independent review, a second method, and a corrected joint model. |
| 14 | 2026-10-09 | [The corrected joint model on every instrument setting](14_corrected_model_all_instrument_settings.md) | Do the conclusions of reports 08 to 10 hold with the corrected joint model? |

A plain-language account of reports 01 to 08 is in [SUMMARY.md](SUMMARY.md).
Reports from 09 on are follow-ups. Each adds data beside an earlier report
and leaves that report's numbers as they were. They are summarised at the end
of SUMMARY.md.

**Read report 13 before quoting reports 06, 08, 10 or 12.** It corrects one
explanation in each. Those four reports carry a dated correction. **For the
joint model, quote reports 13 and 14**, which use the corrected model.
