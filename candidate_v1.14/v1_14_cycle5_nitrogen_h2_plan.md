# Candidate v1.14 Cycle 5 Nitrogen/H2 Diagnostic Plan

## Hypothesis

The current pFBA zero-H2 result is caused by nitrogen regime and objective choice rather than absence of H2-producing capacity. Closing ammonium or forcing a minimal nitrogenase flux should expose whether v1.13 can route electrons through nitrogenase/H2 under carbon-source conditions.

## Method

Use `candidate_v1.14/scripts/run_nitrogen_h2_tradeoff.py`.

For acetate, succinate, butyrate, and fumarate:

- preserve baseline medium except carbon-source switch;
- compare ammonium-open, ammonium-closed, and minimal-nitrogenase regimes;
- report biomass, H2 exchange, nitrogenase flux, and FVA ranges for H2/CBB/nitrogenase readouts.

## Interpretation Rule

If closing ammonium alone does not induce nitrogenase, check whether N2 exchange/metabolite availability is represented in v1.13 and whether the model uses an internal dinitrogen pool. Do not force biological conclusions from a missing boundary condition.

## Result

For acetate, succinate, butyrate, and fumarate:

- ammonium-open and ammonium-closed regimes produced the same growth values and zero pFBA H2/nitrogenase flux;
- FVA still allowed H2 through `EX_cpd11640_e0` and `rxn05759_c0`;
- `rxn06874_c0` nitrogenase FVA stayed fixed at zero;
- forcing `rxn06874_c0 >= 0.01` made all four conditions infeasible.

The model contains intracellular dinitrogen `cpd00528[c0]` in `rxn06874_c0` but no extracellular dinitrogen exchange was found.

## Decision

Do not impose nitrogenase/H2 constraints yet. The next evidence-supported task is an N2 boundary and nitrogen-source audit. If a dinitrogen exchange or transport is absent, adding one would be a model edit and requires explicit evidence, audit, and before/after validation.

## Next Cycle

Create an N2 boundary audit that documents all reactions involving `cpd00528[c0]`, all nitrogen-source exchanges, and whether a reversible, evidence-supported dinitrogen supply boundary is needed for nitrogen-fixing/H2 validation conditions.
