"""
Level 3 — Step 1: Study-Source Population
Counts, sex/age distributions, follow-up summary.
Mirrors: Main_01_studysourcepopulation.R
"""
import pandas as pd
import logging
from src.utils.io import read_cdm_table

logger = logging.getLogger(__name__)


def run(config: dict) -> dict:
    cdm_path = config["paths"]["cdm_data"]
    persons  = read_cdm_table("PERSONS", cdm_path)
    obs      = read_cdm_table("OBSERVATION_PERIODS", cdm_path)

    result = {"available": False, "sex_counts": {}, "age_dist": {},
              "followup": {}, "total_persons": 0, "pop_by_year": {}}

    if persons is None:
        logger.warning("Step 1: PERSONS table not found")
        return result

    result["available"]     = True
    result["total_persons"] = len(persons)

    # Sex distribution
    sex_col = next((c for c in ["sex_at_instance_creation", "sex", "gender"]
                    if c in persons.columns), None)
    if sex_col:
        result["sex_counts"] = persons[sex_col].value_counts(dropna=False).to_dict()

    # Age groups using birth date
    birth_col = next((c for c in ["date_of_birth", "birth_date", "birthdate"]
                      if c in persons.columns), None)
    if birth_col:
        persons = persons.copy()
        persons["_year"] = pd.to_numeric(
            persons[birth_col].str[:4], errors="coerce"
        )
        ref = 2023
        persons["_age"] = ref - persons["_year"]
        bins   = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,200]
        labels = [f"{b}-{e-1}" for b,e in zip(bins[:-1], bins[1:])]
        persons["_age_group"] = pd.cut(
            persons["_age"], bins=bins, labels=labels, right=False
        )
        result["age_dist"] = (
            persons["_age_group"].value_counts().sort_index().to_dict()
        )

    # Follow-up via OBSERVATION_PERIODS
    if obs is not None and "op_start_date" in obs.columns and "op_end_date" in obs.columns:
        obs = obs.copy()
        obs["_start"] = pd.to_datetime(obs["op_start_date"], format="%Y%m%d", errors="coerce")
        obs["_end"]   = pd.to_datetime(obs["op_end_date"],   format="%Y%m%d", errors="coerce")
        obs["_days"]  = (obs["_end"] - obs["_start"]).dt.days
        fu = obs["_days"].dropna()
        result["followup"] = {
            "mean_days":         round(float(fu.mean()), 1),
            "median_days":       round(float(fu.median()), 1),
            "min_days":          int(fu.min()),
            "max_days":          int(fu.max()),
            "total_person_years": round(float(fu.sum() / 365.25), 1),
        }
        # Population entering by year
        obs["_syear"] = obs["_start"].dt.year
        result["pop_by_year"] = (
            obs["_syear"].value_counts().sort_index().to_dict()
        )

    logger.info(f"Step 1: {result['total_persons']:,} persons loaded")
    return result
