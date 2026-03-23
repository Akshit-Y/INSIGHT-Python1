"""
Level 3 — Step 2: Medicines
Counts and rates of medicine use over calendar time.
Mirrors: Main_02_medicines.R
"""
import pandas as pd
import logging
from src.utils.io import read_cdm_table

logger = logging.getLogger(__name__)


def run(config: dict) -> dict:
    cdm_path = config["paths"]["cdm_data"]
    meds = read_cdm_table("MEDICINES", cdm_path)

    result = {"available": False, "total_records": 0,
              "by_year": {}, "top_products": {}, "by_meaning": {}}

    if meds is None:
        logger.warning("Step 2: MEDICINES table not found")
        return result

    result["available"]     = True
    result["total_records"] = len(meds)

    # Records by dispensing year
    if "date_dispensing" in meds.columns:
        years = meds["date_dispensing"].str[:4]
        valid = years[years.str.match(r"^\d{4}$", na=False)]
        result["by_year"] = valid.value_counts().sort_index().to_dict()

    # Top medicinal products
    prod_col = next((c for c in ["medicinal_product_id", "atc_code", "product_id"]
                     if c in meds.columns), None)
    if prod_col:
        result["top_products"] = (
            meds[prod_col].value_counts().head(20).to_dict()
        )

    # By data source (meaning)
    if "meaning" in meds.columns:
        result["by_meaning"] = meds["meaning"].value_counts().to_dict()

    logger.info(f"Step 2: {result['total_records']:,} medicine records")
    return result
