from src.utils.io import read_cdm_table


def run(config):
    visits = read_cdm_table("VISIT_OCCURRENCE", config["paths"]["cdm_data"])
    events = read_cdm_table("EVENTS", config["paths"]["cdm_data"])

    if visits is None or events is None:
        return {"available": False}

    if "visit_occurrence_id" not in events.columns or "visit_occurrence_id" not in visits.columns:
        return {
            "available": False,
            "reason": "visit_occurrence_id not present"
        }

    df = events.merge(
        visits,
        on="visit_occurrence_id",
        how="left",
        suffixes=("_event", "_visit")
    )

    if "person_id_event" not in df.columns or "person_id_visit" not in df.columns:
        return {
            "available": False,
            "reason": "person_id columns missing after merge"
        }

    invalid = df[df["person_id_event"] != df["person_id_visit"]]

    return {
        "available": True,
        "violations": len(invalid),
        "total": len(df)
    }