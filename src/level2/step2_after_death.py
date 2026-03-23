import pandas as pd
from src.utils.io import read_cdm_table


def run(config):
    persons = read_cdm_table("PERSONS", config["paths"]["cdm_data"])
    events  = read_cdm_table("EVENTS", config["paths"]["cdm_data"])

    if persons is None or events is None or "date_of_death" not in persons.columns:
        return {"available": False}

    df = events.merge(persons, on="person_id", how="left")

    df["event_date"] = pd.to_datetime(df["start_date_record"], format="%Y%m%d", errors="coerce")
    df["death_date"] = pd.to_datetime(df["date_of_death"], format="%Y%m%d", errors="coerce")

    invalid = df[df["event_date"] > df["death_date"]]

    return {
        "available": True,
        "violations": len(invalid),
        "total": len(df)
    }