
import numpy as np
import pandas as pd
from scipy.stats import f_oneway


# --------------------------------------------------
# CUSTOMER SEGMENTATION
# --------------------------------------------------

def assign_segments(df):
    """
    Assign customers to Low, Medium and High Value
    segments based on their total spending.
    """

    required = ["Customer_ID", "Total_Sales"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    customer_spending = (
        df.groupby("Customer_ID")["Total_Sales"]
        .sum(min_count=1)
        .dropna()
    )

    if len(customer_spending) < 3:
        return pd.Series(dtype="object", name="Segment")

    ranked_spending = customer_spending.rank(method="first")

    segments = pd.qcut(
        ranked_spending,
        q=3,
        labels=["Low Value", "Medium Value", "High Value"],
    )

    segments.index.name = "Customer_ID"
    segments.name = "Segment"

    return segments


# --------------------------------------------------
# SAFE ANOVA CALCULATION
# --------------------------------------------------

def calculate_anova(df):
    """
    Perform One-Way ANOVA on Total_Sales across
    Gen Z, Millennials and Gen X.
    """

    required_groups = [
        "Gen Z",
        "Millennials",
        "Gen X",
    ]

    groups = []

    for group_name in required_groups:

        values = df.loc[
            df["Age_Group"] == group_name,
            "Total_Sales"
        ].dropna()

        groups.append(values)

    valid_groups = [
        group for group in groups
        if len(group) >= 2
    ]

    if len(valid_groups) < 2:
        return np.nan, np.nan

    try:
        result = f_oneway(*valid_groups)

        return float(result.statistic), float(result.pvalue)

    except (ValueError, FloatingPointError):
        return np.nan, np.nan


# --------------------------------------------------
# EVALUATE ONE DATASET
# --------------------------------------------------

def evaluate_pipeline(df, baseline_segments=None):
    """
    Calculate business KPIs and statistical metrics
    for a clean or corrupted dataset.
    """

    required_columns = [
        "Order_ID",
        "Customer_ID",
        "Quantity",
        "Total_Sales",
        "Category",
        "Age_Group",
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # ----------------------------------------------
    # 1. BUSINESS KPIs
    # ----------------------------------------------

    total_revenue = df["Total_Sales"].sum(min_count=1)

    total_orders = df["Order_ID"].nunique()

    total_units = df["Quantity"].sum(min_count=1)

    unique_customers = df["Customer_ID"].nunique()

    total_revenue = (
        float(total_revenue)
        if pd.notna(total_revenue)
        else np.nan
    )

    total_units = (
        float(total_units)
        if pd.notna(total_units)
        else np.nan
    )

    aov = (
        total_revenue / total_orders
        if total_orders > 0 and pd.notna(total_revenue)
        else np.nan
    )

    revenue_per_customer = (
        total_revenue / unique_customers
        if unique_customers > 0 and pd.notna(total_revenue)
        else np.nan
    )

    # ----------------------------------------------
    # 2. CATEGORY ANALYSIS
    # ----------------------------------------------

    category_revenue = (
        df.groupby("Category")["Total_Sales"]
        .sum(min_count=1)
        .dropna()
    )

    top_category = (
        category_revenue.idxmax()
        if not category_revenue.empty
        else "N/A"
    )

    electronics_revenue = category_revenue.get(
        "Electronics", 0.0
    )

    electronics_share = (
        electronics_revenue / total_revenue * 100
        if pd.notna(total_revenue) and total_revenue != 0
        else np.nan
    )

    # ----------------------------------------------
    # 3. CUSTOMER SEGMENTATION STABILITY
    # ----------------------------------------------

    current_segments = assign_segments(df)

    segment_flip_rate = np.nan

    if baseline_segments is not None and not current_segments.empty:

        common_customers = current_segments.index.intersection(
            baseline_segments.index
        )

        if len(common_customers) > 0:

            segment_flip_rate = (
                current_segments.loc[common_customers]
                != baseline_segments.loc[common_customers]
            ).mean() * 100

    # ----------------------------------------------
    # 4. ANOVA
    # ----------------------------------------------

    anova_f, anova_p = calculate_anova(df)

    if pd.notna(anova_p):
        hypothesis_decision = (
            "Reject H0 (Significant)"
            if anova_p < 0.05
            else "Fail to Reject H0"
        )
    else:
        hypothesis_decision = "Not Available"

    # ----------------------------------------------
    # 5. DATA QUALITY
    # ----------------------------------------------

    selected_columns = [
        col for col in [
            "Quantity",
            "Unit_Price",
            "Total_Sales",
            "Category",
            "Age_Group",
            "City",
        ]
        if col in df.columns
    ]

    missing_cells = int(
        df[selected_columns].isna().sum().sum()
    )

    total_selected_cells = (
        len(df) * len(selected_columns)
    )

    missing_percentage = (
        missing_cells / total_selected_cells * 100
        if total_selected_cells > 0
        else 0.0
    )

    # ----------------------------------------------
    # 6. RETURN RESULTS
    # ----------------------------------------------

    return {
        "Total_Rows": len(df),
        "Total_Revenue": total_revenue,
        "Total_Orders": total_orders,
        "Total_Units": total_units,
        "AOV": aov,
        "Unique_Customers": unique_customers,
        "Revenue_Per_Customer": revenue_per_customer,
        "Top_Category": top_category,
        "Electronics_Share_Pct": electronics_share,
        "Segment_Flip_Rate_Pct": segment_flip_rate,
        "ANOVA_F": anova_f,
        "ANOVA_p": anova_p,
        "Hypothesis_Decision": hypothesis_decision,
        "Missing_Cells": missing_cells,
        "Missing_Percentage": missing_percentage,
    }


# --------------------------------------------------
# ERROR COMPARISON
# --------------------------------------------------

def calculate_percentage_error(current, baseline):
    """
    Calculate percentage difference from clean baseline.
    Returns NaN when the baseline is zero or unavailable.
    """

    if pd.isna(current) or pd.isna(baseline) or baseline == 0:
        return np.nan

    return ((current - baseline) / abs(baseline)) * 100


def add_error_metrics(results, baseline_results):
    """
    Add KPI error percentages to evaluation results.
    """

    results = results.copy()

    results["Revenue_Error_Pct"] = calculate_percentage_error(
        results["Total_Revenue"],
        baseline_results["Total_Revenue"],
    )

    results["Units_Error_Pct"] = calculate_percentage_error(
        results["Total_Units"],
        baseline_results["Total_Units"],
    )

    results["AOV_Error_Pct"] = calculate_percentage_error(
        results["AOV"],
        baseline_results["AOV"],
    )

    results["Revenue_Per_Customer_Error_Pct"] = (
        calculate_percentage_error(
            results["Revenue_Per_Customer"],
            baseline_results["Revenue_Per_Customer"],
        )
    )

    return results
