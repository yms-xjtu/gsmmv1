from pathlib import Path

import cobra
import pandas as pd
from cobra.flux_analysis import flux_variability_analysis, pfba


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "baseline" / "mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml"
OUT = ROOT / "candidate_v1.14" / "baseline_medium_carbon_switch"

CARBON_EXCHANGES = {
    "acetate": "EX_cpd00029_e0",
    "succinate": "EX_cpd00036_e0",
    "butyrate": "EX_cpd00211_e0",
    "fumarate": "EX_cpd00106_e0",
    "malate": "EX_cpd00130_e0",
    "4_coumarate": "EX_cpd00604_e0",
    "benzoate": "EX_cpd00153_e0",
    "4_hydroxybenzoate": "EX_cpd00136_e0",
}

CONDITIONS = {
    "baseline_unchanged": {"exchange": None, "uptake_lb": None},
    "acetate_current": {"exchange": "EX_cpd00029_e0", "uptake_lb": -1.96},
    "succinate_me": {"exchange": "EX_cpd00036_e0", "uptake_lb": -4.66},
    "butyrate_me": {"exchange": "EX_cpd00211_e0", "uptake_lb": -3.69},
    "fumarate_panel": {"exchange": "EX_cpd00106_e0", "uptake_lb": -4.66},
}

READOUT_REACTIONS = [
    "bio1",
    "EX_cpd11640_e0",
    "EX_cpd00011_e0",
    "rxn06874_c0",
    "rxn00018_c0",
    "rxn01111_c0",
    "rxn05759_c0",
    "rxn15455_c0",
]


def close_known_carbon_sources(model: cobra.Model) -> None:
    for rid in CARBON_EXCHANGES.values():
        if rid in model.reactions:
            rxn = model.reactions.get_by_id(rid)
            if rxn.lower_bound < 0:
                rxn.lower_bound = 0.0


def apply_condition(model: cobra.Model, exchange: str | None, uptake_lb: float | None) -> None:
    if exchange is None:
        return
    close_known_carbon_sources(model)
    rxn = model.reactions.get_by_id(exchange)
    rxn.lower_bound = uptake_lb
    rxn.upper_bound = 0.0


def main() -> int:
    cobra.Configuration().solver = "glpk"
    OUT.mkdir(parents=True, exist_ok=True)
    base_model = cobra.io.read_sbml_model(str(MODEL))
    base_model.solver = "glpk"

    summary_rows = []
    flux_rows = []
    fva_rows = []

    for condition, cfg in CONDITIONS.items():
        with base_model as model:
            model.solver = "glpk"
            apply_condition(model, cfg["exchange"], cfg["uptake_lb"])
            sol = model.optimize()
            summary_rows.append(
                {
                    "condition": condition,
                    "exchange": cfg["exchange"],
                    "uptake_lb": cfg["uptake_lb"],
                    "status": sol.status,
                    "objective_value": sol.objective_value,
                    "note": "baseline exchange bounds preserved except known carbon-source switch",
                }
            )
            if sol.status != "optimal":
                continue
            try:
                psol = pfba(model)
                solution = psol
                solution_type = "pfba"
            except Exception:
                solution = sol
                solution_type = "fba"
            for rid in READOUT_REACTIONS:
                if rid in model.reactions:
                    flux_rows.append(
                        {
                            "condition": condition,
                            "solution_type": solution_type,
                            "reaction_id": rid,
                            "flux": solution.fluxes.get(rid),
                        }
                    )
            readouts = [rid for rid in READOUT_REACTIONS if rid in model.reactions]
            fva = flux_variability_analysis(model, reaction_list=readouts, fraction_of_optimum=0.9)
            for rid, row in fva.iterrows():
                fva_rows.append(
                    {
                        "condition": condition,
                        "reaction_id": rid,
                        "minimum": row["minimum"],
                        "maximum": row["maximum"],
                        "fraction_of_optimum": 0.9,
                    }
                )

    pd.DataFrame(summary_rows).to_csv(OUT / "condition_growth_summary.tsv", sep="\t", index=False)
    pd.DataFrame(flux_rows).to_csv(OUT / "pfba_readout_fluxes.tsv", sep="\t", index=False)
    pd.DataFrame(fva_rows).to_csv(OUT / "readout_fva.tsv", sep="\t", index=False)
    print(f"Wrote baseline-medium carbon switch outputs to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
