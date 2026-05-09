from pathlib import Path

import cobra
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MODELS = {
    "baseline_v1.13": ROOT / "baseline" / "mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml",
    "candidate_n2_boundary": ROOT / "candidate_v1.14" / "candidate_model_n2_boundary" / "mymodel_CGA009_candidate_v1.14_n2_boundary.xml",
}
OUT = ROOT / "candidate_v1.14" / "candidate_n2_cobra_qc"


def classify_reaction(rxn: cobra.Reaction) -> str:
    if rxn.id.startswith("EX_") or len(rxn.metabolites) == 1:
        return "boundary_or_single_metabolite"
    if rxn.id.startswith("bio") or "biomass" in rxn.id.lower() or "biomass" in (rxn.name or "").lower():
        return "biomass_or_pseudo"
    return "internal_checkable"


def model_qc(path: Path, label: str):
    model = cobra.io.read_sbml_model(str(path))
    model.solver = "glpk"
    summary = {
        "model": label,
        "reaction_count": len(model.reactions),
        "metabolite_count": len(model.metabolites),
        "gene_count": len(model.genes),
        "missing_formula_metabolites": sum(1 for met in model.metabolites if not met.formula),
        "missing_charge_metabolites": sum(1 for met in model.metabolites if met.charge is None),
    }
    sol = model.optimize()
    summary["fba_status"] = sol.status
    summary["fba_objective"] = sol.objective_value

    imbalance_rows = []
    for rxn in model.reactions:
        scope = classify_reaction(rxn)
        if scope != "internal_checkable":
            continue
        imbalance = rxn.check_mass_balance()
        if imbalance:
            imbalance_rows.append(
                {
                    "model": label,
                    "reaction_id": rxn.id,
                    "name": rxn.name,
                    "scope": scope,
                    "imbalance": repr(imbalance),
                    "reaction": rxn.reaction,
                }
            )
    summary["imbalanced_internal_checkable_reactions"] = len(imbalance_rows)
    return summary, imbalance_rows


def main() -> int:
    cobra.Configuration().solver = "glpk"
    OUT.mkdir(parents=True, exist_ok=True)
    summaries = []
    imbalances = []
    for label, path in MODELS.items():
        summary, rows = model_qc(path, label)
        summaries.append(summary)
        imbalances.extend(rows)
    pd.DataFrame(summaries).to_csv(OUT / "baseline_vs_candidate_cobra_qc_summary.tsv", sep="\t", index=False)
    pd.DataFrame(imbalances).to_csv(OUT / "baseline_vs_candidate_internal_imbalances.tsv", sep="\t", index=False)
    print(f"Wrote candidate N2 COBRA QC to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
