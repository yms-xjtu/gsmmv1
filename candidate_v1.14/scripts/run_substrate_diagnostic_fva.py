from pathlib import Path

import cobra
import pandas as pd
from cobra.flux_analysis import flux_variability_analysis, pfba


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "baseline" / "mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml"
OUT = ROOT / "candidate_v1.14" / "substrate_diagnostic_fva"

CONDITIONS = {
    "acetate_baseline_bound": {"exchange": "EX_cpd00029_e0", "uptake_lb": -1.96},
    "succinate_me_uptake": {"exchange": "EX_cpd00036_e0", "uptake_lb": -4.66},
    "butyrate_me_uptake": {"exchange": "EX_cpd00211_e0", "uptake_lb": -3.69},
    "fumarate_h2_panel": {"exchange": "EX_cpd00106_e0", "uptake_lb": -4.66},
}

ESSENTIAL_OPEN = {
    "EX_cpd00001_e0": (-100.0, 100.0),  # H2O
    "EX_cpd00009_e0": (-100.0, 1000.0),  # phosphate
    "EX_cpd00013_e0": (-100.0, 100.0),  # ammonia
    "EX_cpd00048_e0": (-100.0, 100.0),  # sulfate
    "EX_cpd00067_e0": (-100.0, 100.0),  # proton
    "EX_cpd00254_e0": (-10.0, 1000.0),  # Mg
    "EX_cpd10515_e0": (-20.0, 0.0),  # Fe2+
    "EX_cpd10516_e0": (-20.0, 0.0),  # Fe3+
    "EX_cpd11574_e0": (-100.0, 100.0),  # molybdate
    "EX_cpd11632_e0": (-36.6, 0.0),  # photon
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


def close_carbon_uptake(model: cobra.Model) -> None:
    for rxn in model.exchanges:
        if rxn.id not in ESSENTIAL_OPEN:
            if rxn.lower_bound < 0:
                rxn.lower_bound = 0.0


def apply_condition(model: cobra.Model, exchange: str, uptake_lb: float) -> None:
    close_carbon_uptake(model)
    for rid, (lb, ub) in ESSENTIAL_OPEN.items():
        if rid in model.reactions:
            rxn = model.reactions.get_by_id(rid)
            rxn.lower_bound = lb
            rxn.upper_bound = ub
    model.reactions.get_by_id(exchange).lower_bound = uptake_lb
    model.reactions.get_by_id(exchange).upper_bound = 0.0


def flux_or_none(solution, rid: str):
    try:
        return solution.fluxes.get(rid, None)
    except Exception:
        return None


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
                    "note": "diagnostic condition; not a hard literature reproduction",
                }
            )

            if sol.status == "optimal":
                try:
                    pfba_sol = pfba(model)
                    solution_for_flux = pfba_sol
                    solution_type = "pfba"
                except Exception:
                    solution_for_flux = sol
                    solution_type = "fba"
                for rid in READOUT_REACTIONS:
                    if rid in model.reactions:
                        flux_rows.append(
                            {
                                "condition": condition,
                                "solution_type": solution_type,
                                "reaction_id": rid,
                                "flux": flux_or_none(solution_for_flux, rid),
                            }
                        )
                present_readouts = [rid for rid in READOUT_REACTIONS if rid in model.reactions]
                try:
                    fva = flux_variability_analysis(model, reaction_list=present_readouts, fraction_of_optimum=0.9)
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
                except Exception as exc:
                    fva_rows.append(
                        {
                            "condition": condition,
                            "reaction_id": "FVA_ERROR",
                            "minimum": "",
                            "maximum": "",
                            "fraction_of_optimum": 0.9,
                            "error": repr(exc),
                        }
                    )

    pd.DataFrame(summary_rows).to_csv(OUT / "condition_growth_summary.tsv", sep="\t", index=False)
    pd.DataFrame(flux_rows).to_csv(OUT / "pfba_readout_fluxes.tsv", sep="\t", index=False)
    pd.DataFrame(fva_rows).to_csv(OUT / "readout_fva.tsv", sep="\t", index=False)
    print(f"Wrote diagnostic outputs to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
