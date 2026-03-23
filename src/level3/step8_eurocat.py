"""
Level 3 — Step 8: EUROCAT Indicators
Data quality indicators for congenital anomalies.
Only runs if EUROCAT or SURVEY_OBSERVATIONS table is present.
Mirrors: Main_08_eurocat.R
"""
import pandas as pd
import logging
from src.utils.io import read_cdm_table

logger = logging.getLogger(__name__)


def run(config: dict) -> dict:
    cdm_path = config["paths"]["cdm_data"]
    result = {"available": False, "source": None,
              "total_records": 0, "top_codes": {}, "by_year": {}}

    for tname in ["EUROCAT", "SURVEY_OBSERVATIONS"]:
        df = read_cdm_table(tname, cdm_path)
        if df is None:
            continue
        result["available"]     = True
        result["source"]        = tname
        result["total_records"] = len(df)

        if "meaning" in df.columns:
            result["top_codes"] = df["meaning"].value_counts().head(20).to_dict()

        date_col = next(
            (c for c in ["survey_date", "start_date_record"] if c in df.columns),
            None
        )
        if date_col:
            years = df[date_col].str[:4]
            valid = years[years.str.match(r"^\d{4}$", na=False)]
            result["by_year"] = valid.value_counts().sort_index().to_dict()

        logger.info(f"Step 8: {result['total_records']:,} EUROCAT records from {tname}")
        break

    if not result["available"]:
        logger.warning("Step 8: No EUROCAT table found — step skipped")
    return result
