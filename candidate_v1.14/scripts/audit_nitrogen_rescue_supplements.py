from pathlib import Path

import cobra
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MODELS = {
    "baseline_v1.13": ROOT / "baseline" / "mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml",
    "candidate_n2_boundary": ROOT
    / "candidate_v1.14"
    / "candidate_model_n2_boundary"
    / "mymodel_CGA009_candidate_v1.14_n2_boundary.xml",
}
OUT = ROOT / "candidate_v1.14" / "nitrogen_rescue_audit"

CARBON = ("acetate", "EX_cpd00029_e0", -1.96)
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
GROWTH_TOL = 1e-7


def boundary_like_reactions(model: cobra.Model) -> list[cobra.Reaction]:
    rxns = set(model.exchanges)
    rxns.update(rxn for rxn in model.reactions if len(rxn.metabolites) == 1)
    return sorted(rxns, key=lambda rxn: rxn.id)


def reaction_contains_nitrogen(rxn: cobra.Reaction) -> bool:
    return any(met.elements.get("N", 0) > 0 for met in rxn.metabolites)


def close_carbon_sources(model: cobra.Model) -> None:
    for rid in CARBON_EXCHANGES:
        if rid in model.reactions:
            rxn = model.reactions.get_by_id(rid)
            if rxn.lower_bound < 0:
                rxn.lower_bound = 0.0


def set_carbon(model: cobra.Model) -> None:
    _, exchange, uptake_lb = CARBON
    close_carbon_sources(model)
    rxn = model.reactions.get_by_id(exchange)
    rxn.lower_bound = uptake_lb
    rxn.upper_bound = 0.0


def close_nitrogen_uptake(model: cobra.Model) -> list[dict]:
    closed = []
    for rxn in boundary_like_reactions(model):
        if rxn.lower_bound < 0 and reaction_contains_nitrogen(rxn):
            closed.append(
                {
                    "reaction_id": rxn.id,
                    "name": rxn.name,
                    "original_lower_bound": rxn.lower_bound,
                    "original_upper_bound": rxn.upper_bound,
                    "metabolites": ";".join(sorted(met.id for met in rxn.metabolites)),
                    "formulas": ";".join(sorted(str(met.formula) for met in rxn.metabolites)),
                }
            )
            rxn.lower_bound = 0.0
    return closed


def set_bounds(model: cobra.Model, rid: str, lb: float, ub: float) -> None:
    if rid in model.reactions:
        rxn = model.reactions.get_by_id(rid)
        rxn.lower_bound = lb
        rxn.upper_bound = ub


def solve(model: cobra.Model) -> tuple[str, float]:
    sol = model.optimize()
    return sol.status, sol.objective_value if sol.status == "optimal" else float("nan")


def main() -> int:
    cobra.Configuration().solver = "glpk"
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    closed_rows = []

    for label, path in MODELS.items():
        base = cobra.io.read_sbml_model(str(path))
        base.solver = "glpk"
        set_carbon(base)
        closed = close_nitrogen_uptake(base)
        closed_rows.extend({"model": label, **row} for row in closed)

        with base as model:
            set_bounds(model, "EX_cpd00013_e0", -100.0, 100.0)
            status, objective = solve(model)
            rows.append(
                {
                    "model": label,
                    "test": "ammonium_only",
                    "rescued_reaction": "",
                    "status": status,
                    "objective_value": objective,
                    "growth_positive": objective > GROWTH_TOL if status == "optimal" else False,
                }
            )

        with base as model:
            set_bounds(model, "EX_cpd00013_e0", 0.0, 100.0)
            set_bounds(model, "EX_cpd00528_c0", -100.0, 1000.0)
            status, objective = solve(model)
            rows.append(
                {
                    "model": label,
                    "test": "n2_only_no_ammonium",
                    "rescued_reaction": "EX_cpd00528_c0",
                    "status": status,
                    "objective_value": objective,
                    "growth_positive": objective > GROWTH_TOL if status == "optimal" else False,
                }
            )

        with base as model:
            set_bounds(model, "EX_cpd00013_e0", 0.0, 100.0)
            set_bounds(model, "EX_cpd00528_c0", -100.0, 1000.0)
            set_bounds(model, "EX_cpd00060_e0", -1000.0, 1000.0)
            status, objective = solve(model)
            rows.append(
                {
                    "model": label,
                    "test": "n2_plus_methionine_no_ammonium",
                    "rescued_reaction": "EX_cpd00528_c0;EX_cpd00060_e0",
                    "status": status,
                    "objective_value": objective,
                    "growth_positive": objective > GROWTH_TOL if status == "optimal" else False,
                }
            )

        with base as model:
            set_bounds(model, "EX_cpd00013_e0", 0.0, 100.0)
            set_bounds(model, "EX_cpd00528_c0", -100.0, 1000.0)
            set_bounds(model, "EX_cpd00060_e0", -1000.0, 1000.0)
            if "rxn06874_c0" in model.reactions:
                model.reactions.get_by_id("rxn06874_c0").lower_bound = 0.01
            status, objective = solve(model)
            rows.append(
                {
                    "model": label,
                    "test": "forced_nitrogenase_n2_plus_methionine_no_ammonium",
                    "rescued_reaction": "rxn06874_c0;EX_cpd00528_c0;EX_cpd00060_e0",
                    "status": status,
                    "objective_value": objective,
                    "growth_positive": objective > GROWTH_TOL if status == "optimal" else False,
                }
            )

        for candidate in closed:
            rid = candidate["reaction_id"]
            if rid == "EX_cpd00013_e0":
                continue
            with base as model:
                set_bounds(model, "EX_cpd00013_e0", -100.0, 100.0)
                set_bounds(
                    model,
                    rid,
                    candidate["original_lower_bound"],
                    candidate["original_upper_bound"],
                )
                status, objective = solve(model)
                rows.append(
                    {
                        "model": label,
                        "test": "ammonium_plus_single_original_nitrogen_boundary",
                        "rescued_reaction": rid,
                        "rescued_name": candidate["name"],
                        "status": status,
                        "objective_value": objective,
                        "growth_positive": objective > GROWTH_TOL if status == "optimal" else False,
                    }
                )

        with base as model:
            set_bounds(model, "EX_cpd00013_e0", -100.0, 100.0)
            for candidate in closed:
                if candidate["reaction_id"] != "EX_cpd00013_e0":
                    set_bounds(
                        model,
                        candidate["reaction_id"],
                        candidate["original_lower_bound"],
                        candidate["original_upper_bound"],
                    )
            status, objective = solve(model)
            rows.append(
                {
                    "model": label,
                    "test": "ammonium_plus_all_original_nitrogen_boundaries",
                    "rescued_reaction": "ALL_ORIGINAL_N_BOUNDARIES",
                    "status": status,
                    "objective_value": objective,
                    "growth_positive": objective > GROWTH_TOL if status == "optimal" else False,
                }
            )

    pd.DataFrame(closed_rows).to_csv(OUT / "closed_nitrogen_uptake_boundaries.tsv", sep="\t", index=False)
    pd.DataFrame(rows).to_csv(OUT / "nitrogen_rescue_growth_tests.tsv", sep="\t", index=False)
    print(f"Wrote nitrogen rescue audit to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
