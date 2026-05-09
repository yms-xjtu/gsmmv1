from pathlib import Path

import cobra
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "baseline" / "mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml"
OUT = ROOT / "candidate_v1.14" / "nitrogen_boundary_audit"

NITROGEN_TERMS = [
    "nitrogen",
    "nitrate",
    "nitrite",
    "ammonia",
    "ammonium",
    "dinitrogen",
    "urea",
    "glutamine",
    "glutamate",
    "cpd00528",
    "cpd00013",
    "cpd00209",
    "cpd00053",
    "cpd00023",
]


def main() -> int:
    cobra.Configuration().solver = "glpk"
    OUT.mkdir(parents=True, exist_ok=True)
    model = cobra.io.read_sbml_model(str(MODEL))
    model.solver = "glpk"

    rxn_rows = []
    for rxn in model.reactions:
        text = " ".join([rxn.id, rxn.name or "", rxn.reaction, rxn.gene_reaction_rule or ""]).lower()
        if any(term in text for term in NITROGEN_TERMS):
            rxn_rows.append(
                {
                    "reaction_id": rxn.id,
                    "name": rxn.name,
                    "lower_bound": rxn.lower_bound,
                    "upper_bound": rxn.upper_bound,
                    "reaction": rxn.reaction,
                    "gpr": rxn.gene_reaction_rule,
                    "is_exchange": rxn in model.exchanges,
                }
            )

    met_rows = []
    for met in model.metabolites:
        text = " ".join([met.id, met.name or "", met.formula or ""]).lower()
        if any(term in text for term in NITROGEN_TERMS):
            met_rows.append(
                {
                    "metabolite_id": met.id,
                    "name": met.name,
                    "formula": met.formula,
                    "charge": met.charge,
                    "reaction_count": len(met.reactions),
                    "reactions": ";".join(sorted(r.id for r in met.reactions)),
                }
            )

    pd.DataFrame(rxn_rows).sort_values(["is_exchange", "reaction_id"]).to_csv(
        OUT / "nitrogen_related_reactions.tsv", sep="\t", index=False
    )
    pd.DataFrame(met_rows).sort_values("metabolite_id").to_csv(
        OUT / "nitrogen_related_metabolites.tsv", sep="\t", index=False
    )

    n2_exchange_present = any(
        ("cpd00528" in rxn.reaction or "dinitrogen" in (rxn.name or "").lower()) and rxn in model.exchanges
        for rxn in model.reactions
    )
    pd.DataFrame(
        [
            {
                "check": "n2_exchange_present",
                "value": n2_exchange_present,
                "interpretation": "If false, nitrogen-fixing/H2 validation requires a curated N2 supply boundary before forcing nitrogenase.",
            }
        ]
    ).to_csv(OUT / "nitrogen_boundary_summary.tsv", sep="\t", index=False)

    print(f"Wrote nitrogen boundary audit to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
