# Prompt For The Next Agent

You are taking over a Rhodopseudomonas palustris CGA009/TX73 genome-scale metabolic model project. Your job is to improve the model from a trustworthy frozen baseline to top-journal-level predictive credibility.

Start from this repository root. Use the bundled skill:

`skills/cga009-top-journal-modeling/SKILL.md`

Baseline:

`baseline/mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_20260508.xlsx`

SBML for MEMOTE/COBRA:

`baseline/mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml`

Read first:

1. `baseline/CLAUDE_HANDOFF_V1.13_20260509.md`
2. `evidence/literature_evidence.tsv`
3. `evidence/phenotype_data_requirements.tsv`
4. `skills/cga009-top-journal-modeling/references/top_journal_strategy.md`

Mission:

Build the next publishable version by integrating three constraint layers: enzyme-capacity constraints (ecGEM/ME-model), thermodynamic flux analysis (TFA), and 13C-MFA validation. Do not chase a single reaction or single phenotype. Improve the whole model's reliability.

Rules:

1. Keep v1.13 frozen until a candidate release passes stronger validation.
2. Every model edit must have a source, audit record, before/after validation, and counterargument.
3. Run adversarial analysis at every step: write the best argument against your change, then test it.
4. Separate measured constraints, literature-derived constraints, and sensitivity-only assumptions.
5. Never add exchanges/transports or change bounds just to force growth.
6. Do not make one-off edits in porphyrin/chlorophyll/cobalamin, tRNA pseudo-metabolites, or carrier-convention modules until pathway-wide conventions are solved.
7. Keep all scripts deterministic so another person can rerun from a clean clone.

First deliverables:

1. A `candidate_v1.14/` folder with scripts, changed files, and audit TSVs.
2. A baseline reproduction report showing that v1.13 metrics can be regenerated.
3. A data-gap report mapping each desired ecGEM/TFA/13C-MFA constraint to available or missing data.
4. A no-hallucination evidence ledger with URLs/DOIs and exact fields extracted.
5. A rejection log of tempting but unsupported shortcuts.

Success criterion:

The model is only better when it predicts growth phenotypes, exchange fluxes, and internal flux distributions more accurately without losing stoichiometric, thermodynamic, and biological credibility.
