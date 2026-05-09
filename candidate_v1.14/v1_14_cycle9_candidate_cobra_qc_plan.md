# Candidate v1.14 Cycle 9 Candidate COBRA QC Plan

## Hypothesis

The default-closed N2 boundary candidate should not change baseline model size except by one reaction, should not add missing formulas/charges, and should not increase internal checkable mass/charge imbalances.

## Method

Use `candidate_v1.14/scripts/run_candidate_n2_cobra_qc.py`.

The script compares v1.13 baseline SBML and the candidate N2-boundary SBML for:

- reaction, metabolite, and gene counts;
- missing formula and missing charge metabolite counts;
- FBA objective;
- internal checkable mass/charge imbalances, excluding exchange/single-metabolite and biomass/pseudo reactions.

## Decision Rule

If only reaction count changes by +1 and internal imbalances do not increase, the candidate can advance to MEMOTE/phenotype regression. If internal imbalances increase, reject or revise the boundary.

## Result

COBRA QC passed:

- baseline reactions: 1021
- candidate reactions: 1022
- metabolites unchanged: 979
- genes unchanged: 685
- missing formula metabolites unchanged: 0
- missing charge metabolites unchanged: 0
- FBA objective unchanged to numerical tolerance: 10.545509652968153 vs 10.545509652968292
- internal checkable imbalances unchanged: 33 vs 33
- no new imbalanced internal reaction IDs

## Decision

The default-closed N2 boundary candidate advances to MEMOTE/phenotype regression. It is still not final until those checks are complete and condition-specific N2 opening is demonstrated without damaging non-nitrogen-fixing phenotypes.
