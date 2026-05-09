# Candidate v1.14 Cycle 3 Diagnostic Plan

## Hypothesis

A reversible Python condition runner can expose whether v1.13 produces biologically plausible growth and readout fluxes under acetate, succinate, butyrate, and fumarate conditions before any model edit.

## Scope

This is diagnostic only. It does not replace measured exchange constraints and does not claim exact reproduction of McKinlay/Harwood or the CGA009 ME-model.

## Readouts

- `bio1`: growth objective
- `EX_cpd11640_e0`: H2 exchange
- `EX_cpd00011_e0`: CO2 exchange
- `rxn06874_c0`: nitrogenase
- `rxn00018_c0`: RuBisCO / CBB CO2 fixation step
- `rxn01111_c0`: phosphoribulokinase / RuBP regeneration
- `rxn05759_c0`: hydrogen:ferredoxin oxidoreductase
- `rxn15455_c0`: PHB polymerization proxy

## Interpretation Rule

If a substrate fails to grow in this diagnostic condition, do not immediately gap-fill. First check medium definition, exchange direction, pH/proton conventions, light/photon bound, nitrogen source, and missing uptake evidence.

If H2, CBB, nitrogenase, or PHB flux is extreme, treat it as a sign of under-constrained FBA and prioritize pFBA/FVA, enzyme capacity, and measured exchange rates.

## Result

The first minimal-medium diagnostic produced `objective_value = 0` for acetate, succinate, butyrate, and fumarate. However, FVA still allowed large H2 and CBB flux ranges at zero biomass. This is not acceptable as a biological validation result.

## Decision

Reject the minimal-medium diagnostic as a growth-condition reproduction. Keep its outputs as a failure record showing that medium definition is a first-order problem.

Next cycle should use a more conservative "baseline medium with carbon-source switch" diagnostic: preserve the original v1.13 exchange bounds, close only existing carbon-source uptake reactions, and open one target substrate at a time. This avoids accidentally removing baseline nutrients that the curated v1.13 workbook expects.
