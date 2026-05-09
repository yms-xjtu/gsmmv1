# Memory Restore After Chat Clear

This file preserves the current project state in the repository so the work can continue even if the chat memory is cleared.

## Repository

GitHub: `https://github.com/yms-xjtu/gsmmv1.git`

Current pushed remote `main` before this memory-restore note:

- `01012478765a47daddaf7a72abdcb1664eb1f1a0`

Local working directory used in this run:

- `E:\model\gsmmv1_next_run`

## Core User Requirement

Continue iterating the R. palustris CGA009/TX73 genome-scale metabolic model from frozen trusted v1.13 toward publication-grade predictive credibility.

Do not stop after one pass. Do not merely give advice. Keep running build-test-criticize-rebuild cycles until either:

1. a candidate model is reproducibly stronger than v1.13 and satisfies the publication gates, or
2. a true external blocker is reached, such as missing wet-lab data, inaccessible proprietary data, or paid-database access.

Use Python/COBRApy as the default path. MATLAB is optional only. Do not repeatedly ask the user for yes/no confirmations during normal curation and validation.

## Must Read First After Restart

1. `next_agent/NEXT_AGENT_PROMPT.md`
2. `skills/cga009-top-journal-modeling/SKILL.md`
3. `candidate_v1.14/iteration_log.md`
4. `candidate_v1.14/v1_14_cycle12_memote_and_strict_nitrogen_validation.md`
5. `candidate_v1.14/v1_14_cycle13_methionine_gap_audit.md`
6. `evidence/LITERATURE_READING_PROTOCOL.md`
7. `evidence/literature_evidence.tsv`

## Frozen Baseline

Do not modify v1.13 directly.

Baseline files:

- `baseline/mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml`
- `baseline/mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_20260508.xlsx`
- `baseline/cga009_phenotype_profile_results.tsv`

## Current Candidate

Candidate v1.14 is a low-risk N2-boundary candidate:

- `candidate_v1.14/candidate_model_n2_boundary/mymodel_CGA009_candidate_v1.14_n2_boundary.xml`
- Adds `EX_cpd00528_c0` for intracellular N2 metabolite `cpd00528[c0]`.
- Boundary is closed by default: lower bound `0`, upper bound `1000`.

This candidate is not publication-ready yet.

## Current Evidence And Validation State

Passed or favorable:

- Candidate v1.14 preserves Python phenotype panel: 16/16 expected-design checks pass or pass as structural negatives.
- Reference-model adversarial comparison against iRpa940 supports adding an N2 boundary because iRpa940 has N2 exchange and v1.13 lacks it.
- Candidate v1.14 does not introduce MEMOTE pass/fail regression relative to v1.13.
- Candidate v1.14, but not v1.13, can grow under `N2 + methionine + forced nitrogenase` diagnostic conditions.

Not solved:

- The absolute MEMOTE score is still low and not publication-grade:
  - v1.13 total: `0.3721140138609879`
  - candidate N2 boundary total: `0.3721009059825648`
  - both: 139 failed, 114 passed, 10 skipped
- Strict ammonium-only acetate growth is zero in both v1.13 and candidate.
- Methionine, homocysteine, cystathionine, and cysteine cannot be net-produced under strict ammonium-acetate conditions.
- This points to a sulfur assimilation / reduced sulfur / cysteine / H2S / methionine biosynthesis gap, or to an experimental medium dependence that must be explicitly documented.

## Key Output Folders

- `candidate_v1.14/reference_model_adversarial_compare/`
- `candidate_v1.14/python_phenotype_panel/`
- `candidate_v1.14/memote_baseline_v1_13/`
- `candidate_v1.14/memote_candidate_n2_boundary/`
- `candidate_v1.14/memote_comparison/`
- `candidate_v1.14/nitrogen_h2_tradeoff/`
- `candidate_v1.14/nitrogen_rescue_audit/`
- `candidate_v1.14/methionine_biosynthesis_audit/`

## Key Scripts

- `candidate_v1.14/scripts/adversarial_compare_reference_models.py`
- `candidate_v1.14/scripts/run_python_phenotype_panel.py`
- `candidate_v1.14/scripts/compare_memote_snapshots.py`
- `candidate_v1.14/scripts/run_nitrogen_h2_tradeoff.py`
- `candidate_v1.14/scripts/audit_nitrogen_rescue_supplements.py`
- `candidate_v1.14/scripts/audit_methionine_biosynthesis.py`

Run with:

```powershell
E:\model\memote_py312\Scripts\python.exe candidate_v1.14\scripts\run_python_phenotype_panel.py
E:\model\memote_py312\Scripts\python.exe candidate_v1.14\scripts\adversarial_compare_reference_models.py
E:\model\memote_py312\Scripts\python.exe candidate_v1.14\scripts\compare_memote_snapshots.py
E:\model\memote_py312\Scripts\python.exe candidate_v1.14\scripts\run_nitrogen_h2_tradeoff.py
E:\model\memote_py312\Scripts\python.exe candidate_v1.14\scripts\audit_nitrogen_rescue_supplements.py
E:\model\memote_py312\Scripts\python.exe candidate_v1.14\scripts\audit_methionine_biosynthesis.py
```

## Next Iteration Should Start Here

Cycle 14 should not keep polishing the N2 boundary. The current adversarial bottleneck is sulfur assimilation and methionine biosynthesis.

Immediate tasks:

1. Map sulfate uptake/reduction, sulfide/H2S production, cysteine biosynthesis, and methionine biosynthesis reactions and genes.
2. Compare these genes/reactions against iRpa940 and literature evidence.
3. Check whether missing reaction directionality, missing transport, missing sulfur metabolite boundary, or biomass/medium assumptions explain the methionine dependency.
4. Do not open methionine uptake as a model fix unless the wet-lab medium actually contains methionine.
5. If a candidate sulfur/methionine edit is proposed, create an evidence row, an audit TSV, a before/after phenotype panel, a strict nitrogen rescue rerun, MEMOTE/COBRA comparison, and an adversarial counterargument.

## Security Note

The user pasted GitHub personal access tokens into chat. Do not persist tokens in repository files. Recommend that the user revoke/rotate those tokens after pushing.

## Working Style To Preserve

Keep going autonomously. Periodically reread:

- `next_agent/NEXT_AGENT_PROMPT.md`
- `skills/cga009-top-journal-modeling/SKILL.md`
- this file

The project succeeds only when the model can defend growth predictions, exchange fluxes, and internal flux distributions against adversarial review and wet-lab growth validation.
