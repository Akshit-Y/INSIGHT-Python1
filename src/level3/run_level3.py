"""
Level 3 — Data Characterization
Orchestrates all 8 steps and produces HTML reports.
Designed to match the structure of run_level1.py exactly.
"""
import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.utils.reporting import render_report, dataframe_to_table
from . import (step1_population, step2_medicines, step3_vaccines,
               step4_diagnoses, step5_pregnancy, step6_populations,
               step7_lifestyle, step8_eurocat)

logger = logging.getLogger(__name__)


# ── small plot helpers ─────────────────────────────────────────────────────────

def _bar_by_year(by_year: dict, title: str, color: str = "#378ADD") -> str:
    if not by_year:
        return ""
    df = pd.DataFrame(
        [(str(k), v) for k, v in sorted(by_year.items())],
        columns=["year", "count"]
    )
    fig = px.bar(df, x="year", y="count", title=title,
                 color_discrete_sequence=[color],
                 labels={"year": "Year", "count": "Records"})
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                      font_family="Arial", height=320,
                      margin=dict(l=10, r=10, t=40, b=60))
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def _pie(counts: dict, title: str) -> str:
    if not counts:
        return ""
    df = pd.DataFrame(
        [(str(k), v) for k, v in counts.items()],
        columns=["category", "count"]
    )
    fig = px.pie(df, names="category", values="count", title=title,
                 color_discrete_sequence=px.colors.qualitative.Safe)
    fig.update_layout(font_family="Arial", height=340,
                      margin=dict(l=10, r=10, t=40, b=10))
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def _bar_h(counts: dict, title: str, color: str = "#1D9E75") -> str:
    if not counts:
        return ""
    df = pd.DataFrame(
        [(str(k), v) for k, v in list(counts.items())[:20]],
        columns=["category", "count"]
    ).sort_values("count")
    fig = px.bar(df, x="count", y="category", orientation="h", title=title,
                 color_discrete_sequence=[color],
                 labels={"category": "", "count": "Count"})
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                      font_family="Arial", height=420,
                      margin=dict(l=10, r=10, t=40, b=40))
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


# ── main runner ────────────────────────────────────────────────────────────────

def run(config: dict) -> dict:
    output_path = config["paths"]["output_reports"]

    print("\n" + "=" * 60)
    print("LEVEL 3 — Data Characterization")
    print("=" * 60)

    # ── Run all steps ──────────────────────────────────────────────────────────
    print("\n[Step 1] Study-source population...")
    s1 = step1_population.run(config)

    print("\n[Step 2] Medicines...")
    s2 = step2_medicines.run(config)

    print("\n[Step 3] Vaccines...")
    s3 = step3_vaccines.run(config)

    print("\n[Step 4] Diagnoses...")
    s4 = step4_diagnoses.run(config)

    print("\n[Step 5] Pregnancy...")
    s5 = step5_pregnancy.run(config)

    print("\n[Step 6] Populations of interest...")
    s6 = step6_populations.run(config)

    print("\n[Step 7] Lifestyle and health-seeking behaviour...")
    s7 = step7_lifestyle.run(config)

    print("\n[Step 8] EUROCAT indicators...")
    s8 = step8_eurocat.run(config)

    # ── Build plots ────────────────────────────────────────────────────────────
    pop_year_plot  = _bar_by_year(s1.get("pop_by_year", {}),
                                   "Persons entering follow-up by year", "#185FA5")
    sex_pie        = _pie(s1.get("sex_counts", {}), "Sex distribution")
    age_bar        = _bar_h(s1.get("age_dist", {}), "Age group distribution", "#378ADD")
    med_year_plot  = _bar_by_year(s2.get("by_year", {}),
                                   "Medicine dispensing events by year", "#1D9E75")
    med_pie        = _pie(s2.get("by_meaning", {}), "Medicines by data source")
    vax_year_plot  = _bar_by_year(s3.get("by_year", {}),
                                   "Vaccine administrations by year", "#52b788")
    vax_pie        = _pie(s3.get("by_type", {}), "Vaccine types")
    diag_year_plot = _bar_by_year(s4.get("by_year", {}),
                                   "Diagnosis events by year", "#534AB7")
    diag_bar       = _bar_h(s4.get("by_meaning", {}),
                             "Top 20 event types (meaning)", "#7F77DD")
    preg_year_plot = _bar_by_year(s5.get("by_year", {}),
                                   "Pregnancy records by year", "#D4537E")
    preg_pie       = _pie(s5.get("by_type", {}), "Pregnancy types")
    visit_plot     = _bar_by_year(s7.get("visit_by_year", {}),
                                   "Healthcare encounters by year", "#BA7517")
    lifestyle_bar  = _bar_h(s7.get("lifestyle_counts", {}),
                             "Lifestyle factor record types", "#EF9F27")

    # ── Subgroup table for Step 6 ──────────────────────────────────────────────
    subgroup_df = pd.DataFrame(s6.get("subgroups", []))

    # ── Assemble report sections (same structure as Level 1) ───────────────────
    sections = [
        {
            "title":       "Step 1 — Study-Source Population",
            "description": (
                "High-level characterization of the study population: total persons, "
                "sex distribution, age group distribution, and follow-up duration. "
                "★ Mandatory step."
            ),
            "status":    "pass" if s1["available"] else "fail",
            "table":     None,
            "plot_html": sex_pie + age_bar + pop_year_plot
        },
        {
            "title":       "Step 2 — Medicines",
            "description": (
                "Counts and rates of medicine dispensing over calendar time. "
                "Shows top medicinal products and breakdown by data source."
            ),
            "status":    "pass" if s2["available"] else "warn",
            "table":     None,
            "plot_html": med_year_plot + med_pie
        },
        {
            "title":       "Step 3 — Vaccines",
            "description": (
                "Counts and rates of vaccine administration over calendar time, "
                "broken down by vaccine type."
            ),
            "status":    "pass" if s3["available"] else "warn",
            "table":     None,
            "plot_html": vax_year_plot + vax_pie
        },
        {
            "title":       "Step 4 — Diagnoses",
            "description": (
                "Incidence of clinical events and diagnoses over the study period. "
                "Shows top event types, ICD codes, and coding vocabularies used."
            ),
            "status":    "pass" if s4["available"] else "warn",
            "table":     None,
            "plot_html": diag_year_plot + diag_bar
        },
        {
            "title":       "Step 5 — Pregnancy",
            "description": (
                "Pregnancy-related records from SURVEY_ID or EVENTS, "
                "stratified by pregnancy type (ongoing, birth, abortion, etc.)."
            ),
            "status":    "pass" if s5["available"] else "warn",
            "table":     None,
            "plot_html": preg_year_plot + preg_pie
        },
        {
            "title":       "Step 6 — Populations of Interest",
            "description": (
                "Sub-group analysis: females of reproductive age, elderly (65+), "
                "children (0–17), and breakdown by data provenance."
            ),
            "status":    "pass" if s6["available"] else "warn",
            "table":     dataframe_to_table(subgroup_df) if not subgroup_df.empty else None,
            "plot_html": _pie(s6.get("by_provenance", {}), "Records by data provenance")
        },
        {
            "title":       "Step 7 — Lifestyle and Health-Seeking Behaviour",
            "description": (
                "Healthcare visit counts over time from VISIT_OCCURRENCE. "
                "Lifestyle factor records (BMI, smoking, alcohol, etc.) "
                "from MEDICAL_OBSERVATIONS."
            ),
            "status":    None,
            "table":     None,
            "plot_html": visit_plot + lifestyle_bar
        },
        {
            "title":       "Step 8 — EUROCAT Indicators",
            "description": (
                "Data quality indicators for congenital anomalies from the "
                "EUROCAT or SURVEY_OBSERVATIONS table. "
                "Only applicable for DAPs with registry data on birth defects."
            ),
            "status":    "pass" if s8["available"] else "warn",
            "table":     None,
            "plot_html": (_bar_by_year(s8.get("by_year", {}),
                                       "EUROCAT records by year", "#639922")
                          + _bar_h(s8.get("top_codes", {}),
                                   "Top congenital anomaly codes", "#3B6D11"))
        },
    ]

    # ── Summary stat boxes at top of report ────────────────────────────────────
    fu = s1.get("followup", {})
    stats = [
        {"label": "Total persons",
         "value": f"{s1.get('total_persons', 0):,}"},
        {"label": "Total person-years",
         "value": f"{fu.get('total_person_years', 'N/A'):,}"},
        {"label": "Medicine records",
         "value": f"{s2.get('total_records', 0):,}"},
        {"label": "Vaccine records",
         "value": f"{s3.get('total_records', 0):,}"},
        {"label": "Event/diagnosis records",
         "value": f"{s4.get('total_records', 0):,}"},
        {"label": "Pregnancy records",
         "value": f"{s5.get('total', 0):,}"},
    ]

    render_report(
        title="Level 3 — Data Characterization",
        sections=sections,
        config=config,
        output_path=output_path,
        filename="Level3_Report.html",
        stats=stats
    )

    print("\n✓ Level 3 complete.")
    print(f"  Report saved to: {output_path}Level3_Report.html")

    return {"step1": s1, "step2": s2, "step3": s3, "step4": s4,
            "step5": s5, "step6": s6, "step7": s7, "step8": s8}
