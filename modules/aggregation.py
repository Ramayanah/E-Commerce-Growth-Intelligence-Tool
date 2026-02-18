"""
aggregation.py — Pre-computation of Monthly & Segment Aggregations
Produces reusable summary DataFrames for all analytics modules.
Pure function — no Streamlit calls.
"""

import pandas as pd
from config import safe_divide


def build_monthly_summary(df):
    """Aggregate data by year_month.

    Args:
        df: Cleaned DataFrame with 'year_month' column.

    Returns:
        pd.DataFrame with columns: year_month, total_revenue, total_orders,
        unique_customers, avg_order_value, total_cost (if available).
    """
    if "year_month" not in df.columns or df.empty:
        return pd.DataFrame()

    agg_dict = {
        "revenue": "sum",
        "order_id": "count",
        "customer_id": "nunique",
    }

    # Include cost if available
    if "cost" in df.columns:
        agg_dict["cost"] = "sum"

    # Include marketing_spend if available
    if "marketing_spend" in df.columns:
        agg_dict["marketing_spend"] = "sum"

    monthly = (
        df.groupby("year_month", sort=True)
        .agg(agg_dict)
        .reset_index()
    )

    # Rename columns
    rename_map = {
        "revenue": "total_revenue",
        "order_id": "total_orders",
        "customer_id": "unique_customers",
    }
    if "cost" in monthly.columns:
        rename_map["cost"] = "total_cost"
    if "marketing_spend" in monthly.columns:
        rename_map["marketing_spend"] = "total_marketing_spend"

    monthly = monthly.rename(columns=rename_map)

    # Compute AOV
    monthly["avg_order_value"] = monthly.apply(
        lambda r: round(safe_divide(r["total_revenue"], r["total_orders"]), 2),
        axis=1,
    )

    return monthly


def build_segment_summary(df, segment_col):
    """Aggregate data by a segment column (channel, region, category, etc.).

    Args:
        df: Cleaned DataFrame.
        segment_col: Column name to segment by.

    Returns:
        pd.DataFrame with columns: segment, total_revenue, total_orders,
        unique_customers, avg_order_value.
        Returns empty DataFrame if segment_col not in df.
    """
    if segment_col not in df.columns or df.empty:
        return pd.DataFrame()

    agg_dict = {
        "revenue": "sum",
        "order_id": "count",
        "customer_id": "nunique",
    }

    segment = (
        df.groupby(segment_col, sort=True)
        .agg(agg_dict)
        .reset_index()
        .rename(columns={
            segment_col: "segment",
            "revenue": "total_revenue",
            "order_id": "total_orders",
            "customer_id": "unique_customers",
        })
    )

    segment["avg_order_value"] = segment.apply(
        lambda r: round(safe_divide(r["total_revenue"], r["total_orders"]), 2),
        axis=1,
    )

    # Sort by revenue descending
    segment = segment.sort_values("total_revenue", ascending=False).reset_index(drop=True)

    return segment


def build_daily_summary(df):
    """Aggregate data by date.

    Args:
        df: Cleaned DataFrame with 'date' column.

    Returns:
        pd.DataFrame with columns: date, daily_revenue, daily_orders.
    """
    if "date" not in df.columns or df.empty:
        return pd.DataFrame()

    daily = (
        df.groupby("date", sort=True)
        .agg({"revenue": "sum", "order_id": "count"})
        .reset_index()
        .rename(columns={
            "revenue": "daily_revenue",
            "order_id": "daily_orders",
        })
    )

    return daily
