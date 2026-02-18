"""
segment_analysis.py — Channel / Region / Category Breakdowns
Analyzes revenue, orders, and customers by segment.
"""

import pandas as pd
from config import safe_divide
from modules import visualization as viz
from modules import aggregation


def analyze(clean_df, monthly_df, kpis):
    """Analyze revenue and growth by segment.

    Args:
        clean_df: Cleaned DataFrame.
        monthly_df: Monthly summary DataFrame.
        kpis: Dict of core KPIs.

    Returns:
        dict: {"kpis": [...], "charts": [...], "insights": [...]}
    """
    result = {"kpis": [], "charts": [], "insights": []}

    if clean_df.empty:
        result["insights"].append("📊 Not enough data for segment analysis.")
        return result

    total_revenue = kpis.get("total_revenue", 0)
    segments_found = []

    # ─── Process each segment type ───────────────────────────────────────
    for seg_col in ["channel", "region", "category"]:
        if seg_col not in clean_df.columns:
            continue

        seg_df = aggregation.build_segment_summary(clean_df, seg_col)
        if seg_df.empty:
            continue

        segments_found.append(seg_col)
        top_segment = seg_df.iloc[0]
        top_share = round(safe_divide(top_segment["total_revenue"], total_revenue) * 100, 1)

        # KPI for top segment
        result["kpis"].append({
            "label": f"Top {seg_col.title()}",
            "value": f"{top_segment['segment'].title()}",
            "delta": f"{top_share}% of revenue",
        })

        # Bar chart
        result["charts"].append(
            viz.bar_chart(
                seg_df, x="segment", y="total_revenue",
                title=f"Revenue by {seg_col.title()}",
                y_label="Revenue (₹)",
            )
        )

        # Insight for each segment type
        if len(seg_df) > 1:
            bottom_segment = seg_df.iloc[-1]
            bottom_share = round(
                safe_divide(bottom_segment["total_revenue"], total_revenue) * 100, 1
            )
            result["insights"].append(
                f"📊 **{seg_col.title()}**: Top is **{top_segment['segment'].title()}** "
                f"({top_share}% of revenue), lowest is **{bottom_segment['segment'].title()}** "
                f"({bottom_share}%)."
            )

    # ─── Segment by Channel over Time (if available) ─────────────────────
    if "channel" in clean_df.columns:
        monthly_channel = (
            clean_df.groupby(["year_month", "channel"])
            .agg({"revenue": "sum"})
            .reset_index()
        )
        if not monthly_channel.empty:
            result["charts"].append(
                viz.stacked_bar(
                    monthly_channel, x="year_month", y="revenue", color="channel",
                    title="Revenue by Channel (Monthly Trend)",
                    y_label="Revenue (₹)",
                )
            )

    if not segments_found:
        result["insights"].append(
            "ℹ️ No segment columns (channel, region, category) found in the dataset."
        )

    return result
