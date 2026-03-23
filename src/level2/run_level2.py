import logging
from logging import config
from .reporting import build_level2_report

from . import (
    step1_before_birth,
    step2_after_death,
    step3_outside_observation,
    step4_person_integrity,
    step5_visit_before_start,
    step6_visit_after_end,
    step7_visit_person_mismatch,
    step8_parent_child
)

logger = logging.getLogger(__name__)


def run(config: dict) -> dict:
    print("\n" + "=" * 60)
    print("LEVEL 2 — Temporal Characterization")
    print("=" * 60)

    print("\n[Step 1] Events before birth...")
    s1 = step1_before_birth.run(config)

    print("\n[Step 2] Events after death...")
    s2 = step2_after_death.run(config)

    print("\n[Step 3] Outside observation period...")
    s3 = step3_outside_observation.run(config)

    print("\n[Step 4] Person integrity...")
    s4 = step4_person_integrity.run(config)

    print("\n[Step 5] Visit before start...")
    s5 = step5_visit_before_start.run(config)

    print("\n[Step 6] Visit after end...")
    s6 = step6_visit_after_end.run(config)

    print("\n[Step 7] Visit-person mismatch...")
    s7 = step7_visit_person_mismatch.run(config)

    print("\n[Step 8] Parent-child checks...")
    s8 = step8_parent_child.run(config)

    results = {
    "before_birth": s1,
    "after_death": s2,
    "outside_obs": s3,
    "person_integrity": s4,
    "visit_before": s5,
    "visit_after": s6,
    "visit_mismatch": s7,
    "parent_child": s8
    }

    output_path = config["paths"]["output_reports"]
    build_level2_report(results, config)

    return results