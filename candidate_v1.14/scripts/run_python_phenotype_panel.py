from pathlib import Path

import cobra
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MODELS = {
    "baseline_v1.13": ROOT / "baseline" / "mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml",
    "candidate_n2_boundary": ROOT / "candidate_v1.14" / "candidate_model_n2_boundary" / "mymodel_CGA009_candidate_v1.14_n2_boundary.xml",
}
OUT = ROOT / "candidate_v1.14" / "python_phenotype_panel"

POSITIVE = [
    ("acetate", "EX_cpd00029_e0", "cpd00029", "Acetate"),
    ("succinate", "EX_cpd00036_e0", "cpd00036", "Succinate"),
    ("malate", "EX_cpd00130_e0", "cpd00130", "L-Malate"),
    ("butyrate", "EX_cpd00211_e0", "cpd00211", "Butyrate"),
    ("p_coumarate", "EX_cpd00604_e0", "cpd00604", "4-Coumarate"),
]
NEGATIVE = [
    ("glucose", "EX_cpd00027_e0", "cpd00027", "D-Glucose"),
    ("xylose", "EX_cpd00154_e0", "cpd00154", "D-Xylose"),
    ("fructose", "EX_cpd00082_e0", "cpd00082", "D-Fructose"),
]
SCENARIOS = [
    ("photoanaerobic_CO2_open", -1000.0),
    ("photoanaerobic_CO2_closed", 0.0),
]
DEFAULT_CARBON_UPTAKE = 10.0
GROWTH_TOL = 1e-7

ESSENTIAL_EXCHANGES = {
    "EX_cpd00001_e0": (-1000.0, 1000.0),
    "EX_cpd00009_e0": (-1000.0, 1000.0),
    "EX_cpd00013_e0": (-1000.0, 1000.0),
    "EX_cpd00030_e0": (-1000.0, 1000.0),
    "EX_cpd00034_e0": (-1000.0, 1000.0),
    "EX_cpd00048_e0": (-1000.0, 1000.0),
    "EX_cpd00058_e0": (-1000.0, 1000.0),
    "EX_cpd00063_e0": (-1000.0, 1000.0),
    "EX_cpd00067_e0": (-1000.0, 1000.0),
    "EX_cpd00099_e0": (-1000.0, 1000.0),
    "EX_cpd00104_e0": (-1000.0, 1000.0),
    "EX_cpd00149_e0": (-1000.0, 1000.0),
    "EX_cpd00205_e0": (-1000.0, 1000.0),
    "EX_cpd00254_e0": (-1000.0, 1000.0),
    "EX_cpd00305_e0": (-1000.0, 1000.0),
    "EX_cpd00971_e0": (-1000.0, 1000.0),
    "EX_cpd03424_e0": (-1000.0, 1000.0),
    "EX_cpd10515_e0": (-1000.0, 1000.0),
    "EX_cpd10516_e0": (-1000.0, 1000.0),
    "EX_cpd11574_e0": (-1000.0, 1000.0),
    "EX_cpd11640_e0": (0.0, 1000.0),
    "EX_cpd00268_e0": (-1000.0, 1000.0),
}


def set_bounds(model, rid, lb, ub):
    if rid in model.reactions:
        rxn = model.reactions.get_by_id(rid)
        rxn.lower_bound = lb
        rxn.upper_bound = ub


def build_photoanaerobic_base(model, co2_lb):
    for rxn in model.exchanges:
        rxn.lower_bound = 0.0
        rxn.upper_bound = max(0.0, rxn.upper_bound)
    for rid, (lb, ub) in ESSENTIAL_EXCHANGES.items():
        set_bounds(model, rid, lb, ub)
    set_bounds(model, "EX_cpd11632_e0", -36.6, 0.0)
    set_bounds(model, "EX_cpd00007_e0", 0.0, 0.0)
    set_bounds(model, "EX_cpd00011_e0", co2_lb, 1000.0)
    return model


def close_substrate_set(model):
    for _, ex, _, _ in POSITIVE + NEGATIVE:
        if ex in model.reactions:
            rxn = model.reactions.get_by_id(ex)
            rxn.lower_bound = 0.0
            rxn.upper_bound = max(0.0, rxn.upper_bound)


def classify_transport(model, modelseed_id):
    cyt = f"{modelseed_id}[c0]"
    ext = f"{modelseed_id}[e0]"
    cyt_present = cyt in model.metabolites
    ext_present = ext in model.metabolites
    if not cyt_present and not ext_present:
        return "both_external_and_cytosol_metabolites_missing"
    if not ext_present:
        return "external_metabolite_missing"
    if not cyt_present:
        return "cytosol_metabolite_missing"
    for rxn in model.reactions:
        mets = {met.id for met in rxn.metabolites}
        if cyt in mets and ext in mets:
            return "transport_detected"
    return "exchange_or_metabolites_present_but_no_e0_to_c0_transport_detected"


def classify(expected, growth, net_growth, ex_exists, background):
    if expected == "positive_utilized":
        if not ex_exists:
            return "no_uptake_missing_exchange", "fail", "Positive substrate exchange missing."
        if net_growth > GROWTH_TOL:
            return "growth", "pass", "Positive substrate increases simulated growth above background."
        return "no_growth", "fail", "Positive substrate does not increase growth above background."
    if not ex_exists:
        return "no_uptake_missing_exchange", "pass_structural_negative", "No false positive possible without exchange."
    if net_growth <= GROWTH_TOL:
        if background > GROWTH_TOL:
            return "background_growth_no_uptake", "pass_structural_negative", "No substrate-specific growth above background."
        return "no_growth", "pass", "Negative substrate does not increase simulated growth."
    return "growth", "fail", "Negative substrate increases growth above background."


def solve(model):
    sol = model.optimize()
    return sol.objective_value if sol.status == "optimal" else 0.0


def run_panel(model_path: Path, label: str):
    model = cobra.io.read_sbml_model(str(model_path))
    model.solver = "glpk"
    rows = []
    all_subs = [(x, "positive_utilized") for x in POSITIVE] + [(x, "negative_nonutilized") for x in NEGATIVE]
    for scenario, co2_lb in SCENARIOS:
        with model as m_base:
            m_base.solver = "glpk"
            build_photoanaerobic_base(m_base, co2_lb)
            close_substrate_set(m_base)
            background = solve(m_base)
        rows.append(
            {
                "model": label,
                "scenario": scenario,
                "run_mode": "background_no_test_substrate",
                "substrate": "none",
                "exchange": "",
                "expected": "background_control",
                "exchange_exists": False,
                "transport_status": "not_applicable",
                "growth_flux": background,
                "background_growth_flux": background,
                "net_substrate_growth_flux": 0.0,
                "prediction": "background_control",
                "pass_fail": "background_control",
                "diagnosis": "Blank/control condition.",
            }
        )
        for (substrate, exchange, modelseed_id, description), expected in all_subs:
            with model as m:
                m.solver = "glpk"
                build_photoanaerobic_base(m, co2_lb)
                close_substrate_set(m)
                ex_exists = exchange in m.reactions
                if expected == "positive_utilized" and ex_exists:
                    set_bounds(m, exchange, -DEFAULT_CARBON_UPTAKE, 1000.0)
                elif expected == "negative_nonutilized" and ex_exists:
                    set_bounds(m, exchange, 0.0, 1000.0)
                growth = solve(m)
                net = max(0.0, growth - background)
                prediction, pass_fail, diagnosis = classify(expected, growth, net, ex_exists, background)
                rows.append(
                    {
                        "model": label,
                        "scenario": scenario,
                        "run_mode": "expected_design",
                        "substrate": substrate,
                        "exchange": exchange,
                        "expected": expected,
                        "exchange_exists": ex_exists,
                        "transport_status": classify_transport(m, modelseed_id),
                        "growth_flux": growth,
                        "background_growth_flux": background,
                        "net_substrate_growth_flux": net,
                        "prediction": prediction,
                        "pass_fail": pass_fail,
                        "diagnosis": diagnosis,
                    }
                )
                if expected == "negative_nonutilized" and ex_exists:
                    with model as md:
                        md.solver = "glpk"
                        build_photoanaerobic_base(md, co2_lb)
                        close_substrate_set(md)
                        set_bounds(md, exchange, -DEFAULT_CARBON_UPTAKE, 1000.0)
                        dgrowth = solve(md)
                        dnet = max(0.0, dgrowth - background)
                        rows.append(
                            {
                                "model": label,
                                "scenario": scenario,
                                "run_mode": "negative_forced_open_diagnostic",
                                "substrate": substrate,
                                "exchange": exchange,
                                "expected": expected,
                                "exchange_exists": ex_exists,
                                "transport_status": classify_transport(md, modelseed_id),
                                "growth_flux": dgrowth,
                                "background_growth_flux": background,
                                "net_substrate_growth_flux": dnet,
                                "prediction": "growth_if_forced_open" if dnet > GROWTH_TOL else "no_growth_even_if_forced_open",
                                "pass_fail": "diagnostic_fail" if dnet > GROWTH_TOL else "diagnostic_ok",
                                "diagnosis": "Forced negative uptake diagnostic.",
                            }
                        )
    return rows


def main() -> int:
    cobra.Configuration().solver = "glpk"
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for label, path in MODELS.items():
        rows.extend(run_panel(path, label))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "baseline_vs_candidate_python_phenotype_panel.tsv", sep="\t", index=False)
    expected = df[df["run_mode"].eq("expected_design")]
    summary = expected.groupby("model").agg(
        expected_tests=("pass_fail", "size"),
        pass_like=("pass_fail", lambda x: int(x.isin(["pass", "pass_structural_negative"]).sum())),
        fail_like=("pass_fail", lambda x: int((~x.isin(["pass", "pass_structural_negative"])).sum())),
    ).reset_index()
    summary["pass_rate"] = summary["pass_like"] / summary["expected_tests"]
    summary.to_csv(OUT / "baseline_vs_candidate_python_phenotype_summary.tsv", sep="\t", index=False)
    print(f"Wrote Python phenotype panel to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
