# Candidate v1.14 Cycle 7 Hypothetical N2 Boundary Test

## Hypothesis

If the lack of N2 supply is the reason nitrogenase is infeasible, then adding a temporary diagnostic N2 boundary should make a small forced nitrogenase flux feasible without permanently editing v1.13.

## Method

Use `candidate_v1.14/scripts/test_hypothetical_n2_boundary.py`.

The script:

- temporarily adds `HYP_EX_cpd00528_c0`;
- closes ammonium uptake;
- forces `rxn06874_c0 >= 0.01`;
- compares feasibility with and without the hypothetical boundary for acetate, succinate, butyrate, and fumarate.

## Interpretation Rule

If the hypothetical boundary restores feasibility, this supports an N2 boundary curation proposal. It does not authorize editing the production model until the proposal passes evidence and regression tests.

## Result

Without hypothetical N2 boundary, `rxn06874_c0 >= 0.01` was infeasible for acetate, succinate, butyrate, and fumarate.

With temporary `HYP_EX_cpd00528_c0`, the same minimal forced nitrogenase condition became feasible for all four substrates:

- acetate objective: 7.0100
- succinate objective: 7.1025
- butyrate objective: 7.5763
- fumarate objective: 6.9199

FVA with the hypothetical boundary allowed nitrogenase ranges up to about 2.91-3.19 depending on substrate and H2 exchange maxima around 17.66-19.34. pFBA still chose H2 exchange of 0 under the forced-minimum nitrogenase setting, so H2 production remains objective/tradeoff dependent.

## Decision

The N2 boundary proposal is now evidence-supported as a candidate edit to test in a separate candidate model, but not yet accepted into v1.14. The next cycle must create a reversible candidate SBML/JSON with an N2 exchange, rerun baseline phenotype/QC diagnostics, and compare before/after nitrogenase/H2 behavior.
