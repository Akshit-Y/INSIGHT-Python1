"""
Level 3 — Step 6: Populations of Interest
Sub-group analysis e.g. females of reproductive age.
Mirrors: Main_06_populations_of_interest.R
"""
import pandas as pd
import logging
from src.utils.io import read_cdm_table

logger = logging.getLogger(__name__)


def run(config: dict) -> dict:
    cdm_path = config["paths"]["cdm_data"]
    persons  = read_cdm_table("PERSONS", cdm_path)
    result   = {"available": False, "subgroups": []}

    if persons is None:
        logger.warning("Step 6: PERSONS table not found")
        return result

    result["available"]   = True
    total                 = len(persons)

    birth_col = next((c for c in ["date_of_birth", "birth_date"]
                      if c in persons.columns), None)
    sex_col   = next((c for c in ["sex_at_instance_creation", "sex", "gender"]
                      if c in persons.columns), None)

    if birth_col and sex_col:
        persons = persons.copy()
        persons["_age"] = 2023 - pd.to_numeric(
            persons[birth_col].str[:4], errors="coerce"
        )
        # Females of reproductive age (15-49) — key for pregnancy studies
        female_repro = persons[
            persons[sex_col].str.upper().isin(["F", "FEMALE"]) &
            persons["_age"].between(15, 49)
        ]
        result["subgroups"].append({
            "name":  "Females aged 15–49 (reproductive age)",
            "count": len(female_repro),
            "pct":   round(100 * len(female_repro) / max(total, 1), 1),
        })

        # Elderly (65+)
        elderly = persons[persons["_age"] >= 65]
        result["subgroups"].append({
            "name":  "Persons aged 65+",
            "count": len(elderly),
            "pct":   round(100 * len(elderly) / max(total, 1), 1),
        })

        # Children (0-17)
        children = persons[persons["_age"].between(0, 17)]
        result["subgroups"].append({
            "name":  "Children aged 0–17",
            "count": len(children),
            "pct":   round(100 * len(children) / max(total, 1), 1),
        })

    # Subpopulations by data provenance (meaning column in OBS_PERIODS)
    obs = read_cdm_table("OBSERVATION_PERIODS", cdm_path)
    if obs is not None and "meaning" in obs.columns:
        result["by_provenance"] = obs["meaning"].value_counts().to_dict()
    else:
        result["by_provenance"] = {}

    logger.info(f"Step 6: {len(result['subgroups'])} sub-groups defined")
    return result
