import pandas as pd
from src.utils.io import read_cdm_table


def run(config):
    persons = read_cdm_table("PERSONS", config["paths"]["cdm_data"])
    events  = read_cdm_table("EVENTS", config["paths"]["cdm_data"])

    if persons is None or events is None:
        return {"available": False}

    df = events.merge(persons, on="person_id", how="left")

    df["event_date"] = pd.to_datetime(df["start_date_record"], format="%Y%m%d", errors="coerce")
    df["birth_date"] = pd.to_datetime(df["date_of_birth"], format="%Y%m%d", errors="coerce")

    invalid = df[df["event_date"] < df["birth_date"]]

    return {
        "available": True,
        "violations": len(invalid),
        "total": len(df)
    }