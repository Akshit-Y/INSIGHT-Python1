from src.utils.io import read_cdm_table


def run(config):
    persons = read_cdm_table("PERSONS", config["paths"]["cdm_data"])
    events  = read_cdm_table("EVENTS", config["paths"]["cdm_data"])

    if persons is None or events is None:
        return {"available": False}

    valid_ids = set(persons["person_id"])
    invalid = events[~events["person_id"].isin(valid_ids)]

    return {
        "available": True,
        "violations": len(invalid),
        "total": len(events)
    }