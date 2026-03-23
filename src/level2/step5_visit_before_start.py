import pandas as pd
from src.utils.io import read_cdm_table


def run(config):
    visits = read_cdm_table("VISIT_OCCURRENCE", config["paths"]["cdm_data"])
    events = read_cdm_table("EVENTS", config["paths"]["cdm_data"])

    if visits is None or events is None:
        return {"available": False}

    if "visit_occurrence_id" not in events.columns or "visit_occurrence_id" not in visits.columns:
        return {"available": False}

    df = events.merge(visits, on="visit_occurrence_id", how="left")

    df["event_date"] = pd.to_datetime(df["start_date_record"], format="%Y%m%d", errors="coerce")
    df["visit_start"] = pd.to_datetime(df["visit_start_date"], format="%Y%m%d", errors="coerce")

    invalid = df[df["event_date"] < df["visit_start"]]

    return {
        "available": True,
        "violations": len(invalid),
        "total": len(df)
    }