import pandas as pd
import logging
from src.utils.io import read_cdm_table
from src.utils.validators import check_allowed_values, detect_duplicate_rows
from .step0_metadata import REQUIRED_COLUMNS

logger = logging.getLogger(__name__)

# PERSONS.sex_at_instance_creation must be one of these four values
SEX_ALLOWED = ["M", "F", "U", "O"]


def check_one_table(table_name, df):
    """
    Run all Step 1 formatting checks on a single table.
    Returns a list of result dicts (one per check).
    """
    checks = []

    # Check 1: Are all column names lowercase?
    non_lower = [c for c in df.columns if c != c.lower()]
    checks.append({
        "check":   "All column names lowercase",
        "status":  "FAIL" if non_lower else "PASS",
        "detail":  f"Non-lowercase columns: {non_lower}" if non_lower else "OK"
    })

    # Check 2: Are all required/mandatory columns present?
    required = REQUIRED_COLUMNS.get(table_name, [])
    missing_cols = [c for c in required if c not in df.columns]
    checks.append({
        "check":   "Required columns present",
        "status":  "FAIL" if missing_cols else "PASS",
        "detail":  f"Missing: {missing_cols}" if missing_cols else "OK"
    })

    # Check 3: Duplicate rows
    dupe_result = detect_duplicate_rows(df, table_name)
    checks.append({
        "check":   "No duplicate rows",
        "status":  dupe_result["status"],
        "detail":  (f"{dupe_result['duplicate_rows']} duplicate rows "
                    f"({dupe_result['duplicate_pct']}%)")
                   if dupe_result["duplicate_rows"] > 0 else "OK"
    })

    # Check 4: Sex values (PERSONS table only)
    if table_name == "PERSONS" and "sex_at_instance_creation" in df.columns:
        bad_sex = check_allowed_values(
            df, "sex_at_instance_creation", SEX_ALLOWED, table_name
        )
        checks.append({
            "check":   "Sex values in allowed list (M/F/U/O)",
            "status":  "FAIL" if len(bad_sex) > 0 else "PASS",
            "detail":  (f"{len(bad_sex)} rows with invalid sex values: "
                        f"{bad_sex['sex_at_instance_creation'].unique().tolist()}")
                       if len(bad_sex) > 0 else "OK"
        })

    return checks


def run(config):
    """
    Step 1: Run formatting checks on every CDM table.
    Returns a dict: table_name -> list of check results.
    """
    cdm_path = config["paths"]["cdm_data"]
    all_results = {}

    for table_name in config["tables_present"]:
        df = read_cdm_table(table_name, cdm_path)
        if df is None:
            logger.warning(f"Skipping {table_name} — file not found")
            continue

        checks = check_one_table(table_name, df)
        all_results[table_name] = checks

        n_fail = sum(1 for c in checks if c["status"] == "FAIL")
        logger.info(f"{table_name}: {n_fail}/{len(checks)} checks failed")

    return all_results