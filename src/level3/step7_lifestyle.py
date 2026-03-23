"""
Level 3 — Step 7: Health-Seeking Behaviour and Lifestyle Factors
Visit counts, BMI, smoking, alcohol records.
Mirrors: Main_07_lifestyle.R
"""
import pandas as pd
import logging
from src.utils.io import read_cdm_table

logger = logging.getLogger(__name__)

LIFESTYLE_KEYWORDS = ["bmi", "smoking", "alcohol", "physical_activity",
                      "blood_pressure", "cholesterol", "obesity"]


def run(config: dict) -> dict:
    cdm_path = config["paths"]["cdm_data"]
    result = {"visit_by_year": {}, "lifestyle_counts": {},
              "lifestyle_by_year": {}, "visit_total": 0}

    # Visits from VISIT_OCCURRENCE
    visits = read_cdm_table("VISIT_OCCURRENCE", cdm_path)
    if visits is not None and "visit_start_date" in visits.columns:
        result["visit_total"] = len(visits)
        years = visits["visit_start_date"].str[:4]
        valid = years[years.str.match(r"^\d{4}$", na=False)]
        result["visit_by_year"] = valid.value_counts().sort_index().to_dict()

    # Lifestyle from MEDICAL_OBSERVATIONS
    med_obs = read_cdm_table("MEDICAL_OBSERVATIONS", cdm_path)
    if med_obs is not None and "meaning" in med_obs.columns:
        pattern = "|".join(LIFESTYLE_KEYWORDS)
        mask = med_obs["meaning"].str.lower().str.contains(pattern, na=False)
        lifestyle_df = med_obs[mask].copy()
        result["lifestyle_counts"] = (
            lifestyle_df["meaning"].value_counts().head(20).to_dict()
        )
        if "mo_date" in lifestyle_df.columns:
            years = lifestyle_df["mo_date"].str[:4]
            valid = years[years.str.match(r"^\d{4}$", na=False)]
            result["lifestyle_by_year"] = (
                valid.value_counts().sort_index().to_dict()
            )

    logger.info(f"Step 7: {result['visit_total']:,} visits, "
                f"{len(result['lifestyle_counts'])} lifestyle types")
    return result
