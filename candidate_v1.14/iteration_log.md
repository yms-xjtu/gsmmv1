# Candidate v1.14 Iteration Log

## Cycle 1

Hypothesis: Before editing reactions, v1.13 should be reproducible through a Python-only path and the first evidence ledger should identify safe next constraints.

Actions:

- Cloned `https://github.com/yms-xjtu/gsmmv1.git`.
- Read the next-agent prompt, bundled skill, literature protocol, evidence ledger, phenotype data requirements, baseline handoff, and top-journal strategy.
- Ran the package integrity check successfully.
- Ran Python/COBRApy baseline reproduction with GLPK.
- Created first-pass evidence extraction, data-gap report, and rejected-shortcuts log.

Decision:

- Keep the cycle outputs.
- Do not edit the model yet. The evidence gate is now started, but hard ecGEM/TFA/13C-MFA constraints require more extraction from full papers, supplements, BRENDA/SABIO-RK, and metabolomics sources.

Next falsifiable hypothesis:

The McKinlay/Harwood 13C flux paper plus Navid/iRpa940 conditions can define a first internal-flux validation panel for acetate, succinate, and butyrate without changing v1.13 stoichiometry.

## Cycle 2-8 Summary

Continued work after the first evidence gate:

- Mapped H2, nitrogenase, CBB/RuBisCO, carbon-source, ferredoxin, CO2, and PHB modules to v1.13 reaction IDs.
- Created `mfa_validation_targets.tsv` with H2 yield, CBB electron oxidation, and ME-model growth targets.
- Rejected an overly strict minimal-medium diagnostic because it produced zero growth and would risk false gap-filling.
- Built a safer baseline-medium carbon-switch diagnostic that recovered growth for acetate, succinate, butyrate, and fumarate.
- Found pFBA chooses zero H2/nitrogenase under current conditions, while FVA allows H2/CBB flexibility.
- Audited nitrogen boundaries and found intracellular N2 but no N2 exchange.
- Demonstrated that a temporary N2 boundary restores feasibility of forced minimal nitrogenase.
- Built a candidate N2 boundary model with N2 uptake closed by default.
- Confirmed the default-closed N2 boundary does not change baseline growth or readout FVA.

Current decision:

The N2 boundary is a low-risk candidate edit but is not yet accepted as final. Continue with candidate MEMOTE/COBRA checks and condition-specific nitrogen-fixing/H2 validation.

## Cycle 9 Summary

Ran lightweight Python/COBRA QC comparing v1.13 and the candidate N2-boundary model.

Result:

- Candidate adds exactly one reaction: `EX_cpd00528_c0`.
- No metabolite or gene count changes.
- Missing formulas and charges remain zero.
- FBA objective is unchanged to numerical tolerance.
- Internal checkable imbalances remain unchanged.

Decision:

Advance the N2 boundary candidate to MEMOTE/phenotype regression. Do not finalize until those checks pass.
