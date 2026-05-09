# Claude Handoff: CGA009/TX73 GEM V1.13

Date: 2026-05-09

## Current Recommended Workbook To Back Up

`mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_20260508.xlsx`

This is the latest validated Excel workbook. It supersedes v1.12 for current work.

## What Changed Since V1.12

V1.13 makes two physical reaction-stoichiometry edits in the LPS/lipid A ACP acyltransferase module:

- `rxn06729_c0`: removed `cpd00067[c0]` from the reactant side.
- `rxn06723_c0`: added `cpd00067[c0]` to the product side.

Evidence:

- `rxn06729_c0`: KEGG R04567 / EC 2.3.1.129 / Rhea 67812 support the LpxA acyltransferase reaction without H+.
- `rxn06723_c0`: Rhea 53836 / EC 2.3.1.191 support the LpxD acyltransferase reaction with H+ as a product.

No GPR, bound, objective, metabolite formula, or metabolite charge was changed in v1.13.

Audit:

- `v1.13_lps_acp_acyltransferase_audit.tsv`
- Script: `scripts/build_v1_13_lps_acp_acyltransferase.py`

## MATLAB / COBRA / Gurobi Validation

MATLAB/COBRA script:

- `scripts/run_v1_13_lps_acp_matlab_qc_sbml.m`

Outputs:

- `matlab_qc_v1.13_lps_acp_acyltransferase/cobra_matlab_qc_summary.tsv`
- `matlab_qc_v1.13_lps_acp_acyltransferase/internal_imbalanced_reactions.tsv`
- `memote_export_v1.13_lps_acp_acyltransferase/mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml`

Key MATLAB QC result:

- reactions: 1021
- metabolites: 979
- internal reactions: 945
- imbalanced internal reactions: 47
- metabolites missing formula: 0

V1.12 had 49 imbalanced internal reactions, so v1.13 removed 2 verified imbalances.

## Phenotype Validation

Validation output:

- `validation_v1.13_lps_acp_acyltransferase_curated_medium/cga009_phenotype_mfa_phb_validation_report.xlsx`

Result:

- pass: 12
- pass_structural_negative: 4
- diagnostic_ok: 2
- background_control: 2
- false-positive reaction table is header-only.

The validated substrate phenotype panel remains intact.

## MEMOTE

Annotated SBML:

- `memote_export_v1.13_lps_acp_acyltransferase/mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_memote_annotated.xml`

HTML report:

- `memote_report_v1.13_lps_acp_acyltransferase/memote_v1.13_lps_acp_acyltransferase_annotated.html`

Extracted MEMOTE scores:

- total: 67.8836%
- consistency: 55.6440%
- metabolite annotation: 33.9145%
- reaction annotation: 65.3825%
- gene annotation: 33.3333%
- SBO: 90.9091%

Failed-test table:

- `memote_report_v1.13_lps_acp_acyltransferase/memote_v1.13_lps_acp_acyltransferase_annotated.failed_tests.tsv`

## Figures And Tables

Figures:

- `figures_v1.13_lps_acp_acyltransferase/figure1_phenotype_net_growth.svg`
- `figures_v1.13_lps_acp_acyltransferase/figure2_phenotype_matrix.svg`
- `figures_v1.13_lps_acp_acyltransferase/figure3_model_qc_score.svg`
- `figures_v1.13_lps_acp_acyltransferase/figure4_phb_prediction.svg`
- `figures_v1.13_lps_acp_acyltransferase/figure5_curation_evidence.svg`
- `figures_v1.13_lps_acp_acyltransferase/figure6_remaining_imbalance_modules.svg`

Module review:

- `v1.13_remaining_imbalanced_module_review.tsv`
- `V1.13_REMAINING_IMBALANCE_MODULE_REVIEW.md`

Flux-constraint/publication plan:

- `V1.13_FLUX_CONSTRAINT_AND_PUBLICATION_ANALYSIS_PLAN.md`

Versioned summary:

- `README_publishable_v1.13.md`
- `v1.13_publication_summary_metrics.tsv`

## Important Remaining Decisions

1. `cpd11911[c0]` tRNA(Gln) conflict:
   - `rxn06436_c0` and `rxn06437_c0` require conflicting free-tRNA pseudoformula/charge conventions.
   - Do not edit without curator decision.

2. Porphyrin/chlorophyll/cobalamin module:
   - `cpd02762/cpd08629/cpd08630/cpd08631` formula/proton/charge convention must be solved pathway-wide.
   - Single-reaction H+ edits can break already balanced neighboring reactions.
   - Do not physically edit until pathway-wide closure is demonstrated.

3. Generic acceptor / ferredoxin carrier module:
   - Several imbalances are carrier-convention issues.
   - Do not replace current ferredoxin charges with ModelSEED positive charges without an explicit model convention decision.

4. Biomass and pseudo-polymer reactions:
   - Treat as pseudo-module reactions and annotate clearly.
   - Do not force strict small-molecule balance.

## Software

- MATLAB with COBRA Toolbox: `D:\Program\cobratoolbox`
- MATLAB Gurobi interface: `D:\Program\gurobi1001\win64\matlab`
- MEMOTE environment: `E:\model\memote_py312`
- MEMOTE executable: `E:\model\memote_py312\Scripts\memote.exe`
- MATLAB validation uses Gurobi; MEMOTE uses GLPK because the Python MEMOTE environment is Python 3.12 and cannot use the local Gurobi 10 Python interface directly.
