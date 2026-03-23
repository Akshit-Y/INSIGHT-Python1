import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

# ─────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────
N_PERSONS = 500
OUTPUT_PATH = "./data/cdm/"

START_DATE = datetime(1950, 1, 1)
END_DATE   = datetime(2020, 1, 1)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def to_str(d):
    return d.strftime("%Y%m%d")

os.makedirs(OUTPUT_PATH, exist_ok=True)

# ─────────────────────────────────────────────
# PERSONS
# ─────────────────────────────────────────────
persons = []

for pid in range(1, N_PERSONS + 1):
    birth = random_date(START_DATE, datetime(2005,1,1))

    persons.append({
        "person_id": pid,
        "date_of_birth": to_str(birth)
    })

persons_df = pd.DataFrame(persons)

# ─────────────────────────────────────────────
# OBSERVATION PERIODS
# ─────────────────────────────────────────────
obs = []

for _, p in persons_df.iterrows():
    birth = datetime.strptime(p["date_of_birth"], "%Y%m%d")

    op_start = birth + timedelta(days=365 * random.randint(5, 20))
    op_end   = op_start + timedelta(days=365 * random.randint(5, 20))

    obs.append({
        "person_id": p["person_id"],
        "op_start_date": to_str(op_start),
        "op_end_date": to_str(op_end)
    })

obs_df = pd.DataFrame(obs)

# ─────────────────────────────────────────────
# EVENTS
# ─────────────────────────────────────────────
events = []

for _, o in obs_df.iterrows():
    op_start = datetime.strptime(o["op_start_date"], "%Y%m%d")
    op_end   = datetime.strptime(o["op_end_date"], "%Y%m%d")

    n_events = random.randint(1, 5)

    for _ in range(n_events):
        event_date = random_date(op_start, op_end)

        events.append({
            "person_id": o["person_id"],
            "start_date_record": to_str(event_date)
        })

events_df = pd.DataFrame(events)

# ─────────────────────────────────────────────
# VISITS (optional but consistent)
# ─────────────────────────────────────────────
visits = []
visit_id = 1

for _, o in obs_df.iterrows():
    op_start = datetime.strptime(o["op_start_date"], "%Y%m%d")
    op_end   = datetime.strptime(o["op_end_date"], "%Y%m%d")

    for _ in range(random.randint(1,3)):
        start = random_date(op_start, op_end)
        end   = start + timedelta(days=random.randint(0,5))

        visits.append({
            "visit_occurrence_id": visit_id,
            "person_id": o["person_id"],
            "visit_start_date": to_str(start),
            "visit_end_date": to_str(end)
        })
        visit_id += 1

visits_df = pd.DataFrame(visits)

# ─────────────────────────────────────────────
# MEDICINES
# ─────────────────────────────────────────────
meds = []

for _, o in obs_df.iterrows():
    op_start = datetime.strptime(o["op_start_date"], "%Y%m%d")
    op_end   = datetime.strptime(o["op_end_date"], "%Y%m%d")

    for _ in range(random.randint(1,3)):
        d = random_date(op_start, op_end)

        meds.append({
            "person_id": o["person_id"],
            "date_dispensing": to_str(d),
            "quantity": random.randint(1, 30)
        })

meds_df = pd.DataFrame(meds)

# ─────────────────────────────────────────────
# VACCINES
# ─────────────────────────────────────────────
vaccines = []

for _, o in obs_df.iterrows():
    op_start = datetime.strptime(o["op_start_date"], "%Y%m%d")
    op_end   = datetime.strptime(o["op_end_date"], "%Y%m%d")

    if random.random() < 0.5:
        d = random_date(op_start, op_end)

        vaccines.append({
            "person_id": o["person_id"],
            "vx_admin_date": to_str(d)
        })

vaccines_df = pd.DataFrame(vaccines)

# ─────────────────────────────────────────────
# PROCEDURES
# ─────────────────────────────────────────────
procedures = []

for _, o in obs_df.iterrows():
    op_start = datetime.strptime(o["op_start_date"], "%Y%m%d")
    op_end   = datetime.strptime(o["op_end_date"], "%Y%m%d")

    for _ in range(random.randint(0,2)):
        d = random_date(op_start, op_end)

        procedures.append({
            "person_id": o["person_id"],
            "procedure_date": to_str(d)
        })

procedures_df = pd.DataFrame(procedures)

# ─────────────────────────────────────────────
# RELATIONSHIPS (FIXED LOGIC)
# ─────────────────────────────────────────────
relationships = []

persons_df["birth_dt"] = pd.to_datetime(persons_df["date_of_birth"], format="%Y%m%d")

for _ in range(200):
    parent = persons_df.sample(1).iloc[0]
    child  = persons_df.sample(1).iloc[0]

    if parent["birth_dt"] < child["birth_dt"] - pd.Timedelta(days=365*15):
        relationships.append({
            "person_id": parent["person_id"],
            "linked_person_id": child["person_id"]
        })

rel_df = pd.DataFrame(relationships)

# ─────────────────────────────────────────────
# SAVE ALL
# ─────────────────────────────────────────────
persons_df.drop(columns=["birth_dt"], errors="ignore").to_csv(OUTPUT_PATH + "PERSONS.csv", index=False)
obs_df.to_csv(OUTPUT_PATH + "OBSERVATION_PERIODS.csv", index=False)
events_df.to_csv(OUTPUT_PATH + "EVENTS.csv", index=False)
visits_df.to_csv(OUTPUT_PATH + "VISIT_OCCURRENCE.csv", index=False)
meds_df.to_csv(OUTPUT_PATH + "MEDICINES.csv", index=False)
vaccines_df.to_csv(OUTPUT_PATH + "VACCINES.csv", index=False)
procedures_df.to_csv(OUTPUT_PATH + "PROCEDURES.csv", index=False)
rel_df.to_csv(OUTPUT_PATH + "PERSON_RELATIONSHIPS.csv", index=False)

print("✅ Synthetic CDM dataset generated successfully")