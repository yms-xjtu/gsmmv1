# Candidate v1.14 Cycle 12 MEMOTE And Strict Nitrogen Validation

## Hypothesis

The candidate N2-boundary model should not regress global MEMOTE quality relative to v1.13, and it should improve nitrogen-fixing condition feasibility only when N2 is explicitly available.

## Tests Run

1. MEMOTE snapshot for frozen v1.13.
2. MEMOTE snapshot for candidate v1.14 N2-boundary model.
3. Parsed MEMOTE HTML into reproducible TSV comparison tables.
4. Reran nitrogen/H2 tradeoff under stricter nitrogen boundary logic.
5. Audited nitrogen rescue supplements after closing all original nitrogen-containing uptake boundaries.

## MEMOTE Result

Both models have the same status-count profile:

- 139 failed tests
- 114 passed tests
- 10 skipped tests

Total score is nearly unchanged:

- v1.13: 0.3721140138609879
- candidate N2 boundary: 0.3721009059825648

Interpretation: the N2-boundary candidate does not introduce a new MEMOTE pass/fail regression. The tiny score change is denominator/metric drift from adding one boundary reaction. However, absolute MEMOTE quality remains far below publication-ready because annotation, biomass, stoichiometric consistency, energy-cycle, SBO, and GPR tests still fail.

## Strict Nitrogen Result

The previous nitrogen test was too permissive because it only closed ammonium and left other nitrogen-containing exchanges open. The corrected script now closes all nitrogen uptake boundaries before selectively reopening ammonium or N2.

Closed original nitrogen-containing uptake boundaries:

- `EX_cpd00013_e0` ammonium
- `EX_cpd00039_e0` lysine
- `EX_cpd00041_e0` aspartate
- `EX_cpd00053_e0` glutamine
- `EX_cpd00060_e0` methionine
- `EX_cpd00104_e0` biotin
- `EX_cpd03424_e0` vitamin B12

Key observations:

- ammonium-only acetate growth is zero in both v1.13 and the candidate.
- reopening methionine plus ammonium partially rescues growth in both models.
- restoring all original nitrogen-containing uptake boundaries restores full baseline growth.
- v1.13 cannot grow under forced nitrogenase with N2 plus methionine.
- candidate v1.14 can grow under N2 plus methionine with forced nitrogenase.

## Adversarial Interpretation

The N2 boundary candidate solves only one real problem: missing N2 supply for nitrogenase. It does not by itself make the model a publishable nitrogen-fixing growth model.

The stronger adversarial finding is that the current model appears dependent on external methionine or a related missing methionine biosynthesis route under strict inorganic nitrogen media. This must be resolved or explicitly tied to the experimental medium before claiming growth-experiment validation under minimal nitrogen-fixing conditions.

## Decision

Keep candidate v1.14 N2 boundary as a defensible low-risk edit, but do not accept v1.14 as publication-ready. The next cycle must audit methionine biosynthesis, sulfur metabolism, and biomass amino-acid precursor feasibility before any stronger claim about nitrogen-fixing growth is made.

## Reproducible Outputs

- `candidate_v1.14/memote_baseline_v1_13/memote_baseline_v1_13.html`
- `candidate_v1.14/memote_candidate_n2_boundary/memote_candidate_n2_boundary.html`
- `candidate_v1.14/memote_comparison/baseline_vs_candidate_memote_scores.tsv`
- `candidate_v1.14/memote_comparison/baseline_vs_candidate_memote_status_counts.tsv`
- `candidate_v1.14/memote_comparison/baseline_vs_candidate_memote_changed_tests.tsv`
- `candidate_v1.14/nitrogen_h2_tradeoff/nitrogen_regime_growth_h2_summary.tsv`
- `candidate_v1.14/nitrogen_rescue_audit/closed_nitrogen_uptake_boundaries.tsv`
- `candidate_v1.14/nitrogen_rescue_audit/nitrogen_rescue_growth_tests.tsv`
