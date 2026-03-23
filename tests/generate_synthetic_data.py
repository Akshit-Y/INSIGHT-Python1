import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

OUTPUT_DIR = "./data/cdm/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

N_PERSONS = 500
rng = np.random.default_rng(42)


def rand_date(start_year=1950, end_year=2020):
    """Generate a random date string in YYYYMMDD format."""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = rng.integers(0, delta.days)
    d = start + timedelta(days=int(random_days))
    return d.strftime("%Y%m%d")


# ── PERSONS table ──────────────────────────────────────────────────────────────
print("Creating PERSONS table...")

person_ids = [f"P{str(i).zfill(6)}" for i in range(1, N_PERSONS + 1)]
dob_list = [rand_date(1940, 2005) for _ in person_ids]
sex_list = list(rng.choice(["M", "F"], size=N_PERSONS))

persons = pd.DataFrame({
    "person_id": person_ids,
    "sex_at_instance_creation": sex_list,
    "date_of_birth": dob_list
})

# Deliberately inject errors to test Level 1 checks
persons.loc[0, "sex_at_instance_creation"] = "1"    # wrong sex value
persons.loc[1, "sex_at_instance_creation"] = "male"  # wrong sex value
persons.loc[2, "date_of_birth"] = "19001301"         # impossible month 13
persons.loc[3, "date_of_birth"] = ""                  # missing date

persons.to_csv(f"{OUTPUT_DIR}PERSONS.csv", index=False)
print(f"  Saved PERSONS.csv — {len(persons)} rows")


# ── OBSERVATION_PERIODS table ──────────────────────────────────────────────────
print("Creating OBSERVATION_PERIODS table...")

obs_starts = [rand_date(2000, 2010) for _ in person_ids]
obs_ends   = [rand_date(2015, 2023) for _ in person_ids]

obs_periods = pd.DataFrame({
    "person_id": person_ids,
    "op_start_date": obs_starts,
    "op_end_date": obs_ends
})

obs_periods.to_csv(f"{OUTPUT_DIR}OBSERVATION_PERIODS.csv", index=False)
print(f"  Saved OBSERVATION_PERIODS.csv — {len(obs_periods)} rows")


# ── EVENTS table ───────────────────────────────────────────────────────────────
print("Creating EVENTS table...")

event_meanings = [
    "emergency_room_diagnosis",
    "hospitalisation_primary",
    "hospitalisation_secondary",
    "access_to_mental_health_service_primary",
    "exemption"
]

n_events = 2000
events = pd.DataFrame({
    "person_id": list(rng.choice(person_ids, size=n_events)),
    "start_date_record": [rand_date(1990, 2023) for _ in range(n_events)],
    "end_date_record":   [rand_date(2000, 2023) for _ in range(n_events)],
    "event_code":        [f"ICD{rng.integers(100, 999)}" for _ in range(n_events)],
    "event_code_vocabulary": "ICD10",
    "meaning": list(rng.choice(event_meanings, size=n_events))
})

# Inject date errors for testing
events.loc[0:4, "start_date_record"] = "19880101"   # before 1995 cutoff
events.loc[5:6, "start_date_record"] = "20991231"   # future date

events.to_csv(f"{OUTPUT_DIR}EVENTS.csv", index=False)
print(f"  Saved EVENTS.csv — {len(events)} rows")


# ── MEDICINES table ────────────────────────────────────────────────────────────
print("Creating MEDICINES table...")

n_meds = 1500
medicines = pd.DataFrame({
    "person_id": list(rng.choice(person_ids, size=n_meds)),
    "date_dispensing":   [rand_date(2000, 2023) for _ in range(n_meds)],
    "date_prescription": [rand_date(2000, 2023) for _ in range(n_meds)],
    "medicinal_product_id": [f"ATC{rng.integers(1000, 9999)}" for _ in range(n_meds)],
    "meaning": list(rng.choice(
        ["dispensing_in_community_pharmacy",
         "dispensing_in_hospital_pharmacy_unspecified"],
        size=n_meds
    ))
})

# Inject some missing values
medicines.loc[0:9, "date_dispensing"] = ""
medicines.loc[10:14, "medicinal_product_id"] = ""

medicines.to_csv(f"{OUTPUT_DIR}MEDICINES.csv", index=False)
print(f"  Saved MEDICINES.csv — {len(medicines)} rows")


# ── VACCINES table ─────────────────────────────────────────────────────────────
print("Creating VACCINES table...")

n_vax = 400
vaccines = pd.DataFrame({
    "person_id":    list(rng.choice(person_ids, size=n_vax)),
    "vx_admin_date":  [rand_date(2000, 2023) for _ in range(n_vax)],
    "vx_record_date": [rand_date(2000, 2023) for _ in range(n_vax)],
    "vx_type": list(rng.choice(["COVID19", "INFLUENZA", "MMR", "HEPATITIS_B"], size=n_vax)),
    "meaning": "administration_of_vaccine_unspecified"
})

vaccines.to_csv(f"{OUTPUT_DIR}VACCINES.csv", index=False)
print(f"  Saved VACCINES.csv — {len(vaccines)} rows")


# ── PROCEDURES table ───────────────────────────────────────────────────────────
print("Creating PROCEDURES table...")

n_proc = 800
procedures = pd.DataFrame({
    "person_id":      list(rng.choice(person_ids, size=n_proc)),
    "procedure_date": [rand_date(2000, 2023) for _ in range(n_proc)],
    "procedure_code": [f"PROC{rng.integers(100, 999)}" for _ in range(n_proc)],
    "meaning": list(rng.choice(
        ["italian_outpatient", "procedure_during_hospitalisation"], size=n_proc
    ))
})

procedures.to_csv(f"{OUTPUT_DIR}PROCEDURES.csv", index=False)
print(f"  Saved PROCEDURES.csv — {len(procedures)} rows")


# ── MEDICAL_OBSERVATIONS table ─────────────────────────────────────────────────
print("Creating MEDICAL_OBSERVATIONS table...")

n_obs = 600
medical_obs = pd.DataFrame({
    "person_id": list(rng.choice(person_ids, size=n_obs)),
    "mo_date":   [rand_date(2000, 2023) for _ in range(n_obs)],
    "mo_code":   [f"OBS{rng.integers(10, 99)}" for _ in range(n_obs)],
    "meaning":   list(rng.choice(
        ["measure_during_hospitalisation", "bmi", "blood_pressure"], size=n_obs
    ))
})

medical_obs.to_csv(f"{OUTPUT_DIR}MEDICAL_OBSERVATIONS.csv", index=False)
print(f"  Saved MEDICAL_OBSERVATIONS.csv — {len(medical_obs)} rows")


# ── VISIT_OCCURRENCE table ─────────────────────────────────────────────────────
print("Creating VISIT_OCCURRENCE table...")

n_visits = 700
visits = pd.DataFrame({
    "person_id":       list(rng.choice(person_ids, size=n_visits)),
    "visit_start_date": [rand_date(2000, 2023) for _ in range(n_visits)],
    "visit_end_date":   [rand_date(2000, 2023) for _ in range(n_visits)],
    "visit_occurrence_id": [f"V{str(i).zfill(6)}" for i in range(n_visits)]
})

visits.to_csv(f"{OUTPUT_DIR}VISIT_OCCURRENCE.csv", index=False)
print(f"  Saved VISIT_OCCURRENCE.csv — {len(visits)} rows")


# ── PERSON_RELATIONSHIPS table ─────────────────────────────────────────────────
print("Creating PERSON_RELATIONSHIPS table...")

n_rel = 200
rels = pd.DataFrame({
    "person_id":        list(rng.choice(person_ids, size=n_rel)),
    "linked_person_id": list(rng.choice(person_ids, size=n_rel)),
    "relationship_type": "mother_child",
    "date_of_birth_child": [rand_date(2000, 2020) for _ in range(n_rel)]
})

rels.to_csv(f"{OUTPUT_DIR}PERSON_RELATIONSHIPS.csv", index=False)
print(f"  Saved PERSON_RELATIONSHIPS.csv — {len(rels)} rows")


# ── CDM_SOURCE table ───────────────────────────────────────────────────────────
print("Creating CDM_SOURCE table...")

cdm_source = pd.DataFrame({
    "cdm_source_name": ["TestHospital_DB"],
    "cdm_version":     ["2.2"],
    "cdm_holder":      ["Test DAP"],
    "source_release_date": ["20230101"]
})

cdm_source.to_csv(f"{OUTPUT_DIR}CDM_SOURCE.csv", index=False)
print(f"  Saved CDM_SOURCE.csv")


# ── INSTANCE table ─────────────────────────────────────────────────────────────
print("Creating INSTANCE table...")

instance = pd.DataFrame({
    "instance_id":          ["INST001"],
    "instance_description": ["Test CDM instance for INSIGHT"],
    "date_creation":        ["20230901"]
})

instance.to_csv(f"{OUTPUT_DIR}INSTANCE.csv", index=False)
print(f"  Saved INSTANCE.csv")


# ── METADATA table ─────────────────────────────────────────────────────────────
print("Creating METADATA table...")

metadata_rows = [
    ("PERSONS",              "person_id",                  "Y", "varchar"),
    ("PERSONS",              "sex_at_instance_creation",   "Y", "varchar"),
    ("PERSONS",              "date_of_birth",              "Y", "date"),
    ("OBSERVATION_PERIODS",  "person_id",                  "Y", "varchar"),
    ("OBSERVATION_PERIODS",  "op_start_date",              "Y", "date"),
    ("OBSERVATION_PERIODS",  "op_end_date",                "Y", "date"),
    ("EVENTS",               "person_id",                  "Y", "varchar"),
    ("EVENTS",               "start_date_record",          "Y", "date"),
    ("EVENTS",               "end_date_record",            "N", "date"),
    ("EVENTS",               "event_code",                 "Y", "varchar"),
    ("EVENTS",               "event_code_vocabulary",      "Y", "varchar"),
    ("EVENTS",               "meaning",                    "Y", "varchar"),
    ("MEDICINES",            "person_id",                  "Y", "varchar"),
    ("MEDICINES",            "date_dispensing",            "Y", "date"),
    ("MEDICINES",            "medicinal_product_id",       "Y", "varchar"),
    ("MEDICINES",            "meaning",                    "Y", "varchar"),
    ("VACCINES",             "person_id",                  "Y", "varchar"),
    ("VACCINES",             "vx_admin_date",              "Y", "date"),
    ("VACCINES",             "vx_record_date",             "Y", "date"),
    ("VACCINES",             "vx_type",                    "Y", "varchar"),
    ("PROCEDURES",           "person_id",                  "Y", "varchar"),
    ("PROCEDURES",           "procedure_date",             "Y", "date"),
    ("PROCEDURES",           "procedure_code",             "Y", "varchar"),
    ("MEDICAL_OBSERVATIONS", "person_id",                  "Y", "varchar"),
    ("MEDICAL_OBSERVATIONS", "mo_date",                    "Y", "date"),
    ("MEDICAL_OBSERVATIONS", "mo_code",                    "Y", "varchar"),
]

metadata = pd.DataFrame(
    metadata_rows,
    columns=["table_name", "variable_name", "mandatory", "format"]
)

metadata.to_csv(f"{OUTPUT_DIR}METADATA.csv", index=False)
print(f"  Saved METADATA.csv — {len(metadata)} rows")


# ── PRODUCTS table ─────────────────────────────────────────────────────────────
print("Creating PRODUCTS table...")

products = pd.DataFrame({
    "medicinal_product_id": [f"ATC{i}" for i in range(1000, 1020)],
    "product_name": [f"Drug_{i}" for i in range(20)],
    "atc_code": [f"A0{i}B" for i in range(20)]
})

products.to_csv(f"{OUTPUT_DIR}PRODUCTS.csv", index=False)
print(f"  Saved PRODUCTS.csv")


print("\nDone! All synthetic CDM tables created in ./data/cdm/")
print(f"Total tables created: 12")