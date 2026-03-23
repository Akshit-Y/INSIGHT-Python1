import logging
import plotly.express as px
import pandas as pd

from src.utils.reporting import render_report, dataframe_to_table
from . import step0_metadata
from . import step1_formatting
from . import step2_missing
from . import step3_dates
from . import step4_conventions
from . import step5_distributions

logger = logging.getLogger(__name__)


def run(config):
    """
    Run all Level 1 checks in order and produce one HTML report.
    """
    output_path = config["paths"]["output_reports"]

    print("\n" + "=" * 60)
    print("LEVEL 1 — Conformance & Completeness")
    print("=" * 60)

    # ── Step 0 ────────────────────────────────────────────────────────────────
    print("\n[Step 0] Checking table presence...")
    s0 = step0_metadata.run(config)

    # ── Step 1 ────────────────────────────────────────────────────────────────
    print("\n[Step 1] Checking table formatting...")
    s1 = step1_formatting.run(config)

    # Flatten Step 1 results into one DataFrame for the report
    s1_rows = []
    for table_name, checks in s1.items():
        for check in checks:
            s1_rows.append({"table": table_name, **check})
    s1_df = pd.DataFrame(s1_rows)

    # ── Step 2 ────────────────────────────────────────────────────────────────
    print("\n[Step 2] Analysing missing data...")
    s2 = step2_missing.run(config)

    # ── Step 3 ────────────────────────────────────────────────────────────────
    print("\n[Step 3] Validating date variables...")
    s3 = step3_dates.run(config)

    # ── Step 4 ────────────────────────────────────────────────────────────────
    print("\n[Step 4] Checking conventions and frequency tables...")
    s4 = step4_conventions.run(config)

    # ── Step 5 ────────────────────────────────────────────────────────────────
    print("\n[Step 5] Computing distributions...")
    s5 = step5_distributions.run(config)

    # ── Build plots ───────────────────────────────────────────────────────────
    missing_plot_html = ""
    if not s2["overall"].empty:
        top_missing = (
            s2["overall"]
            .nlargest(20, "missing_pct")
            [["table", "variable", "missing_pct"]]
        )
        top_missing["label"] = top_missing["table"] + "." + top_missing["variable"]
        fig = px.bar(
            top_missing,
            x="missing_pct",
            y="label",
            orientation="h",
            title="Top 20 most-missing variables (%)",
            color_discrete_sequence=["#378ADD"],
            labels={"missing_pct": "Missing (%)", "label": ""}
        )
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font_family="Arial", height=420,
            margin=dict(l=10, r=20, t=40, b=40),
            yaxis=dict(autorange="reversed")
        )
        missing_plot_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

    date_plot_html = ""
    if not s3.empty:
        fig2 = px.bar(
            s3,
            x="date_variable",
            y=["error_format", "error_year", "future_date"],
            title="Date validation issues by column",
            barmode="stack",
            color_discrete_map={
                "error_format": "#E24B4A",
                "error_year":   "#378ADD",
                "future_date":  "#1D9E75"
            },
            labels={"date_variable": "Date column", "value": "Number of records"}
        )
        fig2.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font_family="Arial", height=380,
            margin=dict(l=10, r=20, t=40, b=100)
        )
        date_plot_html = fig2.to_html(full_html=False, include_plotlyjs="cdn")

    # ── Assemble report sections ───────────────────────────────────────────────
    # Figure out overall statuses
    s0_status = "fail" if s0["n_missing_mandatory"] > 0 else "pass"
    s1_status = "fail" if (not s1_df.empty and (s1_df["status"] == "FAIL").any()) else "pass"
    s3_status = "fail" if (not s3.empty and s3["has_issues"].any()) else "pass"
    s4_status = "fail" if (
        not s4["conventions"].empty and
        (s4["conventions"]["status"] == "FAIL").any()
    ) else "pass"

    sections = [
        {
            "title":       "Step 0 — CDM Table Presence",
            "description": (
                "Checks whether all required CDM table files exist on disk. "
                "Missing mandatory tables are a hard FAIL — no further analysis "
                "is possible for those tables."
            ),
            "status":    s0_status,
            "table":     dataframe_to_table(s0["results_df"]),
            "plot_html": None
        },
        {
            "title":       "Step 1 — Table Formatting",
            "description": (
                "For each table: are all column names lowercase? "
                "Are all mandatory columns present? Are there any duplicate rows? "
                "For the PERSONS table, are sex values one of M/F/U/O?"
            ),
            "status":    s1_status,
            "table":     dataframe_to_table(s1_df) if not s1_df.empty else None,
            "plot_html": None
        },
        {
            "title":       "Step 2 — Missing Data Analysis",
            "description": (
                "Percentage of missing values for every variable in every table. "
                "The chart shows the 20 most-missing variables. "
                "High missingness in mandatory fields needs ETL investigation."
            ),
            "status":    None,
            "table":     dataframe_to_table(
                             s2["overall"].sort_values("missing_pct", ascending=False)
                         ) if not s2["overall"].empty else None,
            "plot_html": missing_plot_html
        },
        {
            "title":       "Step 3 — Date Variable Validation",
            "description": (
                f"Three checks per date column: "
                f"(1) format must be exactly YYYYMMDD, "
                f"(2) year must be ≥ {config['study']['start_year']}, "
                f"(3) date must not be in the future. "
                f"The chart shows counts of each error type."
            ),
            "status":    s3_status,
            "table":     dataframe_to_table(s3) if not s3.empty else None,
            "plot_html": date_plot_html
        },
        {
            "title":       "Step 4 — Conventions & Frequency Tables",
            "description": (
                "Checks that categorical columns only contain allowed values "
                "(e.g. sex must be M/F/U/O, not '1'/'2'). "
                "Also shows the distribution of each categorical variable."
            ),
            "status":    s4_status,
            "table":     dataframe_to_table(s4["conventions"])
                         if not s4["conventions"].empty else None,
            "plot_html": None
        },
        {
            "title":       "Step 5 — Distributions",
            "description": (
                "Descriptive statistics for numeric variables "
                "(mean, median, IQR, min, max) and counts of records per year "
                "for date variables."
            ),
            "status":    None,
            "table":     dataframe_to_table(s5["numeric_summaries"])
                         if not s5["numeric_summaries"].empty else None,
            "plot_html": None
        }
    ]

    # Summary stat boxes at the top of the report
    n_format_errors = int(s3["error_format"].sum()) if not s3.empty else 0
    n_year_errors   = int(s3["error_year"].sum())   if not s3.empty else 0
    n_future_dates  = int(s3["future_date"].sum())  if not s3.empty else 0
    n_miss_high     = int(
        (s2["overall"]["missing_pct"] > 20).sum()
    ) if not s2["overall"].empty else 0

    stats = [
        {"label": "Tables present",
         "value": s0["results_df"][s0["results_df"]["present"] == "Yes"].shape[0]},
        {"label": "Tables missing (mandatory)",
         "value": s0["n_missing_mandatory"]},
        {"label": "Variables with >20% missing",
         "value": n_miss_high},
        {"label": "Date format errors",
         "value": n_format_errors},
        {"label": "Dates before cutoff year",
         "value": n_year_errors},
        {"label": "Future dates",
         "value": n_future_dates},
    ]

    render_report(
        title="Level 1 — Conformance & Completeness",
        sections=sections,
        config=config,
        output_path=output_path,
        filename="Level1_Report.html",
        stats=stats
    )

    print("\n Level 1 complete.")
    print(f" Report saved to: {output_path}Level1_Report.html")

    return {
        "step0": s0,
        "step1": s1,
        "step2": s2,
        "step3": s3,
        "step4": s4,
        "step5": s5
    }