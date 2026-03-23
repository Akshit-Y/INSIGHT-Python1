import pandas as pd
from src.utils.reporting import render_report, dataframe_to_table


def build_final_report(config, l1, l2, l3):

    import pandas as pd
    from src.utils.reporting import render_report, dataframe_to_table

    # ── LEVEL 1 SUMMARY ─────────────────────────────
    l1_issues = l1.get("failed_checks", 0)
    l1_status = "PASS" if l1_issues == 0 else "MINOR ISSUES"

    # ── LEVEL 2 SUMMARY ─────────────────────────────
    l2_pcts = []
    for v in l2.values():
        if not v.get("available", False):
            continue
        total = v.get("total", 0)
        violations = v.get("violations", 0)
        pct = 100 * violations / max(total, 1)
        l2_pcts.append(pct)

    avg_l2 = round(sum(l2_pcts) / max(len(l2_pcts), 1), 2)
    l2_status = "PASS" if avg_l2 <= 5 else "FAIL"

    # ── LEVEL 3 SUMMARY ─────────────────────────────
    pop = l3.get("population", {}).get("n_persons", 0)
    med = l3.get("medicines", {}).get("total_records", 0)
    vax = l3.get("vaccines", {}).get("total_records", 0)

    richness_score = pop + med + vax

    l3_status = "GOOD" if richness_score > 0 else "LIMITED"

    # ── FINAL VERDICT ───────────────────────────────
    if l2_status == "FAIL":
        verdict = "NOT FIT FOR PURPOSE"
    elif l1_status != "PASS":
        verdict = "FIT WITH DATA QUALITY ISSUES"
    else:
        verdict = "FIT FOR PURPOSE"

    # ── TABLE ───────────────────────────────────────
    df = pd.DataFrame([
        {"Component": "Level 1 (Structure)", "Status": l1_status},
        {"Component": "Level 2 (Logic)", "Status": l2_status},
        {"Component": "Level 3 (Usability)", "Status": l3_status},
        {"Component": "Final Verdict", "Status": verdict}
    ])

    sections = [{
        "title": "Final INSIGHT Assessment",
        "description": "Combined evaluation across all levels",
        "status": "pass" if "FIT FOR PURPOSE" in verdict else "fail",
        "table": dataframe_to_table(df),
        "plot_html": None
    }]

    render_report(
        config=config,
        title="INSIGHT — Final Report",
        sections=sections,
        output_path=config["paths"]["output_reports"],
        filename="Final_Report.html"
    )