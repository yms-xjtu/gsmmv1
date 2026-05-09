from pathlib import Path

import cobra
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "baseline" / "mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml"
OUT = ROOT / "candidate_v1.14" / "model_reaction_maps"

TARGET_REACTIONS = {
    "H2_exchange": ["EX_cpd11640_e0", "rxn08691_c0", "rxn05759_c0"],
    "nitrogenase": ["rxn06874_c0", "rxn06926_c0", "rxn05893_c0"],
    "CBB_RuBisCO_PRK": ["rxn00018_c0", "rxn01111_c0", "rxn01116_c0"],
    "CO2_exchange": ["EX_cpd00011_e0", "rxn05467_c0"],
    "acetate_condition": ["EX_cpd00029_e0", "rxn05488_c0", "rxn00175_c0", "rxn00225_c0"],
    "succinate_condition": ["EX_cpd00036_e0", "rxn05654_c0", "rxn00285_c0", "rxn00288_c0", "rxn00336_c0"],
    "butyrate_condition": ["EX_cpd00211_e0", "rxn05683_c0", "rxn15455_c0"],
    "fumarate_condition": ["EX_cpd00106_e0", "rxn05561_c0", "rxn00799_c0"],
    "ferredoxin_redox": ["rxn13974_c0", "rxn14048_c0", "rxn05759_c0", "rxn14159_c0", "rxn06874_c0"],
    "PHB": ["rxn15455_c0"],
}


def reaction_row(model: cobra.Model, module: str, rid: str) -> dict:
    if rid not in model.reactions:
        return {
            "module": module,
            "reaction_id": rid,
            "present": False,
            "name": "",
            "lower_bound": "",
            "upper_bound": "",
            "reaction": "",
            "gpr": "",
        }
    rxn = model.reactions.get_by_id(rid)
    return {
        "module": module,
        "reaction_id": rid,
        "present": True,
        "name": rxn.name,
        "lower_bound": rxn.lower_bound,
        "upper_bound": rxn.upper_bound,
        "reaction": rxn.reaction,
        "gpr": rxn.gene_reaction_rule,
    }


def main() -> int:
    cobra.Configuration().solver = "glpk"
    OUT.mkdir(parents=True, exist_ok=True)
    model = cobra.io.read_sbml_model(str(MODEL))
    model.solver = "glpk"

    rows = []
    for module, reaction_ids in TARGET_REACTIONS.items():
        for rid in reaction_ids:
            rows.append(reaction_row(model, module, rid))

    pd.DataFrame(rows).to_csv(OUT / "v1_13_validation_module_reaction_map.tsv", sep="\t", index=False)

    exchange_rows = []
    for rxn in model.exchanges:
        exchange_rows.append(
            {
                "reaction_id": rxn.id,
                "name": rxn.name,
                "lower_bound": rxn.lower_bound,
                "upper_bound": rxn.upper_bound,
                "reaction": rxn.reaction,
            }
        )
    pd.DataFrame(exchange_rows).sort_values("reaction_id").to_csv(
        OUT / "v1_13_exchange_bounds.tsv", sep="\t", index=False
    )
    print(f"Wrote module maps to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
