# Candidate v1.14 Cycle 2 Adversarial Review

## Claim Being Tested

The McKinlay/Harwood 13C-H2 paper and the CGA009 ME-model paper can define a first validation target set for v1.13 without changing model stoichiometry.

## Evidence Supporting The Claim

- McKinlay/Harwood reports H2 yields for fumarate, succinate, acetate, and butyrate, plus Calvin-cycle electron-carrier oxidation fractions.
- The CGA009 ME-model paper reports experimental growth rates and substrate uptake rates for succinate, acetate, and butyrate under nitrogen-fixing photoheterotrophic growth.
- v1.13 contains identifiable H2, nitrogenase, CBB/RuBisCO, CO2, acetate, succinate, butyrate, fumarate, ferredoxin, and PHB reaction IDs.

## Strongest Counterargument

The validation targets are not yet sufficient for hard model constraints because the exact experimental media, strain variants, unit conversions, objective scaling, photon bounds, bicarbonate availability, nitrogenase activation state, and uptake rates are not all harmonized with v1.13. Also, some extracted values came from searchable text/BioNumbers and must be verified against the full article or supplement before being used as hard constraints.

## Test Performed

- Mapped key validation concepts to v1.13 reaction IDs.
- Recorded which targets are validation-only versus constraint-ready.
- Checked exchange bounds and found several literature substrates are closed for uptake in the baseline SBML (`succinate`, `butyrate`, `fumarate` lower bound 0), while acetate is open at -1.96.

## Decision

Keep these as validation targets and condition-building inputs. Do not edit v1.13 or impose hard ecGEM/TFA/MFA constraints yet.

## Next Cycle

Build a Python condition runner that creates temporary, reversible substrate conditions for acetate, succinate, butyrate, and fumarate, then evaluates biomass, H2, CBB/RuBisCO, nitrogenase, PHB, CO2, and ferredoxin flux ranges. This must be treated as diagnostic FVA/tradeoff analysis, not final biological truth.
