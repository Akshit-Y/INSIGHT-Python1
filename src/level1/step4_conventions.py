import pandas as pd
import logging
from src.utils.io import read_cdm_table

logger = logging.getLogger(__name__)

# For each table, define which categorical columns have known allowed values
CATEGORICAL_CONVENTIONS = {
    "PERSONS": {
        "sex_at_instance_creation": ["M", "F", "U", "O"]
    },
    "EVENTS": {
        "event_code_vocabulary": ["ICD9", "ICD10", "ICD10CM", "SNOMED", "READ"]
    }
}


def make_frequency_table(df, col):
    """
    Count how many times each value appears in a column.
    This helps researchers understand what codes/values are present.
    """
    freq = (
        df[col]
        .value_counts(dropna=False)
        .reset_index()
    )
    freq.columns = ["value", "count"]
    freq["percentage"] = round(freq["count"] / len(df) * 100, 2)
    return freq


def run(config):
    """
    Step 4: Convention checks and frequency tables.
    For each CDM table:
      - Check categorical variables match their allowed values
      - Build a frequency table showing the distribution of each category
    """
    cdm_path  = config["paths"]["cdm_data"]
    all_convention_results = []
    all_freq_tables        = {}

    for table_name in config["tables_present"]:
        df = read_cdm_table(table_name, cdm_path)
        if df is None:
            continue

        # Convention checks
        conventions = CATEGORICAL_CONVENTIONS.get(table_name, {})
        for col, allowed in conventions.items():
            if col not in df.columns:
                continue
            non_null = df[df[col].notna()]
            n_invalid = (~non_null[col].isin(allowed)).sum()
            all_convention_results.append({
                "table":       table_name,
                "column":      col,
                "allowed":     str(allowed),
                "invalid_n":   int(n_invalid),
                "invalid_pct": round(n_invalid / len(non_null) * 100, 2)
                                if len(non_null) > 0 else 0.0,
                "status":      "FAIL" if n_invalid > 0 else "PASS"
            })

        # Frequency tables for all columns that look categorical
        # (fewer than 100 unique values and not obviously an ID column)
        all_freq_tables[table_name] = {}
        for col in df.columns:
            if "id" in col.lower():
                continue
            n_unique = df[col].nunique()
            if n_unique <= 100:
                all_freq_tables[table_name][col] = make_frequency_table(df, col)

    conventions_df = pd.DataFrame(all_convention_results)
    return {
        "conventions":   conventions_df,
        "freq_tables":   all_freq_tables
    }