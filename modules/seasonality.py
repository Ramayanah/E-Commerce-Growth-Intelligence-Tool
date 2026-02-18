"""
seasonality.py — MoM / Seasonal Pattern Detection
Analyzes month-over-month changes and seasonal trends.
"""

import pandas as pd
from config import safe_pct_change
from modules import visualization as viz


def analyze(clean_df, monthly_df, kpis):
    """Analyze seasonality and month-over-month patterns.

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
            "📊 Need at least 2 months of data for seasonality analysis."
        )
        return result

    # ─── MoM Growth ──────────────────────────────────────────────────────
    mom_df = monthly_df.copy()
    mom_df["prev_revenue"] = mom_df["total_revenue"].shift(1)
    mom_df["mom_growth"] = mom_df.apply(
        lambda r: round(safe_pct_change(r["total_revenue"], r["prev_revenue"]), 1)
        if pd.notna(r["prev_revenue"]) else None,
        axis=1,
    )

    # Drop first row (no previous month)
    mom_valid = mom_df.dropna(subset=["mom_growth"])

    # ─── KPIs ────────────────────────────────────────────────────────────
    if not mom_valid.empty:
        avg_mom = round(mom_valid["mom_growth"].mean(), 1)
        best_idx = mom_valid["mom_growth"].idxmax()
        worst_idx = mom_valid["mom_growth"].idxmin()
        best_month = mom_valid.loc[best_idx, "year_month"]
        worst_month = mom_valid.loc[worst_idx, "year_month"]
        best_growth = mom_valid.loc[best_idx, "mom_growth"]
        worst_growth = mom_valid.loc[worst_idx, "mom_growth"]

        result["kpis"] = [
            {"label": "Avg MoM Growth", "value": f"{avg_mom}%", "delta": None},
            {"label": "Best Month", "value": str(best_month), "delta": f"+{best_growth}%"},
            {"label": "Worst Month", "value": str(worst_month), "delta": f"{worst_growth}%"},
        ]
    else:
        avg_mom = 0

    # ─── Revenue Trend Chart ─────────────────────────────────────────────
    result["charts"].append(
        viz.line_chart(
            monthly_df, x="year_month", y="total_revenue",
            title="Monthly Revenue Trend",
            y_label="Revenue (₹)",
        )
    )

    # ─── MoM Growth Bar Chart ────────────────────────────────────────────
    if not mom_valid.empty:
        result["charts"].append(
            viz.bar_chart(
                mom_valid, x="year_month", y="mom_growth",
                title="Month-over-Month Revenue Growth (%)",
                y_label="Growth %",
            )
        )

    # ─── Orders Trend ────────────────────────────────────────────────────
    result["charts"].append(
        viz.line_chart(
            monthly_df, x="year_month", y="total_orders",
            title="Monthly Orders Trend",
            y_label="Orders",
        )
    )

    # ─── Day-of-Week Pattern (if daily data available) ───────────────────
    if "date" in clean_df.columns:
        dow_df = clean_df.copy()
        dow_df["day_of_week"] = dow_df["date"].dt.day_name()
        dow_summary = (
            dow_df.groupby("day_of_week")
            .agg({"revenue": "sum", "order_id": "count"})
            .reset_index()
            .rename(columns={"revenue": "total_revenue", "order_id": "total_orders"})
        )
        # Sort by weekday order
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_summary["day_of_week"] = pd.Categorical(
            dow_summary["day_of_week"], categories=day_order, ordered=True
        )
        dow_summary = dow_summary.sort_values("day_of_week")

        result["charts"].append(
            viz.bar_chart(
                dow_summary, x="day_of_week", y="total_revenue",
                title="Revenue by Day of Week",
                y_label="Revenue (₹)",
            )
        )

    # ─── Insights ────────────────────────────────────────────────────────
    if avg_mom > 5:
        result["insights"].append(
            f"📈 Average month-over-month revenue growth is **{avg_mom}%** — positive trajectory."
        )
    elif avg_mom > 0:
        result["insights"].append(
            f"📊 Average MoM growth is **{avg_mom}%** — slow but positive growth."
        )
    elif avg_mom < -5:
        result["insights"].append(
            f"⚠️ Average MoM growth is **{avg_mom}%** — revenue is declining."
        )
    else:
        result["insights"].append(
            f"📊 Average MoM growth is **{avg_mom}%** — revenue is relatively flat."
        )

    if not mom_valid.empty:
        positive_months = (mom_valid["mom_growth"] > 0).sum()
        total_months = len(mom_valid)
        result["insights"].append(
            f"📅 **{positive_months} out of {total_months}** months showed positive growth."
        )

    return result
