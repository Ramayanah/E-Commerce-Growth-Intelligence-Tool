"""
kpi_engine.py — Core KPI Calculator
Computes top-line KPIs from aggregated data.
Pure function — no Streamlit calls.
"""

from config import safe_divide, safe_pct_change


def compute_kpis(clean_df, monthly_df):
    """Compute core KPIs from cleaned and aggregated data.

    Args:
        clean_df: Cleaned DataFrame (full granularity).
        monthly_df: Monthly summary DataFrame from aggregation.py.

    Returns:
        dict of KPI values.
    """
    kpis = {}

    if clean_df.empty or monthly_df.empty:
        return _empty_kpis()

    # ─── Revenue KPIs ────────────────────────────────────────────────────
    kpis["total_revenue"] = round(clean_df["revenue"].sum(), 2)
    kpis["total_orders"] = int(clean_df["order_id"].nunique()) if "order_id" in clean_df.columns else len(clean_df)
    kpis["unique_customers"] = int(clean_df["customer_id"].nunique()) if "customer_id" in clean_df.columns else 0

    # ─── Averages ────────────────────────────────────────────────────────
    kpis["avg_order_value"] = round(
        safe_divide(kpis["total_revenue"], kpis["total_orders"]), 2
    )
    kpis["revenue_per_customer"] = round(
        safe_divide(kpis["total_revenue"], kpis["unique_customers"]), 2
    )

    # ─── Latest & Previous Month ─────────────────────────────────────────
    if len(monthly_df) >= 1:
        kpis["latest_month"] = monthly_df.iloc[-1]["year_month"]
        kpis["latest_month_revenue"] = round(monthly_df.iloc[-1]["total_revenue"], 2)
    else:
        kpis["latest_month"] = "N/A"
        kpis["latest_month_revenue"] = 0

    if len(monthly_df) >= 2:
        prev_rev = monthly_df.iloc[-2]["total_revenue"]
        curr_rev = monthly_df.iloc[-1]["total_revenue"]
        kpis["mom_revenue_growth"] = round(safe_pct_change(curr_rev, prev_rev), 2)
    else:
        kpis["mom_revenue_growth"] = None  # Not enough data

    # ─── Cost & Margin (if available) ────────────────────────────────────
    if "cost" in clean_df.columns:
        total_cost = clean_df["cost"].sum()
        kpis["total_cost"] = round(total_cost, 2)
        kpis["gross_margin"] = round(
            safe_divide(kpis["total_revenue"] - total_cost, kpis["total_revenue"]) * 100, 2
        )
    else:
        kpis["total_cost"] = None
        kpis["gross_margin"] = None

    # ─── Marketing (if available) ────────────────────────────────────────
    if "marketing_spend" in clean_df.columns:
        kpis["total_marketing_spend"] = round(clean_df["marketing_spend"].sum(), 2)
        kpis["roas"] = round(
            safe_divide(kpis["total_revenue"], kpis["total_marketing_spend"]), 2
        )
    else:
        kpis["total_marketing_spend"] = None
        kpis["roas"] = None

    # ─── Period Info ─────────────────────────────────────────────────────
    kpis["total_months"] = len(monthly_df)
    kpis["orders_per_customer"] = round(
        safe_divide(kpis["total_orders"], kpis["unique_customers"]), 2
    )

    return kpis


def _empty_kpis():
    """Return a dict of KPIs with all values set to zero/None."""
    return {
        "total_revenue": 0,
        "total_orders": 0,
        "unique_customers": 0,
        "avg_order_value": 0,
        "revenue_per_customer": 0,
        "latest_month": "N/A",
        "latest_month_revenue": 0,
        "mom_revenue_growth": None,
        "total_cost": None,
        "gross_margin": None,
        "total_marketing_spend": None,
        "roas": None,
        "total_months": 0,
        "orders_per_customer": 0,
    }
