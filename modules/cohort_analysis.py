"""
cohort_analysis.py — Monthly Cohort Retention & Revenue
Tracks customer cohorts by first-purchase month and their retention.
"""

import pandas as pd
import numpy as np
from config import safe_divide
from modules import visualization as viz


def analyze(clean_df, monthly_df, kpis):
    """Analyze customer cohorts by acquisition month.

    Args:
        clean_df: Cleaned DataFrame.
        monthly_df: Monthly summary DataFrame.
        kpis: Dict of core KPIs.

    Returns:
        dict: {"kpis": [...], "charts": [...], "insights": [...]}
    """
    result = {"kpis": [], "charts": [], "insights": []}

    if clean_df.empty or "customer_id" not in clean_df.columns or "year_month" not in clean_df.columns:
        result["insights"].append("📊 Not enough data for cohort analysis.")
        return result

    # ─── Build cohort data ───────────────────────────────────────────────
    # Find each customer's first purchase month (cohort)
    cohort_map = (
        clean_df.groupby("customer_id")["year_month"]
        .min()
        .reset_index()
        .rename(columns={"year_month": "cohort"})
    )

    df = clean_df.merge(cohort_map, on="customer_id", how="left")

    # Unique months sorted
    all_months = sorted(df["year_month"].unique())
    month_index = {m: i for i, m in enumerate(all_months)}

    # Calculate months since cohort
    df["cohort_index"] = df.apply(
        lambda r: month_index.get(r["year_month"], 0) - month_index.get(r["cohort"], 0),
        axis=1,
    )

    # ─── Retention matrix ────────────────────────────────────────────────
    cohort_data = (
        df.groupby(["cohort", "cohort_index"])["customer_id"]
        .nunique()
        .reset_index()
        .rename(columns={"customer_id": "customers"})
    )

    # Pivot to matrix
    cohort_pivot = cohort_data.pivot_table(
        index="cohort", columns="cohort_index", values="customers", fill_value=0
    )

    # Cohort sizes (month 0)
    cohort_sizes = cohort_pivot[0] if 0 in cohort_pivot.columns else pd.Series(dtype=float)

    # Calculate retention percentages
    retention = cohort_pivot.copy()
    for col in retention.columns:
        retention[col] = retention.apply(
            lambda r: round(safe_divide(r[col], cohort_sizes.get(r.name, 1)) * 100, 1),
            axis=1,
        )

    # ─── KPIs ────────────────────────────────────────────────────────────
    num_cohorts = len(cohort_pivot)

    # Average month-1 retention
    avg_m1_retention = 0.0
    if 1 in retention.columns:
        avg_m1_retention = round(retention[1].mean(), 1)

    result["kpis"] = [
        {"label": "Total Cohorts", "value": str(num_cohorts), "delta": None},
        {"label": "Avg Month-1 Retention", "value": f"{avg_m1_retention}%", "delta": None},
    ]

    # ─── Heatmap ─────────────────────────────────────────────────────────
    if not retention.empty and len(retention.columns) > 1:
        z_values = retention.values.tolist()
        x_labels = [f"M+{int(c)}" for c in retention.columns]
        y_labels = retention.index.tolist()

        result["charts"].append(
            viz.heatmap(
                z_values, x_labels, y_labels,
                title="Cohort Retention Heatmap (%)",
                color_label="Retention %",
            )
        )

    # ─── Cohort Revenue ──────────────────────────────────────────────────
    cohort_revenue = (
        df.groupby("cohort")["revenue"]
        .sum()
        .reset_index()
        .rename(columns={"revenue": "total_revenue"})
        .sort_values("cohort")
    )
    if not cohort_revenue.empty:
        result["charts"].append(
            viz.bar_chart(
                cohort_revenue, x="cohort", y="total_revenue",
                title="Total Revenue by Cohort",
                y_label="Revenue (₹)",
            )
        )

    # ─── Insights ────────────────────────────────────────────────────────
    if avg_m1_retention > 30:
        result["insights"].append(
            f"💪 Average month-1 retention is **{avg_m1_retention}%** — strong customer stickiness."
        )
    elif avg_m1_retention > 15:
        result["insights"].append(
            f"📊 Average month-1 retention is **{avg_m1_retention}%** — moderate retention."
        )
    elif avg_m1_retention > 0:
        result["insights"].append(
            f"⚠️ Average month-1 retention is only **{avg_m1_retention}%** — needs improvement."
        )
    else:
        result["insights"].append(
            "ℹ️ Not enough multi-month data to calculate retention rates."
        )

    if num_cohorts > 0:
        result["insights"].append(
            f"📅 Analyzed **{num_cohorts} monthly cohorts** of customers."
        )

    return result
