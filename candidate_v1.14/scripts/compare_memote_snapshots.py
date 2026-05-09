import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "candidate_v1.14" / "memote_comparison"
SNAPSHOTS = {
    "baseline_v1.13": ROOT
    / "candidate_v1.14"
    / "memote_baseline_v1_13"
    / "memote_baseline_v1_13.html",
    "candidate_n2_boundary": ROOT
    / "candidate_v1.14"
    / "memote_candidate_n2_boundary"
    / "memote_candidate_n2_boundary.html",
}


def load_memote_html(path: Path) -> dict:
    html = path.read_text(encoding="utf-8")
    marker = "window.data = "
    start = html.index(marker) + len(marker)
    end = html.index("\n    window.reportType", start)
    payload = html[start:end].strip().rstrip(";")
    return json.loads(payload)


def flatten_tests(data: dict, label: str) -> list[dict]:
    rows = []
    for test_id, test in data["tests"].items():
        result = test.get("result")
        if isinstance(result, dict):
            for sub_id, sub_result in result.items():
                rows.append(
                    {
                        "model": label,
                        "test_id": f"{test_id}:{sub_id}",
                        "result": sub_result,
                        "metric": test.get("metric", {}).get(sub_id),
                    }
                )
        else:
            rows.append(
                {
                    "model": label,
                    "test_id": test_id,
                    "result": result,
                    "metric": test.get("metric"),
                }
            )
    return rows


def score_rows(data: dict, label: str) -> list[dict]:
    rows = [
        {
            "model": label,
            "section": "total",
            "score": data["score"]["total_score"],
        }
    ]
    for section in data["score"]["sections"]:
        rows.append(
            {
                "model": label,
                "section": section["section"],
                "score": section["score"],
            }
        )
    return rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    parsed = {label: load_memote_html(path) for label, path in SNAPSHOTS.items()}

    scores = []
    tests = []
    for label, data in parsed.items():
        scores.extend(score_rows(data, label))
        tests.extend(flatten_tests(data, label))

    score_df = pd.DataFrame(scores)
    test_df = pd.DataFrame(tests)
    score_df.to_csv(OUT / "baseline_vs_candidate_memote_scores.tsv", sep="\t", index=False)
    test_df.to_csv(OUT / "baseline_vs_candidate_memote_tests.tsv", sep="\t", index=False)

    wide = test_df.pivot(index="test_id", columns="model", values=["result", "metric"])
    changes = []
    for test_id, row in wide.iterrows():
        base_result = row.get(("result", "baseline_v1.13"))
        cand_result = row.get(("result", "candidate_n2_boundary"))
        base_metric = row.get(("metric", "baseline_v1.13"))
        cand_metric = row.get(("metric", "candidate_n2_boundary"))
        metric_delta = None
        if pd.notna(base_metric) and pd.notna(cand_metric):
            metric_delta = float(cand_metric) - float(base_metric)
        if base_result != cand_result or (metric_delta is not None and abs(metric_delta) > 1e-12):
            changes.append(
                {
                    "test_id": test_id,
                    "baseline_result": base_result,
                    "candidate_result": cand_result,
                    "baseline_metric": base_metric,
                    "candidate_metric": cand_metric,
                    "candidate_minus_baseline_metric": metric_delta,
                }
            )

    pd.DataFrame(changes).to_csv(
        OUT / "baseline_vs_candidate_memote_changed_tests.tsv", sep="\t", index=False
    )

    status_counts = (
        test_df.groupby(["model", "result"]).size().reset_index(name="test_count")
    )
    status_counts.to_csv(
        OUT / "baseline_vs_candidate_memote_status_counts.tsv", sep="\t", index=False
    )
    print(f"Wrote MEMOTE comparison tables to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
