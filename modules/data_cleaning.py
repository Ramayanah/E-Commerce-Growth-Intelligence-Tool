"""
data_cleaning.py — Type Conversion, Dedup, Normalization
Converts dates, strips currency, handles nulls, normalizes text.
Pure function — no Streamlit calls.
"""

import re
import pandas as pd
import numpy as np
import config


def clean(df):
    """Clean and standardize the DataFrame.

    Args:
        df: DataFrame with standardized column names (after schema_detection).

    Returns:
        tuple: (cleaned_df, cleaning_report)
            - cleaned_df: Cleaned pandas DataFrame.
            - cleaning_report: dict with counts of actions taken.
    """
    report = {
        "original_rows": len(df),
        "duplicates_removed": 0,
        "null_rows_dropped": 0,
        "invalid_dates": 0,
        "invalid_revenue": 0,
        "negative_revenue": 0,
        "text_normalized": 0,
    }

    df = df.copy()

    # ─── Step 1: Remove duplicates on order_id ───────────────────────────
    if "order_id" in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=["order_id"], keep="first")
        report["duplicates_removed"] = before - len(df)

    # ─── Step 2: Convert date column ─────────────────────────────────────
    if "date" in df.columns:
        df["date"], invalid_count = _convert_dates(df["date"])
        report["invalid_dates"] = invalid_count
        # Drop rows with no valid date
        null_dates = df["date"].isna().sum()
        df = df.dropna(subset=["date"])
        report["null_rows_dropped"] += null_dates

    # ─── Step 3: Clean numeric columns (revenue, cost, marketing_spend) ─
    numeric_cols = ["revenue", "cost", "marketing_spend"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = _clean_numeric(df[col])

    # Track invalid revenue
    if "revenue" in df.columns:
        report["invalid_revenue"] = int(df["revenue"].isna().sum())
        report["negative_revenue"] = int((df["revenue"] < 0).sum())

    # ─── Step 4: Drop rows where ALL required fields are null ────────────
    required_present = [c for c in config.REQUIRED_COLUMNS if c in df.columns]
    if required_present:
        before = len(df)
        df = df.dropna(subset=required_present, how="all")
        report["null_rows_dropped"] += before - len(df)

    # ─── Step 5: Fill optional numeric columns with 0 ────────────────────
    optional_numeric = ["cost", "marketing_spend"]
    for col in optional_numeric:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # ─── Step 6: Normalize text columns ──────────────────────────────────
    text_count = 0
    for col in config.TEXT_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
            # Replace 'nan' strings from astype conversion
            df[col] = df[col].replace("nan", "unknown")
            text_count += 1
    report["text_normalized"] = text_count

    # ─── Step 7: Add year_month column for aggregation ───────────────────
    if "date" in df.columns:
        df["year_month"] = df["date"].dt.to_period("M").astype(str)

    # ─── Step 8: Reset index ─────────────────────────────────────────────
    df = df.reset_index(drop=True)
    report["final_rows"] = len(df)

    return df, report


def format_cleaning_report(report):
    """Format cleaning report into user-friendly messages.

    Args:
        report: dict from clean() function.

    Returns:
        list of formatted message strings.
    """
    messages = []
    messages.append(
        f"📋 Started with **{report['original_rows']:,}** rows → "
        f"**{report['final_rows']:,}** rows after cleaning"
    )

    if report["duplicates_removed"] > 0:
        messages.append(
            f"🔄 Removed **{report['duplicates_removed']:,}** duplicate orders"
        )

    if report["invalid_dates"] > 0:
        messages.append(
            f"📅 **{report['invalid_dates']:,}** rows had invalid dates and were removed"
        )

    if report["negative_revenue"] > 0:
        messages.append(
            f"⚠️ **{report['negative_revenue']:,}** rows have negative revenue values (kept in analysis)"
        )

    if report["text_normalized"] > 0:
        messages.append(
            f"🔤 Normalized **{report['text_normalized']}** text columns to lowercase"
        )

    return messages


def _convert_dates(series):
    """Convert a series to datetime, trying multiple formats.

    Returns:
        tuple: (converted_series, count_of_invalid)
    """
    # First try pandas auto-detection
    converted = pd.to_datetime(series, errors="coerce", infer_datetime_format=True)

    # Count invalids
    invalid_count = int(converted.isna().sum() - series.isna().sum())
    if invalid_count < 0:
        invalid_count = 0

    # If too many NaTs, try explicit formats
    nat_ratio = converted.isna().sum() / max(len(series), 1)
    if nat_ratio > 0.5:
        for fmt in config.DATE_FORMATS:
            try:
                attempt = pd.to_datetime(series, format=fmt, errors="coerce")
                if attempt.notna().sum() > converted.notna().sum():
                    converted = attempt
            except Exception:
                continue

    invalid_count = max(0, int(converted.isna().sum() - series.isna().sum()))
    return converted, invalid_count


def _clean_numeric(series):
    """Strip currency symbols and convert to numeric.

    Returns:
        pd.Series of float64 values (with NaN for unconvertible).
    """
    # Convert to string, strip symbols
    s = series.astype(str)
    pattern = "[" + re.escape("".join(config.CURRENCY_SYMBOLS)) + r"\s]"
    s = s.str.replace(pattern, "", regex=True)
    # Handle common text values
    s = s.replace({"nan": np.nan, "": np.nan, "none": np.nan, "null": np.nan})
    return pd.to_numeric(s, errors="coerce")
