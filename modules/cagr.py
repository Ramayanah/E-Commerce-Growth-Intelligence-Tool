"""
cagr.py — CAGR & Investor-View Metrics
Calculates compound annual growth rate and builds investor-grade summary.
"""

import pandas as pd
import numpy as np
from config import safe_divide
from modules import visualization as viz


def analyze(clean_df, monthly_df, kpis):
    """Calculate CAGR and build investor-view summary.

    Args:
        clean_df: Cleaned DataFrame.
        monthly_df: Monthly summary DataFrame.
        kpis: Dict of core KPIs.

    Returns:
        dict: {"kpis": [...], "charts": [...], "insights": [...]}
    """
    result = {"kpis": [], "charts": [], "insights": []}

    if monthly_df.empty or len(monthly_df) < 2:
        result["insights"].append(
            "📊 Need at least 2 months of data to calculate CAGR."
        )
        return result

    # ─── CAGR Calculation ────────────────────────────────────────────────
    first_month_rev = monthly_df.iloc[0]["total_revenue"]
    last_month_rev = monthly_df.iloc[-1]["total_revenue"]
    num_months = len(monthly_df)
    num_years = num_months / 12.0

    cagr = _calculate_cagr(first_month_rev, last_month_rev, num_years)

    # Monthly CAGR (compounded monthly rate)
    monthly_cagr = _calculate_cagr(first_month_rev, last_month_rev, num_months)

    # ─── Revenue Projection (next 3 months) ──────────────────────────────
    projection_df = _project_revenue(monthly_df, months_ahead=3)

    # ─── KPIs ────────────────────────────────────────────────────────────
    result["kpis"] = [
        {"label": "Annualized CAGR", "value": f"{cagr}%", "delta": None},
        {"label": "Monthly Growth Rate", "value": f"{monthly_cagr}%", "delta": None},
        {"label": "First Month Revenue", "value": f"₹{first_month_rev:,.0f}", "delta": None},
        {"label": "Latest Month Revenue", "value": f"₹{last_month_rev:,.0f}", "delta": None},
    ]

    # ─── Revenue Trend + Projection Chart ────────────────────────────────
    if not projection_df.empty:
        result["charts"].append(
            viz.line_chart(
                projection_df, x="year_month", y="revenue", color="type",
                title="Revenue Trend with Projection",
                y_label="Revenue (₹)",
            )
        )
    else:
        result["charts"].append(
            viz.line_chart(
                monthly_df, x="year_month", y="total_revenue",
                title="Revenue Trend",
                y_label="Revenue (₹)",
            )
        )

    # ─── Cumulative Revenue Chart ────────────────────────────────────────
    cum_df = monthly_df.copy()
    cum_df["cumulative_revenue"] = cum_df["total_revenue"].cumsum()
    result["charts"].append(
        viz.line_chart(
            cum_df, x="year_month", y="cumulative_revenue",
            title="Cumulative Revenue Over Time",
            y_label="Cumulative Revenue (₹)",
        )
    )

    # ─── Investor Summary Table Data ─────────────────────────────────────
    total_rev = kpis.get("total_revenue", 0)
    total_orders = kpis.get("total_orders", 0)
    total_customers = kpis.get("unique_customers", 0)

    result["insights"].append(f"📈 **Annualized CAGR: {cagr}%** over {num_months} months of data.")

    if cagr > 50:
        result["insights"].append("🚀 Hyper-growth territory — excellent trajectory for investors.")
    elif cagr > 20:
        result["insights"].append("💪 Strong growth rate — attractive for investment.")
    elif cagr > 0:
        result["insights"].append("📊 Moderate growth — stable but may need acceleration.")
    else:
        result["insights"].append("⚠️ Negative CAGR — revenue is declining over the period.")

    result["insights"].append(
        f"📋 **Investor Summary**: {num_months} months data | "
        f"₹{total_rev:,.0f} total revenue | "
        f"{total_orders:,} orders | "
        f"{total_customers:,} customers | "
        f"AOV: ₹{kpis.get('avg_order_value', 0):,.2f}"
    )

    return result


def _calculate_cagr(beginning_value, ending_value, periods):
    """Calculate CAGR (Compound Annual Growth Rate).

    Args:
        beginning_value: Starting value.
        ending_value: Ending value.
        periods: Number of periods (years for annual, months for monthly).

    Returns:
        float: CAGR percentage, rounded to 2 decimals.
    """
    if beginning_value <= 0 or ending_value <= 0 or periods <= 0:
        return 0.0

    try:
        cagr = (pow(ending_value / beginning_value, 1.0 / periods) - 1) * 100
        return round(cagr, 2)
    except (ValueError, ZeroDivisionError, OverflowError):
        return 0.0


def _project_revenue(monthly_df, months_ahead=3):
    """Project revenue using simple linear trend.

    Args:
        monthly_df: Monthly summary DataFrame.
        months_ahead: Number of months to project.

    Returns:
        pd.DataFrame with historical + projected rows.
    """
    if len(monthly_df) < 2:
        return pd.DataFrame()

    try:
        # Simple linear regression on monthly revenue
        y = monthly_df["total_revenue"].values
        x = np.arange(len(y))

        # Fit line: y = mx + b
        coeffs = np.polyfit(x, y, 1)
        slope, intercept = coeffs[0], coeffs[1]

        # Historical data
        hist = pd.DataFrame({
            "year_month": monthly_df["year_month"].values,
            "revenue": y,
            "type": "Actual",
        })

        # Projected data
        last_month = pd.Period(monthly_df.iloc[-1]["year_month"], freq="M")
        proj_months = [(last_month + i + 1).strftime("%Y-%m") for i in range(months_ahead)]
        proj_x = np.arange(len(y), len(y) + months_ahead)
        proj_y = slope * proj_x + intercept
        proj_y = np.maximum(proj_y, 0)  # No negative projections

        proj = pd.DataFrame({
            "year_month": proj_months,
            "revenue": proj_y.round(2),
            "type": "Projected",
        })

        return pd.concat([hist, proj], ignore_index=True)

    except Exception:
        return pd.DataFrame()
