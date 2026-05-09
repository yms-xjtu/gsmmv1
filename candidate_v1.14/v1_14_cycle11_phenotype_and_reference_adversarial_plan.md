# Candidate v1.14 Cycle 11 Phenotype And Reference Adversarial Plan

## Hypothesis

The candidate N2 boundary model can pass the same substrate growth phenotype panel as v1.13 while resolving the reference-model discrepancy around N2 supply.

## Work Items

1. Fix false-positive N2 matching in the reference comparison script so Mn2+/Zn2+ are not counted as N2.
2. Rerun reference-model adversarial comparison.
3. Run a Python reproduction of the substrate phenotype panel on both v1.13 and the candidate N2-boundary model.

## Decision Rule

The candidate can continue only if:

- expected positive substrates remain growth-positive;
- expected negative substrates do not gain substrate-specific growth;
- forced-open fructose remains non-growing;
- reference-model discrepancy is limited to evidence-supported N2 boundary, not broad phenotype conflicts.

## Result

Python phenotype regression passed for both models:

- v1.13 baseline: 16/16 expected-design tests pass or pass as structural negatives.
- candidate N2-boundary model: 16/16 expected-design tests pass or pass as structural negatives.
- no fail-like rows were observed.

Reference-model adversarial comparison found two actionable concerns:

1. Fructose has an exchange in v1.13/candidate but no transport, and forced-open fructose still does not grow. This supports the current negative phenotype classification rather than a model edit.
2. iRpa940 includes an N2 boundary, while v1.13 lacks an N2 boundary. This supports the candidate N2 boundary edit, especially because the candidate boundary is closed by default and does not regress the phenotype panel.

## Decision

The candidate N2 boundary model passes the current growth-experiment phenotype gate. Continue to MEMOTE and condition-specific nitrogen-fixing/H2 validation before final acceptance.
