"""
Level 3 — Step 5: Pregnancy
Counts of pregnancy records stratified by status/type.
Mirrors: Main_05_pregnancy.R
"""
import pandas as pd
import logging
from src.utils.io import read_cdm_table

logger = logging.getLogger(__name__)

PREGNANCY_KEYWORDS = [
    "pregnan", "birth", "delivery", "abortion",
    "miscarriage", "termination", "stillbirth"
]


def run(config: dict) -> dict:
    cdm_path = config["paths"]["cdm_data"]
    result = {"available": False, "source": None,
              "total": 0, "by_type": {}, "by_year": {}}

    for tname in ["SURVEY_ID", "SURVEY_OBSERVATIONS", "EVENTS"]:
        df = read_cdm_table(tname, cdm_path)
        if df is None or "meaning" not in df.columns:
            continue

        pattern = "|".join(PREGNANCY_KEYWORDS)
        mask = df["meaning"].str.lower().str.contains(pattern, na=False)
        preg_df = df[mask].copy()

        if len(preg_df) == 0:
            continue

        result["available"] = True
        result["source"]    = tname
        result["total"]     = len(preg_df)
        result["by_type"]   = preg_df["meaning"].value_counts().to_dict()

        date_col = next(
            (c for c in ["survey_date", "start_date_record"] if c in preg_df.columns),
            None
        )
        if date_col:
            years = preg_df[date_col].str[:4]
            valid = years[years.str.match(r"^\d{4}$", na=False)]
            result["by_year"] = valid.value_counts().sort_index().to_dict()

        logger.info(f"Step 5: {result['total']:,} pregnancy records from {tname}")
        break

    if not result["available"]:
        logger.warning("Step 5: No pregnancy records found")
    return result
