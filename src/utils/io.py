import os
import yaml
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def load_config(config_path="config/parameters.yml"):
    """Read the YAML config file and return it as a Python dictionary."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def read_cdm_table(table_name, cdm_path):
    """
    Read one CDM table (CSV file) from disk.
    - Everything is loaded as text (dtype=str) because dates are stored
      as YYYYMMDD strings, not real date objects.
    - Column names are lowercased to match CDM convention.
    - Returns None if the file doesn't exist.
    """
    file_path = os.path.join(cdm_path, f"{table_name}.csv")

    if not os.path.exists(file_path):
        logger.warning(f"Table file not found: {file_path}")
        return None

    df = pd.read_csv(
        file_path,
        dtype=str,
        keep_default_na=False,
        na_values=["", "NA", "NULL", "null", "NaN"]
    )

    # Enforce lowercase column names
    df.columns = [col.lower().strip() for col in df.columns]

    logger.info(f"Read {table_name}: {len(df):,} rows, {len(df.columns)} columns")
    return df


def save_csv(df, output_path, filename):
    """Save a DataFrame as CSV to the output folder."""
    os.makedirs(output_path, exist_ok=True)
    full_path = os.path.join(output_path, filename)
    df.to_csv(full_path, index=False)
    logger.info(f"Saved CSV: {full_path}")
    return full_path