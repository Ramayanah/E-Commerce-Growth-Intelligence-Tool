"""
schema_detection.py — Alias-Based Column Mapping
Auto-maps user columns to standard schema using configurable alias lists.
Pure function — no Streamlit calls.
"""

import config


def detect_and_map(df):
    """Detect and map columns to the standard schema using alias lists.

    Args:
        df: Raw pandas DataFrame.

    Returns:
        tuple: (mapped_df, mapping_report, missing_required)
            - mapped_df: DataFrame with standardized column names.
            - mapping_report: dict of {standard_name: original_name}.
            - missing_required: list of required columns not found.
    """
    # Step 1: Normalize column names
    df = df.copy()
    df.columns = [_normalize_col_name(c) for c in df.columns]

    # Step 2: De-duplicate column names
    df.columns = _deduplicate_columns(list(df.columns))

    # Step 3: Build mapping
    all_standard = config.REQUIRED_COLUMNS + config.OPTIONAL_COLUMNS
    mapping = {}         # standard_name → original_name
    rename_map = {}      # original_name → standard_name (for df.rename)

    for standard_col in all_standard:
        aliases = config.COLUMN_ALIASES.get(standard_col, [standard_col])
        for alias in aliases:
            normalized_alias = _normalize_col_name(alias)
            if normalized_alias in df.columns and normalized_alias not in rename_map:
                mapping[standard_col] = normalized_alias
                if normalized_alias != standard_col:
                    rename_map[normalized_alias] = standard_col
                break

    # Step 4: Rename columns
    if rename_map:
        df = df.rename(columns=rename_map)

    # Step 5: Identify missing required columns
    missing_required = [
        col for col in config.REQUIRED_COLUMNS if col not in mapping
    ]

    return df, mapping, missing_required


def format_mapping_report(mapping, missing_required):
    """Format the mapping results into a user-friendly report.

    Args:
        mapping: dict of {standard_name: original_name}.
        missing_required: list of missing required column names.

    Returns:
        dict with 'mapped', 'missing', and 'summary' keys.
    """
    report = {
        "mapped": {k: v for k, v in mapping.items()},
        "missing": missing_required,
        "total_mapped": len(mapping),
        "summary": [],
    }

    for std_name, orig_name in mapping.items():
        if std_name == orig_name:
            report["summary"].append(f"✅ **{std_name}** — found directly")
        else:
            report["summary"].append(f"✅ **{std_name}** ← mapped from `{orig_name}`")

    for col in missing_required:
        report["summary"].append(f"❌ **{col}** — not found (required)")

    return report


def _normalize_col_name(name):
    """Normalize a column name: lowercase, strip, replace spaces with underscores."""
    return str(name).strip().lower().replace(" ", "_")


def _deduplicate_columns(columns):
    """Make column names unique by appending _1, _2, etc. for duplicates."""
    seen = {}
    result = []
    for col in columns:
        if col in seen:
            seen[col] += 1
            result.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            result.append(col)
    return result
