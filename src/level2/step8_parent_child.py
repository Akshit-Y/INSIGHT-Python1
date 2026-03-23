import pandas as pd
from src.utils.io import read_cdm_table


def run(config):
    rel = read_cdm_table("PERSON_RELATIONSHIPS", config["paths"]["cdm_data"])
    persons = read_cdm_table("PERSONS", config["paths"]["cdm_data"])

    if rel is None or persons is None:
        return {"available": False}

    df = rel.merge(persons, left_on="person_id", right_on="person_id", how="left")
    df = df.merge(persons, left_on="linked_person_id", right_on="person_id", suffixes=("_parent", "_child"))

    df["parent_birth"] = pd.to_datetime(df["date_of_birth_parent"], format="%Y%m%d", errors="coerce")
    df["child_birth"]  = pd.to_datetime(df["date_of_birth_child"], format="%Y%m%d", errors="coerce")

    df["age_diff"] = (df["child_birth"] - df["parent_birth"]).dt.days / 365

    invalid = df[df["age_diff"] < 12]

    return {
        "available": True,
        "violations": len(invalid),
        "total": len(df)
    }