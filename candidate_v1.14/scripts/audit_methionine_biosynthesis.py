from pathlib import Path

import cobra
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "baseline" / "mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml"
OUT = ROOT / "candidate_v1.14" / "methionine_biosynthesis_audit"

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
METHIONINE_MODULE_METABOLITES = [
    "cpd00060[c0]",
    "cpd00135[c0]",
    "cpd00424[c0]",
    "cpd19019[c0]",
    "cpd00790[c0]",
    "cpd00822[c0]",
    "cpd00227[c0]",
    "cpd00084[c0]",
    "cpd00048[c0]",
]


def boundary_like_reactions(model: cobra.Model) -> list[cobra.Reaction]:
    rxns = set(model.exchanges)
    rxns.update(rxn for rxn in model.reactions if len(rxn.metabolites) == 1)
    return sorted(rxns, key=lambda rxn: rxn.id)


def configure_strict_ammonium_acetate(model: cobra.Model) -> None:
    for rid in CARBON_EXCHANGES:
        if rid in model.reactions and model.reactions.get_by_id(rid).lower_bound < 0:
            model.reactions.get_by_id(rid).lower_bound = 0.0
    acetate = model.reactions.get_by_id("EX_cpd00029_e0")
    acetate.lower_bound = -1.96
    acetate.upper_bound = 0.0
    for rxn in boundary_like_reactions(model):
        if rxn.lower_bound < 0 and any(met.elements.get("N", 0) > 0 for met in rxn.metabolites):
            rxn.lower_bound = 0.0
    nh3 = model.reactions.get_by_id("EX_cpd00013_e0")
    nh3.lower_bound = -100.0
    nh3.upper_bound = 100.0


def demand_capacity(model: cobra.Model, met_id: str) -> tuple[str, float]:
    with model:
        met = model.metabolites.get_by_id(met_id)
        demand = cobra.Reaction(f"DM_audit_{met_id.replace('[', '_').replace(']', '')}")
        demand.add_metabolites({met: -1.0})
        demand.lower_bound = 0.0
        demand.upper_bound = 1000.0
        model.add_reactions([demand])
        model.objective = demand
        sol = model.optimize()
        return sol.status, sol.objective_value if sol.status == "optimal" else float("nan")


def main() -> int:
    cobra.Configuration().solver = "glpk"
    OUT.mkdir(parents=True, exist_ok=True)
    model = cobra.io.read_sbml_model(str(MODEL))
    model.solver = "glpk"
    configure_strict_ammonium_acetate(model)

    demand_rows = []
    for met_id in METHIONINE_MODULE_METABOLITES:
        status, objective = demand_capacity(model, met_id)
        met = model.metabolites.get_by_id(met_id)
        demand_rows.append(
            {
                "metabolite_id": met.id,
                "name": met.name,
                "formula": met.formula,
                "demand_status": status,
                "max_net_production_under_strict_ammonium_acetate": objective,
            }
        )

    reaction_rows = []
    seen = set()
    for met_id in METHIONINE_MODULE_METABOLITES:
        met = model.metabolites.get_by_id(met_id)
        for rxn in sorted(met.reactions, key=lambda item: item.id):
            key = (met_id, rxn.id)
            if key in seen:
                continue
            seen.add(key)
            reaction_rows.append(
                {
                    "anchor_metabolite_id": met_id,
                    "anchor_metabolite_name": met.name,
                    "reaction_id": rxn.id,
                    "reaction_name": rxn.name,
                    "lower_bound": rxn.lower_bound,
                    "upper_bound": rxn.upper_bound,
                    "gpr": rxn.gene_reaction_rule,
                    "reaction": rxn.reaction,
                }
            )

    pd.DataFrame(demand_rows).to_csv(OUT / "methionine_module_demand_capacity.tsv", sep="\t", index=False)
    pd.DataFrame(reaction_rows).to_csv(OUT / "methionine_module_reaction_neighborhood.tsv", sep="\t", index=False)
    print(f"Wrote methionine biosynthesis audit to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
