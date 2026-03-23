"""
Level 3 — Step 4: Diagnoses / Events
Counts and rates of diagnoses/events over calendar time.
Mirrors: Main_04_diagnoses.R
"""
import pandas as pd
import logging
from src.utils.io import read_cdm_table

logger = logging.getLogger(__name__)


def run(config: dict) -> dict:
    cdm_path = config["paths"]["cdm_data"]
    events = read_cdm_table("EVENTS", cdm_path)

    result = {"available": False, "total_records": 0,
              "by_year": {}, "top_codes": {}, "by_meaning": {}, "by_vocabulary": {}}

    if events is None:
        logger.warning("Step 4: EVENTS table not found")
        return result

    result["available"]     = True
    result["total_records"] = len(events)

    if "start_date_record" in events.columns:
        years = events["start_date_record"].str[:4]
        valid = years[years.str.match(r"^\d{4}$", na=False)]
        result["by_year"] = valid.value_counts().sort_index().to_dict()

    code_col = next((c for c in ["event_code", "code", "icd_code"]
                     if c in events.columns), None)
    if code_col:
        result["top_codes"] = events[code_col].value_counts().head(20).to_dict()

    if "meaning" in events.columns:
        result["by_meaning"] = events["meaning"].value_counts().head(20).to_dict()

    if "event_code_vocabulary" in events.columns:
        result["by_vocabulary"] = events["event_code_vocabulary"].value_counts().to_dict()

    logger.info(f"Step 4: {result['total_records']:,} event records")
    return result
