# Candidate v1.14 Cycle 8 Candidate N2 Boundary Model Plan

## Hypothesis

Adding an N2 exchange boundary that is closed for uptake by default can preserve baseline behavior while allowing condition-specific nitrogen-fixing/H2 diagnostics to open N2 supply explicitly.

## Method

Use `candidate_v1.14/scripts/build_candidate_n2_boundary_model.py`.

The candidate edit:

- adds `EX_cpd00528_c0`;
- uses existing intracellular `cpd00528[c0]`;
- sets lower bound to `0.0` and upper bound to `1000.0` by default;
- exports candidate SBML and JSON;
- does not alter v1.13 baseline files.

## Required Tests Before Acceptance

1. Baseline unchanged growth comparison.
2. Carbon-switch condition comparison.
3. Nitrogenase/H2 tradeoff with N2 opened only for nitrogen-fixing conditions.
4. MEMOTE/COBRA validation.
5. Phenotype panel regression check.

## Acceptance Status

Not accepted yet. This is a candidate model artifact for testing.

## Result

The candidate model with `EX_cpd00528_c0` closed for uptake by default reproduced baseline and carbon-switch objective values to numerical tolerance:

- baseline unchanged: 10.545509652968153 vs 10.545509652968292
- acetate: 7.012417318145626 vs 7.012417318145600
- succinate: 7.104909834918660 vs 7.104909834918646
- butyrate: 7.578673497522972 vs 7.578673497522937
- fumarate: 6.922311475211926 vs 6.922311475211909

FVA readout ranges for biomass, H2 exchange, CBB/RuBisCO, PRK, ferredoxin-H2, and nitrogenase were unchanged when N2 uptake remained closed.

## Decision

The default-closed N2 boundary is a low-risk candidate edit for v1.14 because it does not change baseline behavior until condition scripts explicitly open N2 uptake. It is still not accepted as final because the expanded phenotype panel and MEMOTE/COBRA checks have not yet been rerun on the candidate SBML.

Next cycle should run MEMOTE or a lightweight COBRA consistency audit on the candidate model, then implement a condition-specific nitrogen-fixing diagnostic where `EX_cpd00528_c0` is opened only for literature-matched nitrogen-fixing/H2 conditions.
