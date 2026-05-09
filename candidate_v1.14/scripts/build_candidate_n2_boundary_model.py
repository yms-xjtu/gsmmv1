from pathlib import Path

import cobra
from cobra import Reaction


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "baseline" / "mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml"
OUT = ROOT / "candidate_v1.14" / "candidate_model_n2_boundary"


def main() -> int:
    cobra.Configuration().solver = "glpk"
    OUT.mkdir(parents=True, exist_ok=True)
    model = cobra.io.read_sbml_model(str(MODEL))
    model.solver = "glpk"

    if "EX_cpd00528_c0" not in model.reactions:
        n2 = model.metabolites.get_by_id("cpd00528[c0]")
        rxn = Reaction("EX_cpd00528_c0")
        rxn.name = "Exchange for N2_c0 candidate boundary"
        rxn.lower_bound = 0.0
        rxn.upper_bound = 1000.0
        rxn.add_metabolites({n2: -1.0})
        model.add_reactions([rxn])

    cobra.io.write_sbml_model(model, str(OUT / "mymodel_CGA009_candidate_v1.14_n2_boundary.xml"))
    cobra.io.save_json_model(model, str(OUT / "mymodel_CGA009_candidate_v1.14_n2_boundary.json"))
    with open(OUT / "candidate_n2_boundary_audit.tsv", "w", encoding="utf-8") as handle:
        handle.write("reaction_id\tname\tlower_bound\tupper_bound\treaction\tnote\n")
        rxn = model.reactions.get_by_id("EX_cpd00528_c0")
        handle.write(
            f"{rxn.id}\t{rxn.name}\t{rxn.lower_bound}\t{rxn.upper_bound}\t{rxn.reaction}\t"
            "Candidate N2 boundary added closed for uptake by default; condition scripts may set lower_bound < 0 only for nitrogen-fixing scenarios.\n"
        )
    print(f"Wrote candidate N2 boundary model to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
