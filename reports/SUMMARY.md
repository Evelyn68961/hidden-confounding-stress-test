# What this project found, in plain words

A summary of reports 01 to 13. Each claim below points to the report that
holds the numbers, the checks and the limits. Written 2026-10-08; the
follow-ups section and the verification section were added on 2026-10-09.
Findings 5, 6 and 11 are corrected by finding 12.

## The question

Treatment selection models learn from health records which drug works best
for which patient. In records, doctors choose drugs for reasons that are often
not written down. If such a hidden reason also affects how patients do, a
model can mistake it for an effect of the drug.

In real records this cannot be checked, because each patient takes one drug.
In a simulation the truth is known. So this project asks, for simulated people
with type 2 diabetes choosing between an SGLT2 inhibitor and a GLP-1 receptor
agonist:

1. How wrong does a model get as a hidden factor gets stronger, and does the
   form of the hidden factor matter?
2. Does a model that describes drug choice and outcome together do better?
3. Would the usual way of validating such models notice the problem?

## The setup

- **Patients.** Simulated, 5,000 per dataset, tuned to reproduce summary
  figures printed in Cardoso et al., *Diabetologia* 2024. No patient data were
  used ([calibration](../docs/calibration.md)).
- **The hidden factor.** One number per patient that makes the GLP-1 drug more
  likely and the result worse. Two settings: its **strength** (0.5 is about as
  strong on drug choice as BMI; 1 is twice that) and the **shape** of its
  effect on the outcome (`linear`, `threshold`, or `effect`, where it changes
  how well one drug works) ([report 02](02_what_the_hidden_factor_does.md)).
- **Models.** A Bayesian causal forest; a plain regression in which the drug
  effect varies with patient features; and a joint model that adds a model of
  drug choice and lets the unexplained parts of choice and outcome be linked.
- **Scoring.** Against the known truth: the error in the average effect, the
  share of 95% intervals that contain the truth, and the share of patients
  the model would send to the worse drug.

## What was found

### 1. With nothing hidden, the models are honest

The causal forest shows no systematic error and its 95% intervals contain the
truth 94% of the time. At 5,000 patients it still sends about one patient in
six to the worse drug, mostly patients for whom the two drugs are close
([report 03](03_causal_forest_grid.md)).

### 2. A hidden factor passes straight through, whatever the model

With the hidden factor on, the forest's error in the average effect equals
that of simply comparing the two drug groups (4.44 against 4.40 mmol/mol for
the linear shape at strength 1). The plain regression does the same (4.39). A
moderate hidden factor does modest damage: the share sent to the worse drug
rises from 16.5% to about 20%. A strong one sends 34% to 43% to the worse
drug, where choosing at random would send 50%
([report 03](03_causal_forest_grid.md), [report 06](06_joint_model_grid.md)).

### 3. The models give no warning

At strength 1, only 28% to 50% of the forest's 95% intervals contain the
truth, and 9% to 27% of the plain regression's. The models are as confident
as before while being right far less often.

### 4. The form of the hidden factor matters

At equal strength, the linear form does the most damage and the effect form
the least, for every model.

### 5. A joint model without an instrument does not find the hidden factor

In none of 140 fits did the joint model detect the link between drug choice
and outcome, and it did not correct the bias. It did widen its intervals, so
that about 80% contained the truth at strength 1. It stopped being confident
about a wrong answer ([report 06](06_joint_model_grid.md)). The same model
recovers a strong link when the data make that possible
([report 05](05_joint_model_trial_and_check.md)).

### 6. With an instrument, it corrects most of the bias

An instrument is something that moves drug choice and affects the outcome in
no other way. Given a strong one, the joint model cut the error in the average
effect from 3.77 to 0.95 (linear shape, strength 1) and the share sent to the
worse drug from 35% to 17%. A weaker instrument corrected less. The correction
was smaller when the hidden factor's form departed from the model's
assumptions: 75% of the error removed for the linear form, 64% for the
threshold form, 40% for the effect form. The joint model is also noisier, and
does slightly worse than the plain regression when nothing is hidden
([report 08](08_instrument.md)).

### 7. The usual validation check does not notice

Models of this kind are validated by comparing patients who received the
recommended drug with matched patients who did not. With nothing hidden, the
check works. With a hidden factor, it agreed with the misled model: the plain
regression predicted a benefit of 4.82 mmol/mol, the check observed 4.93, and
the true benefit was 0.70. The same hidden factor made the check disagree
with a model that was exactly right ([report 07](07_validation_check.md)).

## Follow-ups (reports 09 to 12, added 2026-10-09)

Four further runs tested how far findings 5 and 6 can be trusted. The numbers
above are unchanged; these sit beside them.

### 8. The instrument result holds on new datasets

On ten new datasets per setting, a strong instrument removed 72% of the error
for the linear form, 68% for threshold and 39% for effect, against 75%, 64%
and 40% on the first ten. With nothing hidden, the joint model reported a
hidden link in 3 of 40 fits, which is about what chance allows
([report 09](09_instrument_twenty_datasets.md)).

### 9. A slightly flawed instrument is worse than none

An instrument shared by all the patients of a practice corrected as well as
an ideal one. An instrument that also affects the outcome directly, by as
little as 1 mmol/mol, made the joint model worse than the plain regression
(an error of 5.90 against 4.51). With nothing hidden it created an error of
4.55 where the plain regression had 0.99, and the model reported a hidden
link in all ten datasets. The flaw is credited to the drug at about five
times its size ([report 10](10_less_ideal_instruments.md)).

### 10. An instrument must not be used as an ordinary feature

Added to the plain regression like any other feature, the instrument made the
error 13% to 17% larger in every setting with a hidden factor
([report 11](11_instrument_as_a_feature.md)).

### 11. More patients do not replace an instrument

With 20,000 patients and no instrument, the joint model still estimated no
link, and its error was unchanged (4.23). Its intervals narrowed, so the share
containing the truth fell from 84% to under 1%. The honest intervals of
finding 5 were a result of having few patients
([report 12](12_more_patients.md)).

### 12. Verification, and a correction to findings 5, 6 and 11

An independent code review found no error that changes a number, and least
squares reproduced the plain regression exactly. The review did find a
mismatch: the joint model assumed one noise level for both drugs, and the
simulated patients have two.

With that removed, and an ideal instrument, the joint model corrects all of
the error for the linear form, 92% for threshold and 54% for effect, where
finding 6 reported 75%, 64% and 40%. A classical two-step method agrees.
It is also more variable, so one dataset's answer is no closer to the truth.

Without an instrument, the corrected model is not confidently wrong, as
findings 5 and 11 described. It is very uncertain, and its answers swing by
several mmol/mol between datasets. A joint model still needs an instrument;
the reason is that the data hold almost no information about the link without
one ([report 13](13_verification_and_corrected_joint_model.md)).

## What this does not show

- **Nothing here is about real patients.** The size of any hidden factor in
  real prescribing is unknown. Strength 1 is a severe setting.
- **It is not a verdict on any published model.** The published models were
  also validated in randomised trials, where a hidden factor cannot drive the
  choice of drug. This simulation has no trial arm.
- **The simulation is one design among many.** The patients match printed
  summary figures from one paper, and several effect sizes were chosen. The
  hidden factor is unrelated to every recorded feature, which is the hardest
  case; in real records part of it would show through other features.
- **The joint model is the simplest of its kind.** It assumes bell-shaped
  errors and straight-line effects. Flexible versions (Dirichlet process
  mixtures, Bayesian additive regression trees) were not implemented, so
  nothing here shows what they would achieve.
- **The instrument is ideal.** A real one has to be argued for.
- **5,000 patients per dataset.** Published models use many more.

## Reproducibility

Every run is a numbered script, every result file records the code commit
that produced it, and the long runs were shared between two computers that
were shown to give identical results for the same data
([report 04](04_cross_computer_check.md)).
