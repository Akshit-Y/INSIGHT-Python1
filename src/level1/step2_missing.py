import pandas as pd
import logging
from src.utils.io import read_cdm_table
from src.utils.validators import compute_missingness

logger = logging.getLogger(__name__)

# Tables that have a date column we can use to break down missingness by year
DATE_COLUMNS_PER_TABLE = {
    "PERSONS":               "date_of_birth",
    "OBSERVATION_PERIODS":   "op_start_date",
    "EVENTS":                "start_date_record",
    "MEDICINES":             "date_dispensing",
    "VACCINES":              "vx_admin_date",
    "PROCEDURES":            "procedure_date",
    "MEDICAL_OBSERVATIONS":  "mo_date",
    "VISIT_OCCURRENCE":      "visit_start_date",
}


def run(config):
    """
    Step 2: Missing data analysis.
    For every CDM table, calculate what percentage of each column is missing.
    Also calculate missingness broken down by calendar year (where possible).
    """
    cdm_path = config["paths"]["cdm_data"]
    overall_list = []
    yearly_list  = []

    for table_name in config["tables_present"]:
        df = read_cdm_table(table_name, cdm_path)
        if df is None:
            continue

        # Overall missingness for this table
        miss_df = compute_missingness(df, table_name)
        overall_list.append(miss_df)

        # Missingness by year (only if this table has a recognizable date column)
        date_col = DATE_COLUMNS_PER_TABLE.get(table_name)
        if date_col and date_col in df.columns:
            # Extract the 4-digit year from YYYYMMDD string
            df = df.copy()
            df["_year"] = df[date_col].str[:4]

            # Only keep rows where year looks valid (4 digits)
            df_valid_year = df[df["_year"].str.match(r"^\d{4}$", na=False)]

            for year_val, group in df_valid_year.groupby("_year"):
                miss_year = compute_missingness(
                    group.drop("_year", axis=1), table_name
                )
                miss_year["year"] = year_val
                yearly_list.append(miss_year)

    overall_df = pd.concat(overall_list, ignore_index=True) if overall_list else pd.DataFrame()
    yearly_df  = pd.concat(yearly_list, ignore_index=True)  if yearly_list  else pd.DataFrame()

    return {
        "overall": overall_df,
        "by_year": yearly_df
    }