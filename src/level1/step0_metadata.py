import os
import pandas as pd
import logging
from src.utils.io import read_cdm_table

logger = logging.getLogger(__name__)

# These are the minimum required columns for each table.
REQUIRED_COLUMNS = {
    "PERSONS":               ["person_id", "sex_at_instance_creation", "date_of_birth"],
    "OBSERVATION_PERIODS":   ["person_id", "op_start_date", "op_end_date"],
    "EVENTS":                ["person_id", "start_date_record", "event_code",
                               "event_code_vocabulary", "meaning"],
    "MEDICINES":             ["person_id", "date_dispensing",
                               "medicinal_product_id", "meaning"],
    "VACCINES":              ["person_id", "vx_admin_date",
                               "vx_record_date", "vx_type"],
    "PROCEDURES":            ["person_id", "procedure_date",
                               "procedure_code", "meaning"],
    "MEDICAL_OBSERVATIONS":  ["person_id", "mo_date", "mo_code"],
    "VISIT_OCCURRENCE":      ["person_id", "visit_start_date", "visit_end_date"],
    "PERSON_RELATIONSHIPS":  ["person_id", "linked_person_id", "relationship_type"],
    "CDM_SOURCE":            ["cdm_source_name", "cdm_version"],
    "INSTANCE":              ["instance_id", "instance_description"],
    "METADATA":              ["table_name", "variable_name", "mandatory"],
    "PRODUCTS":              ["medicinal_product_id"],
}


def run(config):
    """
    Step 0: Check that all expected CDM table files exist on disk,
    and that the mandatory METADATA table is present.
    This is the very first gate — nothing else can run if files are missing.
    """
    cdm_path = config["paths"]["cdm_data"]
    all_tables = config["tables_present"] + config.get("tables_optional", [])

    results = []
    for table_name in all_tables:
        file_path = os.path.join(cdm_path, f"{table_name}.csv")
        is_present = os.path.exists(file_path)
        is_optional = table_name in config.get("tables_optional", [])
        status = "PASS" if is_present else ("WARN" if is_optional else "FAIL")

        results.append({
            "table":       table_name,
            "file_path":   file_path,
            "present":     "Yes" if is_present else "No",
            "mandatory":   "No" if is_optional else "Yes",
            "status":      status
        })

    results_df = pd.DataFrame(results)
    n_missing_mandatory = (
        (results_df["mandatory"] == "Yes") & (results_df["present"] == "No")
    ).sum()

    return {
        "results_df":          results_df,
        "n_missing_mandatory": int(n_missing_mandatory),
        "metadata_present":    os.path.exists(
            os.path.join(cdm_path, "METADATA.csv")
        ),
        "overall_status":      "FAIL" if n_missing_mandatory > 0 else "PASS"
    }