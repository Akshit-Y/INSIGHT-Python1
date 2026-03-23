import pandas as pd
import numpy as np
import logging
from src.utils.io import read_cdm_table

logger = logging.getLogger(__name__)

# These columns contain numbers (not codes or IDs)
CONTINUOUS_COLUMNS = {
    "MEDICAL_OBSERVATIONS": ["mo_value"],
    "MEDICINES":            ["quantity"],
}

DATE_COLUMNS_PER_TABLE = {
    "PERSONS":               ["date_of_birth"],
    "OBSERVATION_PERIODS":   ["op_start_date", "op_end_date"],
    "EVENTS":                ["start_date_record"],
    "MEDICINES":             ["date_dispensing"],
    "VACCINES":              ["vx_admin_date"],
    "PROCEDURES":            ["procedure_date"],
    "MEDICAL_OBSERVATIONS":  ["mo_date"],
    "VISIT_OCCURRENCE":      ["visit_start_date"],
}


def numeric_summary(series):
    """
    Compute basic descriptive statistics for a numeric column.
    """
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if len(numeric) == 0:
        return {}
    return {
        "n":       int(len(numeric)),
        "mean":    round(float(numeric.mean()), 2),
        "median":  round(float(numeric.median()), 2),
        "std":     round(float(numeric.std()), 2),
        "min":     round(float(numeric.min()), 2),
        "max":     round(float(numeric.max()), 2),
        "q25":     round(float(numeric.quantile(0.25)), 2),
        "q75":     round(float(numeric.quantile(0.75)), 2),
    }


def date_distribution(series):
    """
    Count how many records fall in each calendar year.
    Returns a small DataFrame: year | count
    """
    years = series.str[:4]
    valid_years = years[years.str.match(r"^\d{4}$", na=False)]
    counts = valid_years.value_counts().sort_index().reset_index()
    counts.columns = ["year", "count"]
    return counts


def run(config):
    """
    Step 5: Distributions of continuous variables and date variables.
    - For numbers: mean, median, IQR, min, max
    - For dates: count of records per year
    """
    cdm_path = config["paths"]["cdm_data"]
    numeric_results = []
    date_dist_results = {}

    for table_name in config["tables_present"]:
        df = read_cdm_table(table_name, cdm_path)
        if df is None:
            continue

        # Numeric summaries
        cont_cols = CONTINUOUS_COLUMNS.get(table_name, [])
        for col in cont_cols:
            if col in df.columns:
                stats = numeric_summary(df[col])
                if stats:
                    stats["table"]    = table_name
                    stats["variable"] = col
                    numeric_results.append(stats)

        # Date distributions
        date_cols = DATE_COLUMNS_PER_TABLE.get(table_name, [])
        date_dist_results[table_name] = {}
        for col in date_cols:
            if col in df.columns:
                dist = date_distribution(df[col])
                date_dist_results[table_name][col] = dist

    numeric_df = pd.DataFrame(numeric_results)
    return {
        "numeric_summaries": numeric_df,
        "date_distributions": date_dist_results
    }