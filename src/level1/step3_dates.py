import pandas as pd
import logging
from src.utils.io import read_cdm_table
from src.utils.validators import validate_date_value

logger = logging.getLogger(__name__)

DATE_COLUMNS_PER_TABLE = {
    "PERSONS":               ["date_of_birth"],
    "OBSERVATION_PERIODS":   ["op_start_date", "op_end_date"],
    "EVENTS":                ["start_date_record", "end_date_record"],
    "MEDICINES":             ["date_dispensing", "date_prescription"],
    "VACCINES":              ["vx_admin_date", "vx_record_date"],
    "PROCEDURES":            ["procedure_date"],
    "MEDICAL_OBSERVATIONS":  ["mo_date"],
    "VISIT_OCCURRENCE":      ["visit_start_date", "visit_end_date"],
}


def check_one_date_column(df, table_name, date_col, start_year):
    """
    For one date column in one table, validate every single value.
    Returns a summary row (one row per column, not per record).
    """
    if date_col not in df.columns:
        return None

    n_format_error = 0
    n_year_error   = 0
    n_future       = 0
    total          = len(df)

    for raw_val in df[date_col]:
        result = validate_date_value(str(raw_val) if pd.notna(raw_val) else "", start_year)
        if result["error_format"]: n_format_error += 1
        if result["error_year"]:   n_year_error   += 1
        if result["future_date"]:  n_future        += 1

    has_issues = (n_format_error + n_year_error + n_future) > 0

    return {
        "table":            table_name,
        "date_variable":    date_col,
        "total_records":    total,
        "error_format":     n_format_error,
        "error_year":       n_year_error,
        "future_date":      n_future,
        "has_issues":       has_issues,
        "status":           "FAIL" if has_issues else "PASS"
    }


def run(config):
    """
    Step 3: Check every date column in every CDM table.
    Looks for: wrong format, year before cutoff, dates in the future.
    This mirrors the 'Dates Check' section shown in Figure 3 of the paper.
    """
    cdm_path   = config["paths"]["cdm_data"]
    start_year = config["study"]["start_year"]
    all_rows   = []

    for table_name, date_cols in DATE_COLUMNS_PER_TABLE.items():
        if table_name not in config["tables_present"]:
            continue

        df = read_cdm_table(table_name, cdm_path)
        if df is None:
            continue

        for date_col in date_cols:
            row = check_one_date_column(df, table_name, date_col, start_year)
            if row:
                all_rows.append(row)

    if not all_rows:
        return pd.DataFrame()

    results_df = pd.DataFrame(all_rows)

    total_issues = results_df["has_issues"].sum()
    logger.info(f"Step 3: {total_issues}/{len(results_df)} date columns have issues")
    return results_df