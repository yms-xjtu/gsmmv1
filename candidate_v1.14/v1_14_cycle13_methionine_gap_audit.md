# Candidate v1.14 Cycle 13 Methionine Gap Audit

## Hypothesis

The strict nitrogen validation failure is caused by a methionine biosynthesis gap, not by the N2 boundary itself.

## Test

Configured acetate with all nitrogen-containing uptake boundaries closed, then reopened ammonium only. Added temporary demand reactions for methionine-module metabolites and maximized each demand.

## Result

Under strict ammonium-acetate conditions:

- L-methionine (`cpd00060[c0]`) max net production: 0
- homocysteine (`cpd00135[c0]`) max net production: 0
- cystathionine forms (`cpd00424[c0]`, `cpd19019[c0]`) max net production: 0
- cysteine (`cpd00084[c0]`) max net production: 0
- homoserine and activated homoserine precursors are producible
- sulfate is available, but reduced sulfur assimilation to cysteine/H2S/methionine appears blocked under this strict condition

## Mechanistic Clue

The methionine module contains annotated reactions from homoserine to O-acetyl/O-succinyl homoserine and from H2S to homocysteine/methionine. The blocked demand profile points upstream of homocysteine, likely around reduced sulfur supply or cysteine/H2S production rather than carbon skeleton formation.

## Adversarial Decision

Do not patch methionine by opening methionine uptake in the model as a default. Treat external methionine as an experimental medium supplement only when the wet-lab medium includes it. For publication-grade minimal nitrogen-fixing claims, the next curator must resolve sulfur assimilation and methionine biosynthesis with genomic/literature evidence and rerun the strict nitrogen rescue panel.

## Outputs

- `candidate_v1.14/methionine_biosynthesis_audit/methionine_module_demand_capacity.tsv`
- `candidate_v1.14/methionine_biosynthesis_audit/methionine_module_reaction_neighborhood.tsv`
