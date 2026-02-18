"""
unit_economics.py — Unit Economics Analysis
Analyzes AOV trends, revenue per customer, cost ratios, margins.
"""

import pandas as pd
from config import safe_divide
from modules import visualization as viz


def analyze(clean_df, monthly_df, kpis):
    """Analyze unit economics metrics.

    Args:
        clean_df: Cleaned DataFrame.
        monthly_df: Monthly summary DataFrame.
        kpis: Dict of core KPIs.

    Returns:
        dict: {"kpis": [...], "charts": [...], "insights": [...]}
    """
    result = {"kpis": [], "charts": [], "insights": []}

    if clean_df.empty or monthly_df.empty:
        result["insights"].append("📊 Not enough data to analyze unit economics.")
        return result

    # ─── KPIs ────────────────────────────────────────────────────────────
    aov = kpis.get("avg_order_value", 0)
    rpc = kpis.get("revenue_per_customer", 0)
    opc = kpis.get("orders_per_customer", 0)
    margin = kpis.get("gross_margin", None)

    result["kpis"] = [
        {"label": "Avg Order Value", "value": f"₹{aov:,.2f}", "delta": None},
        {"label": "Revenue / Customer", "value": f"₹{rpc:,.2f}", "delta": None},
        {"label": "Orders / Customer", "value": f"{opc:.1f}", "delta": None},
    ]
    if margin is not None:
        result["kpis"].append(
            {"label": "Gross Margin", "value": f"{margin}%", "delta": None}
        )

    # ─── AOV Trend Chart ─────────────────────────────────────────────────
    result["charts"].append(
        viz.line_chart(
            monthly_df, x="year_month", y="avg_order_value",
            title="Average Order Value (Monthly Trend)",
            y_label="AOV (₹)",
        )
    )

    # ─── Revenue per Customer Trend ──────────────────────────────────────
    monthly_rpc = monthly_df.copy()
    monthly_rpc["rev_per_customer"] = monthly_rpc.apply(
        lambda r: round(safe_divide(r["total_revenue"], r["unique_customers"]), 2),
        axis=1,
    )
    result["charts"].append(
        viz.line_chart(
            monthly_rpc, x="year_month", y="rev_per_customer",
            title="Revenue per Customer (Monthly Trend)",
            y_label="Revenue / Customer (₹)",
        )
    )

    # ─── Margin Trend (if cost data available) ───────────────────────────
    if "total_cost" in monthly_df.columns:
        margin_df = monthly_df.copy()
        margin_df["margin_pct"] = margin_df.apply(
            lambda r: round(
                safe_divide(r["total_revenue"] - r["total_cost"], r["total_revenue"]) * 100, 1
            ),
            axis=1,
        )
        result["charts"].append(
            viz.bar_chart(
                margin_df, x="year_month", y="margin_pct",
                title="Gross Margin % (Monthly)",
                y_label="Margin %",
            )
        )

    # ─── Insights ────────────────────────────────────────────────────────
    if aov > 0:
        result["insights"].append(
            f"🛒 Average order value is **₹{aov:,.2f}** across all orders."
        )

    if opc > 1.5:
        result["insights"].append(
            f"🔁 Customers place **{opc:.1f} orders** on average — strong repeat behavior."
        )
    elif opc > 1.0:
        result["insights"].append(
            f"📦 Customers place **{opc:.1f} orders** on average — some repeat purchases."
        )
    else:
        result["insights"].append(
            f"⚠️ Customers place only **{opc:.1f} orders** on average — mostly one-time buyers."
        )

    if margin is not None:
        if margin > 30:
            result["insights"].append(f"✅ Healthy gross margin at **{margin}%**.")
        elif margin > 15:
            result["insights"].append(f"📊 Moderate gross margin at **{margin}%**. Room for optimization.")
        else:
            result["insights"].append(f"⚠️ Low gross margin at **{margin}%**. Review cost structure.")

    return result
