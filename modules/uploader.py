"""
uploader.py — File Upload & Encoding Detection
Accepts CSV and Excel files, auto-detects encoding, returns DataFrame.
Pure function — no Streamlit calls.
"""

import io
import pandas as pd
import chardet


def parse_file(uploaded_file):
    """Parse an uploaded file into a DataFrame.

    Args:
        uploaded_file: Streamlit UploadedFile object.

    Returns:
        tuple: (DataFrame, status_message) on success,
               (None, error_message) on failure.
    """
    try:
        file_name = uploaded_file.name.lower()
        raw_bytes = uploaded_file.read()

        # Validate not empty
        if len(raw_bytes) == 0:
            return None, "⚠️ The uploaded file is empty. Please upload a file with data."

        # Parse based on extension
        if file_name.endswith(".csv"):
            df = _parse_csv(raw_bytes)
        elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
            df = _parse_excel(raw_bytes)
        else:
            return None, "⚠️ Unsupported file format. Please upload a .csv or .xlsx file."

        # Validate result
        if df is None or df.empty:
            return None, "⚠️ The file was read but contains no data."

        if len(df.columns) < 2:
            return None, "⚠️ The file has too few columns. Please check the format."

        rows, cols = df.shape
        return df, f"✅ Loaded successfully — {rows:,} rows × {cols} columns"

    except Exception:
        return None, "⚠️ Could not read this file. It may be corrupted or in an unsupported format."


def _parse_csv(raw_bytes):
    """Parse CSV bytes with auto-detected encoding."""
    # Detect encoding
    detection = chardet.detect(raw_bytes[:10000])  # Sample first 10KB
    encoding = detection.get("encoding", "utf-8") or "utf-8"

    try:
        df = pd.read_csv(io.BytesIO(raw_bytes), encoding=encoding)
    except (UnicodeDecodeError, LookupError):
        # Fallback to utf-8, then latin-1
        try:
            df = pd.read_csv(io.BytesIO(raw_bytes), encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(raw_bytes), encoding="latin-1")

    return df


def _parse_excel(raw_bytes):
    """Parse Excel bytes."""
    df = pd.read_excel(io.BytesIO(raw_bytes), engine="openpyxl")
    return df
