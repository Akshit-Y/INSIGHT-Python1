from src.utils.io import read_cdm_table


def run(config):
    visits = read_cdm_table("VISIT_OCCURRENCE", config["paths"]["cdm_data"])
    events = read_cdm_table("EVENTS", config["paths"]["cdm_data"])

    if visits is None or events is None:
        return {"available": False}

    df = events.merge(visits, on="visit_occurrence_id", how="left", suffixes=("_event", "_visit"))

    invalid = df[df["person_id_event"] != df["person_id_visit"]]

    return {
        "available": True,
        "violations": len(invalid),
        "total": len(df)
    }