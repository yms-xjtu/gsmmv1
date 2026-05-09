from pathlib import Path
import re

import cobra
import pandas as pd
from cobra.flux_analysis import flux_variability_analysis


ROOT = Path(__file__).resolve().parents[2]
MODELS = {
    "v1_13_baseline": ROOT / "baseline" / "mymodel_CGA009_publishable_v1.13_lps_acp_acyltransferase_for_memote.xml",
    "v1_14_candidate_n2": ROOT / "candidate_v1.14" / "candidate_model_n2_boundary" / "mymodel_CGA009_candidate_v1.14_n2_boundary.xml",
    "iRpa940_reference": ROOT / "candidate_v1.14" / "reference_models" / "iRpa940_SBML_model.xml",
}
OUT = ROOT / "candidate_v1.14" / "reference_model_adversarial_compare"

SUBSTRATES = {
    "acetate": ["cpd00029", "acetate", "ac_e", "EX_ac"],
    "succinate": ["cpd00036", "succinate", "succ_e", "EX_succ"],
    "malate": ["cpd00130", "malate", "mal__L_e", "EX_mal"],
    "butyrate": ["cpd00211", "butyrate", "but_e", "EX_but"],
    "fumarate": ["cpd00106", "fumarate", "fum_e", "EX_fum"],
    "p_coumarate": ["cpd00604", "coumarate", "4-coumarate"],
    "benzoate": ["cpd00153", "benzoate", "benz"],
    "4_hydroxybenzoate": ["cpd00136", "hydroxybenzoate", "4hbz"],
    "glucose_negative": ["cpd00027", "glucose", "glc"],
    "xylose_negative": ["cpd00154", "xylose", "xyl"],
    "fructose_negative": ["cpd00082", "fructose", "fru"],
    "n2": ["cpd00528", "dinitrogen"],
    "h2": ["cpd11640", "hydrogen", "h2"],
    "co2": ["cpd00011", "co2", "carbon dioxide"],
}

MODULE_TERMS = {
    "nitrogenase": ["nitrogenase", "dinitrogen", "cpd00528", "rxn06874"],
    "h2": ["cpd11640", "hydrogen", "h2"],
    "cbb_rubisco": ["ribulose", "rubisco", "ribulose-1,5", "cpd00871", "cpd00169"],
    "phb": ["poly-beta-hydroxybutyrate", "polyhydroxybutyrate", "cpd12836", "3-hydroxybutanoyl"],
    "ferredoxin": ["ferredoxin", "cpd11620", "cpd11621"],
}


def safe_read_model(path: Path):
    cobra.Configuration().solver = "glpk"
    model = cobra.io.read_sbml_model(str(path))
    model.solver = "glpk"
    return model


def text_match(text: str, terms: list[str]) -> bool:
    t = text.lower()
    return any(term.lower() in t for term in terms)


def exchange_matches_substrate(rxn, substrate: str, terms: list[str]) -> bool:
    txt = reaction_text(rxn)
    if substrate == "n2":
        lowered = txt.lower()
        return (
            "cpd00528" in lowered
            or "dinitrogen" in lowered
            or bool(re.search(r"(^|[^a-z0-9])n2([^a-z0-9]|$)", lowered))
        )
    if substrate == "h2":
        lowered = txt.lower()
        return (
            "cpd11640" in lowered
            or "hydrogen" in lowered
            or bool(re.search(r"(^|[^a-z0-9])h2([^a-z0-9]|$)", lowered))
        )
    return text_match(txt, terms)


def reaction_text(rxn) -> str:
    return " ".join([rxn.id, rxn.name or "", rxn.reaction, rxn.gene_reaction_rule or ""])


def exchange_rows(model, label):
    rows = []
    boundary_like = set(model.exchanges) | {rxn for rxn in model.reactions if len(rxn.metabolites) == 1}
    for rxn in boundary_like:
        for substrate, terms in SUBSTRATES.items():
            if exchange_matches_substrate(rxn, substrate, terms):
                rows.append(
                    {
                        "model": label,
                        "substrate_or_metabolite": substrate,
                        "exchange_id": rxn.id,
                        "name": rxn.name,
                        "lower_bound": rxn.lower_bound,
                        "upper_bound": rxn.upper_bound,
                        "reaction": rxn.reaction,
                        "cobra_exchange": rxn in model.exchanges,
                        "single_metabolite_boundary": len(rxn.metabolites) == 1,
                    }
                )
    return rows


def module_rows(model, label):
    rows = []
    for rxn in model.reactions:
        txt = reaction_text(rxn)
        for module, terms in MODULE_TERMS.items():
            if text_match(txt, terms):
                rows.append(
                    {
                        "model": label,
                        "module": module,
                        "reaction_id": rxn.id,
                        "name": rxn.name,
                        "lower_bound": rxn.lower_bound,
                        "upper_bound": rxn.upper_bound,
                        "reaction": rxn.reaction,
                        "gpr": rxn.gene_reaction_rule,
                        "is_exchange": rxn in model.exchanges,
                    }
                )
    return rows


def qc_summary(model, label):
    sol = model.optimize()
    imbalanced = 0
    for rxn in model.reactions:
        if rxn in model.exchanges or len(rxn.metabolites) == 1:
            continue
        if rxn.id.lower().startswith("bio") or "biomass" in (rxn.id + " " + (rxn.name or "")).lower():
            continue
        if rxn.check_mass_balance():
            imbalanced += 1
    return {
        "model": label,
        "reactions": len(model.reactions),
        "metabolites": len(model.metabolites),
        "genes": len(model.genes),
        "exchanges": len(model.exchanges),
        "missing_formula_metabolites": sum(1 for met in model.metabolites if not met.formula),
        "missing_charge_metabolites": sum(1 for met in model.metabolites if met.charge is None),
        "fba_status_default": sol.status,
        "fba_objective_default": sol.objective_value,
        "internal_checkable_imbalances": imbalanced,
    }


def substrate_support_matrix(exchange_df):
    rows = []
    for model in exchange_df["model"].unique():
        sub = exchange_df[exchange_df["model"] == model]
        for substrate in SUBSTRATES:
            hits = sub[sub["substrate_or_metabolite"] == substrate]
            rows.append(
                {
                    "model": model,
                    "substrate_or_metabolite": substrate,
                    "exchange_count": len(hits),
                    "uptake_open_by_default": bool((hits["lower_bound"] < 0).any()) if len(hits) else False,
                    "exchange_ids": ";".join(hits["exchange_id"].astype(str).tolist()),
                    "bounds": ";".join((hits["lower_bound"].astype(str) + "/" + hits["upper_bound"].astype(str)).tolist()),
                }
            )
    return pd.DataFrame(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    models = {label: safe_read_model(path) for label, path in MODELS.items()}
    summaries = []
    exchanges = []
    modules = []
    for label, model in models.items():
        summaries.append(qc_summary(model, label))
        exchanges.extend(exchange_rows(model, label))
        modules.extend(module_rows(model, label))
    summary_df = pd.DataFrame(summaries)
    exchange_df = pd.DataFrame(exchanges)
    module_df = pd.DataFrame(modules)
    support_df = substrate_support_matrix(exchange_df)

    summary_df.to_csv(OUT / "model_qc_size_comparison.tsv", sep="\t", index=False)
    exchange_df.to_csv(OUT / "matched_exchange_reactions.tsv", sep="\t", index=False)
    support_df.to_csv(OUT / "substrate_exchange_support_matrix.tsv", sep="\t", index=False)
    module_df.to_csv(OUT / "key_module_reaction_matches.tsv", sep="\t", index=False)

    concern_rows = []
    for substrate in ["acetate", "succinate", "malate", "butyrate", "p_coumarate", "glucose_negative", "xylose_negative", "fructose_negative", "n2"]:
        pivot = support_df[support_df["substrate_or_metabolite"] == substrate]
        values = {
            row["model"]: row["exchange_count"]
            for _, row in pivot.iterrows()
        }
        uptake = {
            row["model"]: row["uptake_open_by_default"]
            for _, row in pivot.iterrows()
        }
        concern = ""
        if substrate == "n2" and values.get("v1_13_baseline", 0) == 0 and values.get("iRpa940_reference", 0) > 0:
            concern = "v1.13 lacks N2 exchange found in reference; supports candidate N2 boundary audit."
        elif substrate.endswith("_negative") and values.get("v1_13_baseline", 0) > 0:
            concern = "Negative substrate has exchange in v1.13; verify transport prevents false-positive growth."
        elif substrate in ["acetate", "succinate", "malate", "butyrate", "p_coumarate"] and values.get("v1_13_baseline", 0) == 0:
            concern = "Expected positive substrate lacks v1.13 exchange; would threaten phenotype validation."
        if concern:
            concern_rows.append(
                {
                    "substrate_or_metabolite": substrate,
                    "baseline_exchange_count": values.get("v1_13_baseline", 0),
                    "candidate_exchange_count": values.get("v1_14_candidate_n2", 0),
                    "reference_exchange_count": values.get("iRpa940_reference", 0),
                    "baseline_uptake_open_by_default": uptake.get("v1_13_baseline", False),
                    "candidate_uptake_open_by_default": uptake.get("v1_14_candidate_n2", False),
                    "reference_uptake_open_by_default": uptake.get("iRpa940_reference", False),
                    "adversarial_concern": concern,
                }
            )
    pd.DataFrame(concern_rows).to_csv(OUT / "adversarial_concerns.tsv", sep="\t", index=False)
    print(f"Wrote adversarial reference comparison to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
