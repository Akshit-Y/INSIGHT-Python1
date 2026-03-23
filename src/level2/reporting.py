import pandas as pd
from src.utils.reporting import render_report, dataframe_to_table


THRESHOLD = 5.0  # % threshold


def build_level2_report(results: dict, config: dict):
    rows = []

    for step_name, res in results.items():
        if not res.get("available", False):
            rows.append({
                "step": step_name,
                "violations": "-",
                "total": "-",
                "pct": "-",
                "status": "SKIPPED"
            })
            continue

        total = res.get("total", 0)
        violations = res.get("violations", 0)
        pct = round(100 * violations / max(total, 1), 2)

        status = "PASS" if pct <= THRESHOLD else "FAIL"

        rows.append({
            "step": step_name,
            "violations": violations,
            "total": total,
            "pct": pct,
            "status": status
        })

    df = pd.DataFrame(rows)

    n_fail = (df["status"] == "FAIL").sum()

    sections = [
        {
            "title": "Level 2 — Temporal & Logical Checks",
            "description": "Checks temporal plausibility and cross-table integrity. FAIL if >5%.",
            "status": "fail" if n_fail > 0 else "pass",
            "table": dataframe_to_table(df),
            "plot_html": None
        }
    ]

    print(type(config))
    print(config)

    # ✅ Correct call
    render_report(
    config=config,
    title="INSIGHT — Level 2 Report",
    sections=sections,
    output_path=config["paths"]["output_reports"],
    filename="Level2_Report.html"
)

    print("\nReport saved → ./output/Level2_Report.html")