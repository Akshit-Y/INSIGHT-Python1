import pandas as pd
from src.utils.io import read_cdm_table


def run(config):
    obs    = read_cdm_table("OBSERVATION_PERIODS", config["paths"]["cdm_data"])
    events = read_cdm_table("EVENTS", config["paths"]["cdm_data"])

    if obs is None or events is None:
        return {"available": False}

    df = events.merge(obs, on="person_id", how="left")

    df["event_date"] = pd.to_datetime(df["start_date_record"], format="%Y%m%d", errors="coerce")
    df["start"] = pd.to_datetime(df["op_start_date"], format="%Y%m%d", errors="coerce")
    df["end"]   = pd.to_datetime(df["op_end_date"], format="%Y%m%d", errors="coerce")

    invalid = df[(df["event_date"] < df["start"]) | (df["event_date"] > df["end"])]

    return {
        "available": True,
        "violations": len(invalid),
        "total": len(df)
    }