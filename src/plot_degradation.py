
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_FILE = PROJECT_ROOT / "results" / "stress_test_summary.csv"

PLOTS_DIR = PROJECT_ROOT / "results" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# LOAD EXPERIMENT RESULTS
# --------------------------------------------------

def load_results():

    if not RESULTS_FILE.exists():
        raise FileNotFoundError(
            "Experiment summary not found. "
            "Run experiment_runner.py first."
        )

    return pd.read_csv(RESULTS_FILE)


# --------------------------------------------------
# PLOT 1: REVENUE ERROR
# --------------------------------------------------

def plot_revenue_error(df):

    plt.figure(figsize=(10, 6))

    for noise_type in df["Noise_Type"].unique():

        subset = df[df["Noise_Type"] == noise_type]

        plt.plot(
            subset["Noise_Level_Pct"],
            subset["Revenue_Error_Pct_mean"],
            marker="o",
            linewidth=2,
            label=noise_type.title(),
        )

    plt.axhline(
        0,
        linestyle="--",
        linewidth=1,
        color="black",
    )

    plt.title("Revenue Error Under Different Noise Conditions")
    plt.xlabel("Noise Level (%)")
    plt.ylabel("Mean Revenue Error (%)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "revenue_error.png",
        dpi=300,
    )

    plt.close()


# --------------------------------------------------
# PLOT 2: CUSTOMER SEGMENTATION
# --------------------------------------------------

def plot_segmentation_stability(df):

    plt.figure(figsize=(10, 6))

    for noise_type in df["Noise_Type"].unique():

        subset = df[df["Noise_Type"] == noise_type]

        plt.plot(
            subset["Noise_Level_Pct"],
            subset["Segment_Flip_Rate_Pct_mean"],
            marker="s",
            linewidth=2,
            label=noise_type.title(),
        )

    plt.title("Customer Segmentation Stability")
    plt.xlabel("Noise Level (%)")
    plt.ylabel("Mean Segment Flip Rate (%)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "segmentation_stability.png",
        dpi=300,
    )

    plt.close()


# --------------------------------------------------
# PLOT 3: ANOVA P-VALUE
# --------------------------------------------------

def plot_anova_stability(df):

    plt.figure(figsize=(10, 6))

    for noise_type in df["Noise_Type"].unique():

        subset = df[df["Noise_Type"] == noise_type]

        plt.plot(
            subset["Noise_Level_Pct"],
            subset["ANOVA_p_mean"],
            marker="D",
            linewidth=2,
            label=noise_type.title(),
        )

    plt.axhline(
        0.05,
        linestyle="--",
        color="red",
        label="Significance threshold (0.05)",
    )

    plt.title("ANOVA P-Value Under Different Noise Conditions")
    plt.xlabel("Noise Level (%)")
    plt.ylabel("Mean ANOVA P-Value")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "anova_stability.png",
        dpi=300,
    )

    plt.close()


# --------------------------------------------------
# PLOT 4: MISSING DATA
# --------------------------------------------------

def plot_missing_values(df):

    plt.figure(figsize=(10, 6))

    for noise_type in df["Noise_Type"].unique():

        subset = df[df["Noise_Type"] == noise_type]

        plt.plot(
            subset["Noise_Level_Pct"],
            subset["Missing_Percentage_mean"],
            marker="o",
            linewidth=2,
            label=noise_type.title(),
        )

    plt.title("Missing Data Percentage Across Experiments")
    plt.xlabel("Noise Level (%)")
    plt.ylabel("Mean Missing Values (%)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / "missing_data.png",
        dpi=300,
    )

    plt.close()


# --------------------------------------------------
# GENERATE ALL GRAPHS
# --------------------------------------------------

def generate_all_plots():

    df = load_results()

    plot_revenue_error(df)
    plot_segmentation_stability(df)
    plot_anova_stability(df)
    plot_missing_values(df)

    print("\nAll graphs generated successfully!")

    print(f"Saved in: {PLOTS_DIR}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":
    generate_all_plots()
