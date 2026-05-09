from pathlib import Path

import cobra
import pandas as pd
from cobra.flux_analysis import flux_variability_analysis


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "baseline" / "mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml"
OUT = ROOT / "candidate_v1.14" / "nitrogen_h2_tradeoff"

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


def switch_carbon(model: cobra.Model, exchange: str, uptake_lb: float) -> None:
    for rid in CARBON_EXCHANGES:
        if rid in model.reactions:
            rxn = model.reactions.get_by_id(rid)
            if rxn.lower_bound < 0:
                rxn.lower_bound = 0.0
    rxn = model.reactions.get_by_id(exchange)
    rxn.lower_bound = uptake_lb
    rxn.upper_bound = 0.0


def set_nitrogen_regime(model: cobra.Model, regime: str) -> None:
    if "EX_cpd00013_e0" in model.reactions:
        nh3 = model.reactions.get_by_id("EX_cpd00013_e0")
        if regime == "ammonium_open":
            nh3.lower_bound = -100.0
            nh3.upper_bound = 100.0
        elif regime == "ammonium_closed":
            nh3.lower_bound = 0.0
            nh3.upper_bound = 100.0
    if "rxn06874_c0" in model.reactions:
        nif = model.reactions.get_by_id("rxn06874_c0")
        if regime == "nitrogenase_forced_min":
            nif.lower_bound = 0.01


def main() -> int:
    cobra.Configuration().solver = "glpk"
    OUT.mkdir(parents=True, exist_ok=True)
    base = cobra.io.read_sbml_model(str(MODEL))
    base.solver = "glpk"

    rows = []
    fva_rows = []
    regimes = ["ammonium_open", "ammonium_closed", "nitrogenase_forced_min"]
    for carbon_name, (exchange, uptake_lb) in CARBON_CONDITIONS.items():
        for regime in regimes:
            with base as model:
                model.solver = "glpk"
                switch_carbon(model, exchange, uptake_lb)
                set_nitrogen_regime(model, regime)
                sol = model.optimize()
                rows.append(
                    {
                        "carbon": carbon_name,
                        "exchange": exchange,
                        "uptake_lb": uptake_lb,
                        "nitrogen_regime": regime,
                        "status": sol.status,
                        "objective_value": sol.objective_value,
                        "h2_flux": sol.fluxes.get("EX_cpd11640_e0") if sol.status == "optimal" else "",
                        "nitrogenase_flux": sol.fluxes.get("rxn06874_c0") if sol.status == "optimal" else "",
                    }
                )
                if sol.status == "optimal":
                    readouts = [rid for rid in READOUTS if rid in model.reactions]
                    try:
                        fva = flux_variability_analysis(model, reaction_list=readouts, fraction_of_optimum=0.9)
                        for rid, row in fva.iterrows():
                            fva_rows.append(
                                {
                                    "carbon": carbon_name,
                                    "nitrogen_regime": regime,
                                    "reaction_id": rid,
                                    "minimum": row["minimum"],
                                    "maximum": row["maximum"],
                                    "fraction_of_optimum": 0.9,
                                }
                            )
                    except Exception as exc:
                        fva_rows.append(
                            {
                                "carbon": carbon_name,
                                "nitrogen_regime": regime,
                                "reaction_id": "FVA_ERROR",
                                "minimum": "",
                                "maximum": "",
                                "fraction_of_optimum": 0.9,
                                "error": repr(exc),
                            }
                        )

    pd.DataFrame(rows).to_csv(OUT / "nitrogen_regime_growth_h2_summary.tsv", sep="\t", index=False)
    pd.DataFrame(fva_rows).to_csv(OUT / "nitrogen_regime_readout_fva.tsv", sep="\t", index=False)
    print(f"Wrote nitrogen/H2 tradeoff outputs to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
