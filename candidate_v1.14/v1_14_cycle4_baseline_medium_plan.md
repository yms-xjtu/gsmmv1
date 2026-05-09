# Candidate v1.14 Cycle 4 Baseline-Medium Carbon-Switch Plan

## Hypothesis

The zero-growth result in cycle 3 was caused by an overly strict reconstructed medium, not necessarily by missing metabolism. Preserving baseline exchange bounds and only switching known carbon-source uptake reactions should recover growth in at least the baseline acetate condition.

## Method

Use `candidate_v1.14/scripts/run_baseline_medium_carbon_switch.py`.

The script:

- preserves the original v1.13 exchange bounds;
- closes known carbon-source uptake reactions;
- opens one target substrate at a time;
- runs FBA, pFBA, and FVA for biomass, H2, CO2, nitrogenase, CBB, ferredoxin-H2, and PHB readouts.

## Decision Rule

If acetate growth is recovered, use this script as the safer diagnostic condition builder for v1.14.

If acetate still fails, audit baseline exchange requirements directly from the validated phenotype script or original Excel workbook before any model edit.

## Result

The baseline-medium carbon-switch diagnostic recovered growth in every tested condition:

- baseline unchanged: 10.5455
- acetate current bound: 7.0124
- succinate ME uptake: 7.1049
- butyrate ME uptake: 7.5787
- fumarate panel: 6.9223

pFBA chose zero H2 and zero nitrogenase flux in all tested conditions, while FVA at 90% optimum allowed nonzero H2 and large CBB/RuBisCO ranges. This means the network has latent H2/CBB capacity, but the current diagnostic does not reproduce nitrogen-fixing/H2-producing conditions.

## Decision

Keep `run_baseline_medium_carbon_switch.py` as the safer condition builder for v1.14 diagnostics. Do not interpret pFBA zero H2 as contradiction of McKinlay/Harwood until nitrogen source, N2 availability, ammonium repression, and objective/tradeoff settings are matched.

Next cycle: build a nitrogen-condition/H2 tradeoff diagnostic using baseline-medium carbon-switch conditions, closing ammonium uptake and checking whether nitrogenase/H2 becomes required or feasible.
