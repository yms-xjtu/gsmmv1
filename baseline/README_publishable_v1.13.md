# CGA009 publishable V1 model summary

This first-version package was generated from the curated Excel workbook and deterministic validation scripts.

## Key results
- Model size: 1021 reactions and 979 metabolites.
- Custom deterministic QC score: 96.22/100.
- Expected-design phenotype pass rate: 100.0%.
- PHB maximum flux on acetate diagnostic condition: 52.036.
- H2 exchange at PHB maximum: 0.000.

## Figure files
- figure1_phenotype_net_growth.svg
- figure1_phenotype_net_growth.png
- figure2_phenotype_matrix.svg
- figure2_phenotype_matrix.png
- figure3_model_qc_score.svg
- figure3_model_qc_score.png
- figure4_phb_prediction.svg
- figure4_phb_prediction.png
- figure5_curation_evidence.svg
- figure5_curation_evidence.png

## Caution
- NADPH/NADP is reported as a flux-turnover diagnostic, not as a directly constrained concentration ratio.
- The PhaB/PhaA ratio is an FBA flux diagnostic and should not be read as direct enzyme capacity without kinetic/proteomic evidence.
