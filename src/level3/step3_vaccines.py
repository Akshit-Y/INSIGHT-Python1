"""
Level 3 — Step 3: Vaccines
Counts and rates of vaccine exposure over calendar time.
Mirrors: Main_03_vaccines.R
"""
import pandas as pd
import logging
from src.utils.io import read_cdm_table

logger = logging.getLogger(__name__)


def run(config: dict) -> dict:
    cdm_path = config["paths"]["cdm_data"]
    vax = read_cdm_table("VACCINES", cdm_path)

    result = {"available": False, "total_records": 0,
              "by_year": {}, "by_type": {}, "by_meaning": {}}

    if vax is None:
        logger.warning("Step 3: VACCINES table not found")
        return result

    result["available"]     = True
    result["total_records"] = len(vax)

    if "vx_admin_date" in vax.columns:
        years = vax["vx_admin_date"].str[:4]
        valid = years[years.str.match(r"^\d{4}$", na=False)]
        result["by_year"] = valid.value_counts().sort_index().to_dict()

    type_col = next((c for c in ["vx_type", "vaccine_type"] if c in vax.columns), None)
    if type_col:
        result["by_type"] = vax[type_col].value_counts().to_dict()

    if "meaning" in vax.columns:
        result["by_meaning"] = vax["meaning"].value_counts().to_dict()

    logger.info(f"Step 3: {result['total_records']:,} vaccine records")
    return result
