# Candidate v1.14 Cycle 6 Nitrogen Boundary Plan

## Hypothesis

Nitrogenase is infeasible when forced because v1.13 lacks an explicit N2 supply boundary or has nitrogen-source conventions that do not match nitrogen-fixing literature conditions.

## Method

Use `candidate_v1.14/scripts/audit_nitrogen_boundaries.py` to list all nitrogen-related reactions and metabolites, especially `cpd00528[c0]` dinitrogen and exchange reactions.

## Decision Rule

If no N2 exchange is present, do not immediately add one. First record the absence, cite the nitrogenase reaction evidence, and create a proposed edit requiring:

- N2 exchange/transport stoichiometry;
- no biomass or phenotype regression;
- FVA before/after effect on `rxn06874_c0` and `EX_cpd11640_e0`;
- literature evidence that the condition is nitrogen-fixing.

## Result

The audit found:

- `cpd00528[c0]` exists as intracellular N2.
- `cpd00528[c0]` participates in `rxn06874_c0` nitrogenase and `rxn39362_c0`.
- No N2 exchange reaction is present.
- Closing ammonium does not force nitrogenase because biomass can still be supported through other nitrogen pools/bounds in the baseline medium.

## Decision

Do not add N2 boundary to the frozen v1.13 baseline yet. Create a reversible test to determine whether a hypothetical N2 demand/supply boundary would make nitrogenase feasible and how it changes H2/FVA behavior.
