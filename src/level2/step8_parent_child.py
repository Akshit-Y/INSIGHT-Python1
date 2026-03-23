import pandas as pd
from src.utils.io import read_cdm_table


def run(config):
    rel = read_cdm_table("PERSON_RELATIONSHIPS", config["paths"]["cdm_data"])
    persons = read_cdm_table("PERSONS", config["paths"]["cdm_data"])

    if rel is None or persons is None:
        return {"available": False}

    # ── Prepare clean PERSONS subsets ───────────────────
    parent_df = persons[["person_id", "date_of_birth"]].copy()
    parent_df = parent_df.rename(columns={
        "person_id": "parent_id",
        "date_of_birth": "parent_birth"
    })

    child_df = persons[["person_id", "date_of_birth"]].copy()
    child_df = child_df.rename(columns={
        "person_id": "child_id",
        "date_of_birth": "child_birth"
    })

    # ── Merge relationships ─────────────────────────────
    df = rel.copy()

    if "person_id" not in df.columns or "linked_person_id" not in df.columns:
        return {"available": False}

    df = df.rename(columns={
        "person_id": "parent_id",
        "linked_person_id": "child_id"
    })

    df = df.merge(parent_df, on="parent_id", how="left")
    df = df.merge(child_df, on="child_id", how="left")

    # ── Convert dates safely ────────────────────────────
    df["parent_birth"] = pd.to_datetime(df["parent_birth"], format="%Y%m%d", errors="coerce")
    df["child_birth"]  = pd.to_datetime(df["child_birth"], format="%Y%m%d", errors="coerce")

    # ── Compute age difference ──────────────────────────
    df["age_diff"] = (df["child_birth"] - df["parent_birth"]).dt.days / 365

    invalid = df[df["age_diff"] < 12]

    return {
        "available": True,
        "violations": len(invalid),
        "total": len(df)
    }