
from pathlib import Path

import numpy as np
import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_CSV = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cleaned_apexplanet_sales_2026.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "corrupted"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Columns selected for controlled corruption
NUMERIC_COLUMNS = [
    "Quantity",
    "Unit_Price",
    "Total_Sales",
]

CATEGORICAL_COLUMNS = [
    "Category",
    "Age_Group",
    "City",
]


# --------------------------------------------------
# NOISE INJECTION FUNCTION
# --------------------------------------------------

def inject_noise(
    df,
    noise_type,
    noise_level,
    seed=42,
    outlier_multiplier=5.0,
):
    """
    Introduces controlled errors into a copy of the dataset.

    noise_type:
        missing  - randomly replaces values with NaN
        outlier  - introduces extreme numerical values
        label    - changes categorical labels
        combined - applies all three types

    noise_level:
        A fraction between 0 and 1.
        For each eligible column, this is the
        approximate percentage of rows affected.
    """

    if not 0 <= noise_level <= 1:
        raise ValueError("noise_level must be between 0 and 1.")

    if noise_type not in ["missing", "outlier", "label", "combined"]:
        raise ValueError("Invalid noise_type.")

    if outlier_multiplier <= 1:
        raise ValueError("outlier_multiplier must be greater than 1.")

    rng = np.random.default_rng(seed)
    corrupted = df.copy()

    numeric_cols = [
        col for col in NUMERIC_COLUMNS
        if col in corrupted.columns
    ]

    # Convert numeric columns to float so decimal outliers can be stored
    for col in numeric_cols:
        corrupted[col] = pd.to_numeric(
            corrupted[col], errors="coerce"
        ).astype(float)

    categorical_cols = [
        col for col in CATEGORICAL_COLUMNS
        if col in corrupted.columns
    ]

    n_rows = len(corrupted)
    n_corrupt = int(n_rows * noise_level)

    if n_rows == 0 or n_corrupt == 0:
        return corrupted

    # ----------------------------------------------
    # 1. MISSING VALUE INJECTION
    # ----------------------------------------------

    if noise_type in ["missing", "combined"]:

        for col in numeric_cols + categorical_cols:

            valid_indices = corrupted.index[
                corrupted[col].notna()
            ].to_numpy()

            k = min(n_corrupt, len(valid_indices))

            if k == 0:
                continue

            selected_indices = rng.choice(
                valid_indices,
                size=k,
                replace=False,
            )

            corrupted.loc[selected_indices, col] = np.nan

    # ----------------------------------------------
    # 2. NUMERICAL OUTLIER INJECTION
    # ----------------------------------------------

    if noise_type in ["outlier", "combined"]:

        for col in numeric_cols:

            valid_indices = corrupted.index[
                corrupted[col].notna()
            ].to_numpy()

            k = min(n_corrupt, len(valid_indices))

            if k == 0:
                continue

            selected_indices = rng.choice(
                valid_indices,
                size=k,
                replace=False,
            )

            # Randomly create unusually high or low values
            factors = rng.choice(
                [outlier_multiplier, 1 / outlier_multiplier],
                size=k,
            )

            corrupted.loc[selected_indices, col] = (
                corrupted.loc[selected_indices, col].to_numpy()
                * factors
            )

    # ----------------------------------------------
    # 3. CATEGORICAL LABEL ERRORS
    # ----------------------------------------------

    if noise_type in ["label", "combined"]:

        for col in categorical_cols:

            valid_indices = corrupted.index[
                corrupted[col].notna()
            ].to_numpy()

            unique_values = corrupted[col].dropna().unique()

            if len(unique_values) < 2:
                continue

            k = min(n_corrupt, len(valid_indices))

            if k == 0:
                continue

            selected_indices = rng.choice(
                valid_indices,
                size=k,
                replace=False,
            )

            for idx in selected_indices:

                current_value = corrupted.at[idx, col]

                alternatives = [
                    value for value in unique_values
                    if value != current_value
                ]

                corrupted.at[idx, col] = rng.choice(alternatives)

    return corrupted


# --------------------------------------------------
# GENERATE CORRUPTED DATASETS
# --------------------------------------------------

def generate_datasets():

    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {INPUT_CSV}"
        )

    clean_df = pd.read_csv(INPUT_CSV)

    # Save the original clean baseline
    baseline_path = OUTPUT_DIR / "baseline_0pct.csv"

    clean_df.to_csv(
        baseline_path,
        index=False,
    )

    print(f"[OK] Saved baseline: {baseline_path.name}")

    noise_types = [
        "missing",
        "outlier",
        "label",
        "combined",
    ]

    noise_levels = [0.05, 0.15, 0.30]

    for noise_type in noise_types:

        for level in noise_levels:

            percentage = int(level * 100)

            noisy_df = inject_noise(
                df=clean_df,
                noise_type=noise_type,
                noise_level=level,
                seed=42,
            )

            filename = f"{noise_type}_{percentage}pct.csv"

            output_path = OUTPUT_DIR / filename

            noisy_df.to_csv(
                output_path,
                index=False,
            )

            print(f"[OK] Generated: {filename}")

    print("\nAll corrupted datasets generated successfully!")
    print(f"Files saved in: {OUTPUT_DIR}")


# --------------------------------------------------
# RUN SCRIPT
# --------------------------------------------------

if __name__ == "__main__":
    generate_datasets()
