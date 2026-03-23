import logging
import sys
from src.utils.io import load_config
from src.level1.run_level1 import run as run_level1
from src.level2.run_level2 import run as run_level2 
from src.level3.run_level3 import run as run_level3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

if __name__ == "__main__":
    print("INSIGHT — Data Quality Assessment Pipeline")
    print("Starting...\n")

    config = load_config("config/parameters.yml")
    print(f"Study: {config['study']['name']}")
    print(f"CDM data folder: {config['paths']['cdm_data']}")

    run_level1(config)

    run_level2(config)

    run_level3(config)

    print("\nAll done.")
    print("Level 1 → output/Level1_Report.html")
    print("Level 2 → (add report if implemented)")
    print("Level 3 → output/Level3_Report.html")