"""
growth_quality.py — Growth Quality Diagnostics
Analyzes new vs repeat customers, revenue concentration, growth quality.
"""

import pandas as pd
from config import safe_divide, safe_pct_change
from modules import visualization as viz


def analyze(clean_df, monthly_df, kpis):
    """Analyze growth quality metrics.

    Args:
        clean_df: Cleaned DataFrame.
        monthly_df: Monthly summary DataFrame.
        kpis: Dict of core KPIs from kpi_engine.

    Returns:
        dict: {"kpis": [...], "charts": [...], "insights": [...]}
    """
    result = {"kpis": [], "charts": [], "insights": []}

    if clean_df.empty or monthly_df.empty:
        result["insights"].append("📊 Not enough data to analyze growth quality.")
        return result

    # ─── New vs Repeat Customer Analysis ─────────────────────────────────
    customer_first_month = (
        clean_df.groupby("customer_id")["year_month"]
        .min()
        .reset_index()
        .rename(columns={"year_month": "first_month"})
    )
    merged = clean_df.merge(customer_first_month, on="customer_id", how="left")
    merged["customer_type"] = merged.apply(
        lambda r: "New" if r["year_month"] == r["first_month"] else "Repeat",
        axis=1,
    )

    # Monthly new vs repeat
    monthly_type = (
        merged.groupby(["year_month", "customer_type"])
        .agg({"revenue": "sum", "customer_id": "nunique"})
        .reset_index()
        .rename(columns={"revenue": "total_revenue", "customer_id": "customers"})
    )

    # KPIs
    total_customers = kpis.get("unique_customers", 0)
    new_count = int(merged[merged["customer_type"] == "New"]["customer_id"].nunique())
    repeat_count = int(merged[merged["customer_type"] == "Repeat"]["customer_id"].nunique())
    repeat_rate = round(safe_divide(repeat_count, total_customers) * 100, 1)

    new_revenue = merged[merged["customer_type"] == "New"]["revenue"].sum()
    repeat_revenue = merged[merged["customer_type"] == "Repeat"]["revenue"].sum()
    total_rev = new_revenue + repeat_revenue
    repeat_revenue_share = round(safe_divide(repeat_revenue, total_rev) * 100, 1)

    result["kpis"] = [
        {"label": "Repeat Customer Rate", "value": f"{repeat_rate}%", "delta": None},
        {"label": "Repeat Revenue Share", "value": f"{repeat_revenue_share}%", "delta": None},
        {"label": "New Customers", "value": f"{new_count:,}", "delta": None},
        {"label": "Repeat Customers", "value": f"{repeat_count:,}", "delta": None},
    ]

    # ─── Charts ──────────────────────────────────────────────────────────
    # Revenue by customer type over time
    if not monthly_type.empty:
        result["charts"].append(
            viz.stacked_bar(
                monthly_type, x="year_month", y="total_revenue", color="customer_type",
                title="Revenue by Customer Type (Monthly)",
                y_label="Revenue",
            )
        )

    # Revenue mix pie chart
    type_summary = pd.DataFrame({
        "type": ["New", "Repeat"],
        "revenue": [new_revenue, repeat_revenue],
    })
    result["charts"].append(
        viz.pie_chart(type_summary, names="type", values="revenue",
                      title="Revenue Mix: New vs Repeat")
    )

    # ─── Insights ────────────────────────────────────────────────────────
    if repeat_rate > 40:
        result["insights"].append(
            f"💪 Strong repeat customer base: **{repeat_rate}%** of customers are repeat buyers."
        )
    elif repeat_rate > 20:
        result["insights"].append(
            f"📊 Moderate repeat rate: **{repeat_rate}%** of customers return. Focus on retention."
        )
    else:
        result["insights"].append(
            f"⚠️ Low repeat rate: Only **{repeat_rate}%** of customers return. Retention needs attention."
        )

    if repeat_revenue_share > 50:
        result["insights"].append(
            f"✅ Repeat customers drive **{repeat_revenue_share}%** of revenue — healthy growth quality."
        )
    else:
        result["insights"].append(
            f"📈 New customers drive majority of revenue ({round(100 - repeat_revenue_share, 1)}%). "
            f"Growth depends heavily on acquisition."
        )

    return result
