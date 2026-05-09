from pathlib import Path

import cobra
import pandas as pd
from cobra import Metabolite, Reaction
from cobra.flux_analysis import flux_variability_analysis


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "baseline" / "mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml"
OUT = ROOT / "candidate_v1.14" / "hypothetical_n2_boundary"

CARBON_CONDITIONS = {
    "acetate": ("EX_cpd00029_e0", -1.96),
    "succinate": ("EX_cpd00036_e0", -4.66),
    "butyrate": ("EX_cpd00211_e0", -3.69),
    "fumarate": ("EX_cpd00106_e0", -4.66),
}

CARBON_EXCHANGES = [
    "EX_cpd00029_e0",
    "EX_cpd00036_e0",
    "EX_cpd00211_e0",
    "EX_cpd00106_e0",
    "EX_cpd00130_e0",
    "EX_cpd00604_e0",
    "EX_cpd00153_e0",
    "EX_cpd00136_e0",
]

READOUTS = ["bio1", "EX_cpd11640_e0", "rxn06874_c0", "rxn05759_c0", "rxn00018_c0", "rxn01111_c0"]


def add_hypothetical_n2_exchange(model: cobra.Model) -> None:
    met = model.metabolites.get_by_id("cpd00528[c0]")
    rxn = Reaction("HYP_EX_cpd00528_c0")
    rxn.name = "Hypothetical N2 supply boundary for diagnostic only"
    rxn.lower_bound = -1000.0
    rxn.upper_bound = 1000.0
    rxn.add_metabolites({met: -1.0})
    model.add_reactions([rxn])


def switch_carbon(model: cobra.Model, exchange: str, uptake_lb: float) -> None:
    for rid in CARBON_EXCHANGES:
        if rid in model.reactions:
            rxn = model.reactions.get_by_id(rid)
            if rxn.lower_bound < 0:
                rxn.lower_bound = 0.0
    rxn = model.reactions.get_by_id(exchange)
    rxn.lower_bound = uptake_lb
    rxn.upper_bound = 0.0


def main() -> int:
    cobra.Configuration().solver = "glpk"
    OUT.mkdir(parents=True, exist_ok=True)
    base = cobra.io.read_sbml_model(str(MODEL))
    base.solver = "glpk"

    rows = []
    fva_rows = []
    for carbon, (exchange, uptake_lb) in CARBON_CONDITIONS.items():
        for n2_boundary in [False, True]:
            with base as model:
                model.solver = "glpk"
                switch_carbon(model, exchange, uptake_lb)
                if "EX_cpd00013_e0" in model.reactions:
                    model.reactions.get_by_id("EX_cpd00013_e0").lower_bound = 0.0
                if n2_boundary:
                    add_hypothetical_n2_exchange(model)
                if "rxn06874_c0" in model.reactions:
                    model.reactions.get_by_id("rxn06874_c0").lower_bound = 0.01
                sol = model.optimize()
                rows.append(
                    {
                        "carbon": carbon,
                        "n2_boundary": n2_boundary,
                        "nitrogenase_min": 0.01,
                        "status": sol.status,
                        "objective_value": sol.objective_value,
                        "h2_flux": sol.fluxes.get("EX_cpd11640_e0") if sol.status == "optimal" else "",
                        "nitrogenase_flux": sol.fluxes.get("rxn06874_c0") if sol.status == "optimal" else "",
                        "n2_boundary_flux": sol.fluxes.get("HYP_EX_cpd00528_c0") if sol.status == "optimal" and n2_boundary else "",
                    }
                )
                if sol.status == "optimal":
                    fva = flux_variability_analysis(
                        model,
                        reaction_list=[rid for rid in READOUTS if rid in model.reactions],
                        fraction_of_optimum=0.9,
                    )
                    for rid, row in fva.iterrows():
                        fva_rows.append(
                            {
                                "carbon": carbon,
                                "n2_boundary": n2_boundary,
                                "reaction_id": rid,
                                "minimum": row["minimum"],
                                "maximum": row["maximum"],
                                "fraction_of_optimum": 0.9,
                            }
                        )

    pd.DataFrame(rows).to_csv(OUT / "hypothetical_n2_boundary_summary.tsv", sep="\t", index=False)
    pd.DataFrame(fva_rows).to_csv(OUT / "hypothetical_n2_boundary_fva.tsv", sep="\t", index=False)
    print(f"Wrote hypothetical N2 boundary test to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
