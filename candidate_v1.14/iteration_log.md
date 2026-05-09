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

## Cycle 10-11 Summary

Compared v1.13 and the candidate N2-boundary model against iRpa940/Navid2019 and reran a Python version of the substrate phenotype panel.

Findings:

- The first N2 matching pass falsely counted Mn2+/Zn2+ as N2; the comparison script was corrected to use exact N2/dinitrogen matching.
- iRpa940 has an N2 boundary; v1.13 does not.
- The candidate N2-boundary model preserves the current phenotype panel: 16/16 expected-design checks pass or pass as structural negatives, matching v1.13.
- Fructose remains a controlled negative: exchange exists but no transport-driven growth is detected.

Decision:

The candidate N2 boundary model has passed Python phenotype regression and reference-model adversarial screening. Continue to MEMOTE and nitrogen-fixing/H2 validation.

## Cycle 12 Summary

Ran paired MEMOTE snapshots for frozen v1.13 and the candidate N2-boundary model, then parsed the HTML reports into TSV comparison tables.

Findings:

- v1.13 MEMOTE: total score 0.3721140138609879; 139 failed, 114 passed, 10 skipped.
- candidate N2-boundary MEMOTE: total score 0.3721009059825648; 139 failed, 114 passed, 10 skipped.
- The candidate does not introduce a new MEMOTE pass/fail regression, but the absolute quality profile is not publication-ready.

Tightened the nitrogen/H2 validation by closing all original nitrogen-containing uptake boundaries before selectively reopening ammonium or N2.

Adversarial finding:

- The earlier nitrogen diagnostic was too permissive because lysine, aspartate, glutamine, methionine, biotin, and B12 exchange could remain open.
- Under strict nitrogen-source control, ammonium-only acetate growth is zero in both v1.13 and the candidate.
- Methionine plus ammonium partially rescues both models.
- Candidate v1.14, but not v1.13, can grow under N2 plus methionine with forced nitrogenase.

Decision:

The N2 boundary remains a defensible v1.14 candidate edit, but the model is not yet ready for publication claims about minimal nitrogen-fixing growth. The next cycle should audit methionine biosynthesis/sulfur metabolism and distinguish true experimental medium supplements from model gaps.

## Cycle 13 Summary

Audited the methionine module under strict ammonium-acetate conditions after closing all nitrogen-containing uptake boundaries.

Finding:

- Methionine, homocysteine, cystathionine, and cysteine have zero net production capacity.
- Homoserine and O-acetyl/O-succinyl-homoserine precursors are producible.
- Sulfate is available, but reduced sulfur assimilation into cysteine/H2S/methionine appears blocked under the strict condition.

Decision:

Do not treat methionine uptake as a model fix. It is currently a diagnostic rescue and possible medium supplement. The next iteration should resolve sulfur assimilation and methionine biosynthesis with gene/literature evidence before claiming minimal-medium nitrogen-fixing growth.
