
from pathlib import Path

import pandas as pd

from noise_injector import inject_noise, INPUT_CSV
from stress_evaluator import (
    assign_segments,
    evaluate_pipeline,
    add_error_metrics,
)


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

DETAILED_RESULTS = RESULTS_DIR / "stress_test_results.csv"
SUMMARY_RESULTS = RESULTS_DIR / "stress_test_summary.csv"


# --------------------------------------------------
# EXPERIMENT SETTINGS
# --------------------------------------------------

NOISE_TYPES = [
    "missing",
    "outlier",
    "label",
    "combined",
]

NOISE_LEVELS = [0.05, 0.15, 0.30]

RANDOM_SEEDS = list(range(10, 20))


# --------------------------------------------------
# RUN EXPERIMENTS
# --------------------------------------------------

def run_experiments():

    # Load clean dataset
    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"Clean dataset not found: {INPUT_CSV}"
        )

    clean_df = pd.read_csv(INPUT_CSV)

    print("\nClean dataset loaded successfully.")
    print(f"Rows: {len(clean_df)}")
    print(f"Columns: {len(clean_df.columns)}")

    # ----------------------------------------------
    # BASELINE EVALUATION
    # ----------------------------------------------

    print("\nCalculating clean baseline...")

    baseline_segments = assign_segments(clean_df)

    baseline_metrics = evaluate_pipeline(
        clean_df,
        baseline_segments,
    )

    baseline_metrics = add_error_metrics(
        baseline_metrics,
        baseline_metrics,
    )

    baseline_metrics.update({
        "Scenario": "Clean_Baseline",
        "Noise_Type": "none",
        "Noise_Level_Pct": 0,
        "Random_Seed": 0,
    })

    all_results = [baseline_metrics]

    # ----------------------------------------------
    # EXPERIMENTAL RUNS
    # ----------------------------------------------

    total_runs = (
        len(NOISE_TYPES)
        * len(NOISE_LEVELS)
        * len(RANDOM_SEEDS)
    )

    run_number = 0

    print(f"\nStarting {total_runs} experimental runs...\n")

    for noise_type in NOISE_TYPES:

        for noise_level in NOISE_LEVELS:

            for seed in RANDOM_SEEDS:

                run_number += 1

                # Inject noise into a fresh copy
                noisy_df = inject_noise(
                    df=clean_df,
                    noise_type=noise_type,
                    noise_level=noise_level,
                    seed=seed,
                )

                # Evaluate corrupted dataset
                metrics = evaluate_pipeline(
                    noisy_df,
                    baseline_segments,
                )

                # Compare against clean baseline
                metrics = add_error_metrics(
                    metrics,
                    baseline_metrics,
                )

                percentage = int(noise_level * 100)

                metrics.update({
                    "Scenario": (
                        f"{noise_type}_{percentage}pct"
                    ),
                    "Noise_Type": noise_type,
                    "Noise_Level_Pct": percentage,
                    "Random_Seed": seed,
                })

                all_results.append(metrics)

                print(
                    f"[{run_number}/{total_runs}] "
                    f"{noise_type} | "
                    f"{percentage}% | "
                    f"Seed {seed}"
                )

    # ----------------------------------------------
    # SAVE DETAILED RESULTS
    # ----------------------------------------------

    results_df = pd.DataFrame(all_results)

    # Keep experiment identification columns first
    identification_columns = [
        "Scenario",
        "Noise_Type",
        "Noise_Level_Pct",
        "Random_Seed",
    ]

    remaining_columns = [
        col for col in results_df.columns
        if col not in identification_columns
    ]

    results_df = results_df[
        identification_columns + remaining_columns
    ]

    results_df.to_csv(
        DETAILED_RESULTS,
        index=False,
    )

    print("\nDetailed results saved:")
    print(DETAILED_RESULTS)

    # ----------------------------------------------
    # CREATE SUMMARY RESULTS
    # ----------------------------------------------

    numeric_metrics = [
        "Total_Revenue",
        "Total_Orders",
        "Total_Units",
        "AOV",
        "Revenue_Per_Customer",
        "Revenue_Error_Pct",
        "Units_Error_Pct",
        "AOV_Error_Pct",
        "Revenue_Per_Customer_Error_Pct",
        "Electronics_Share_Pct",
        "Segment_Flip_Rate_Pct",
        "ANOVA_F",
        "ANOVA_p",
        "Missing_Percentage",
    ]

    summary = (
        results_df[
            results_df["Noise_Type"] != "none"
        ]
        .groupby(
            ["Noise_Type", "Noise_Level_Pct"]
        )[numeric_metrics]
        .agg(["mean", "std"])
        .reset_index()
    )

    # Flatten multi-level column names
    summary.columns = [
        "_".join(
            str(part) for part in column if str(part)
        ).rstrip("_")
        if isinstance(column, tuple)
        else str(column)
        for column in summary.columns
    ]

    summary.to_csv(
        SUMMARY_RESULTS,
        index=False,
    )

    print("\nSummary results saved:")
    print(SUMMARY_RESULTS)

    # ----------------------------------------------
    # DISPLAY SUMMARY
    # ----------------------------------------------

    print("\n========== EXPERIMENT SUMMARY ==========")

    print(
        summary[
            [
                "Noise_Type",
                "Noise_Level_Pct",
                "Revenue_Error_Pct_mean",
                "Segment_Flip_Rate_Pct_mean",
                "Missing_Percentage_mean",
            ]
        ].round(3).to_string(index=False)
    )

    print("\n=========================================")
    print("ALL EXPERIMENTS COMPLETED SUCCESSFULLY!")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":
    run_experiments()
