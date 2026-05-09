# Candidate v1.14 Cycle 10 Reference Model Adversarial Comparison

## Hypothesis

Comparing v1.13 and the candidate N2-boundary model against iRpa940/Navid2019 can reveal likely model errors or missing boundary conditions that are not obvious from single-model FBA.

## Reference Model

`candidate_v1.14/reference_models/iRpa940_SBML_model.xml`

This model comes from the local Navid2019/iRpa940 supplementary files and is used as a reference, not a truth source. Strain, objective, compartments, identifiers, and medium conventions can differ.

## Method

Run `candidate_v1.14/scripts/adversarial_compare_reference_models.py`.

The script compares:

- model size and basic COBRA QC;
- exchange support for positive and negative phenotype-panel substrates;
- N2, H2, CO2 exchange support;
- key modules: nitrogenase, H2, CBB/RuBisCO, PHB, ferredoxin.

## Decision Rule

Do not copy reactions from iRpa940 automatically. A discrepancy becomes an actionable candidate only if it also has:

- CGA009/TX73 or R. palustris literature evidence;
- no regression in current phenotype validation;
- clear before/after model tests.
