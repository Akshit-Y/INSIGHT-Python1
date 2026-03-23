import re
import pandas as pd
from datetime import datetime


def is_valid_date_format(date_str):
    """
    Check if a string is exactly 8 digits (YYYYMMDD format).
    Example: "20230115" is valid. "2023-01-15" is not.
    """
    if pd.isna(date_str) or date_str == "":
        return False
    return bool(re.match(r"^\d{8}$", str(date_str).strip()))


def parse_cdm_date(date_str):
    """
    Convert a YYYYMMDD string into a Python datetime object.
    Returns None if the string is invalid or unparseable.
    """
    try:
        return datetime.strptime(str(date_str).strip(), "%Y%m%d")
    except (ValueError, TypeError):
        return None


def validate_date_value(date_str, start_year=1995):
    """
    Given a date string, check three things:
    1. Is the format correct (8 digits)?
    2. Is the year before the allowed start year?
    3. Is the date in the future?

    Returns a dictionary with True/False for each issue type.
    """
    result = {
        "error_format": False,
        "error_year": False,
        "future_date": False
    }

    # First check format
    if not is_valid_date_format(date_str):
        result["error_format"] = True
        return result

    # Try to extract year, month, day
    s = str(date_str).strip()
    year  = int(s[0:4])
    month = int(s[4:6])
    day   = int(s[6:8])

    # Check month and day are in sensible range
    if not (1 <= month <= 12) or not (1 <= day <= 31):
        result["error_format"] = True
        return result

    # Check if year is before allowed start
    if year < start_year:
        result["error_year"] = True

    # Check if date is in the future
    parsed = parse_cdm_date(date_str)
    if parsed and parsed > datetime.today():
        result["future_date"] = True

    return result


def compute_missingness(df, table_name):
    """
    For every column in a DataFrame, count how many values are missing (NaN).
    Returns a summary DataFrame with one row per column.
    """
    rows = []
    total = len(df)

    for col in df.columns:
        n_missing = df[col].isna().sum()
        pct = round((n_missing / total * 100), 2) if total > 0 else 0.0
        rows.append({
            "table":        table_name,
            "variable":     col,
            "total_rows":   total,
            "missing_n":    int(n_missing),
            "missing_pct":  pct
        })

    return pd.DataFrame(rows)


def detect_duplicate_rows(df, table_name):
    """
    Count exact duplicate rows (all columns identical).
    Returns a summary dictionary.
    """
    total = len(df)
    n_dupes = int(df.duplicated().sum())
    return {
        "table":          table_name,
        "total_rows":     total,
        "duplicate_rows": n_dupes,
        "duplicate_pct":  round(n_dupes / total * 100, 2) if total > 0 else 0.0,
        "status":         "FAIL" if n_dupes > 0 else "PASS"
    }


def check_allowed_values(df, column, allowed_values, table_name):
    """
    Find rows where a column's value is not in the list of allowed values.
    Ignores NaN/missing values (those are caught by missingness check).
    Returns a DataFrame of the flagged rows.
    """
    if column not in df.columns:
        return pd.DataFrame()

    # Only look at non-null values
    non_null = df[df[column].notna()].copy()
    bad_mask = ~non_null[column].isin(allowed_values)
    flagged = non_null[bad_mask][[column]].copy()
    flagged["table"]  = table_name
    flagged["column"] = column
    flagged["issue"]  = "value_not_in_allowed_list"
    return flagged.reset_index(drop=True)