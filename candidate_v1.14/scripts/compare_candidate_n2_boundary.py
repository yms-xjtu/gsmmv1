from pathlib import Path

import cobra
import pandas as pd
from cobra.flux_analysis import flux_variability_analysis


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "baseline" / "mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml"
CANDIDATE = ROOT / "candidate_v1.14" / "candidate_model_n2_boundary" / "mymodel_CGA009_candidate_v1.14_n2_boundary.xml"
OUT = ROOT / "candidate_v1.14" / "candidate_model_n2_boundary_comparison"

CARBON_CONDITIONS = {
    "baseline_unchanged": (None, None),
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


def switch_carbon(model, exchange, uptake_lb):
    if exchange is None:
        return
    for rid in CARBON_EXCHANGES:
        if rid in model.reactions:
            rxn = model.reactions.get_by_id(rid)
            if rxn.lower_bound < 0:
                rxn.lower_bound = 0.0
    rxn = model.reactions.get_by_id(exchange)
    rxn.lower_bound = uptake_lb
    rxn.upper_bound = 0.0


def run_model(model_path: Path, label: str):
    model = cobra.io.read_sbml_model(str(model_path))
    model.solver = "glpk"
    rows = []
    fva_rows = []
    for condition, (exchange, uptake_lb) in CARBON_CONDITIONS.items():
        with model:
            model.solver = "glpk"
            switch_carbon(model, exchange, uptake_lb)
            sol = model.optimize()
            rows.append(
                {
                    "model": label,
                    "condition": condition,
                    "status": sol.status,
                    "objective_value": sol.objective_value,
                    "n2_exchange_present": "EX_cpd00528_c0" in model.reactions,
                    "n2_default_lb": model.reactions.get_by_id("EX_cpd00528_c0").lower_bound if "EX_cpd00528_c0" in model.reactions else "",
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
                            "model": label,
                            "condition": condition,
                            "reaction_id": rid,
                            "minimum": row["minimum"],
                            "maximum": row["maximum"],
                            "fraction_of_optimum": 0.9,
                        }
                    )
    return rows, fva_rows


def main() -> int:
    cobra.Configuration().solver = "glpk"
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    fva_rows = []
    for path, label in [(BASELINE, "baseline_v1.13"), (CANDIDATE, "candidate_n2_closed")]:
        r, f = run_model(path, label)
        rows.extend(r)
        fva_rows.extend(f)
    pd.DataFrame(rows).to_csv(OUT / "baseline_vs_candidate_growth.tsv", sep="\t", index=False)
    pd.DataFrame(fva_rows).to_csv(OUT / "baseline_vs_candidate_fva.tsv", sep="\t", index=False)
    print(f"Wrote comparison outputs to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
