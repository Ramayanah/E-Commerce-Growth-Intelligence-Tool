"""
config.py — Single Source of Truth
Central constants, column aliases, color palette, and safe utilities.
"""

#  Required & Optional Columns 
REQUIRED_COLUMNS = ["date", "order_id", "customer_id", "revenue"]

OPTIONAL_COLUMNS = [
    "cost", "channel", "region", "category", "device", "marketing_spend"
]

#  Column Alias Map 
# Each standard column name → list of possible aliases found in user datasets.
COLUMN_ALIASES = {
    # Required
    "date": [
        "date", "order_date", "purchase_date", "transaction_date",
        "created_at", "created_date", "sale_date", "invoice_date",
        "dt", "dates",
    ],
    "order_id": [
        "order_id", "orderid", "order_number", "order_no",
        "transaction_id", "txn_id", "invoice_id", "id",
    ],
    "customer_id": [
        "customer_id", "customerid", "cust_id", "custid",
        "client_id", "user_id", "userid", "buyer_id",
    ],
    "revenue": [
        "revenue", "sales", "amount", "total_amount", "order_value",
        "total_sales", "total_revenue", "sale_amount", "gmv",
        "gross_revenue", "net_revenue", "price", "total_price",
        "order_amount", "transaction_amount",
    ],
    # Optional
    "cost": [
        "cost", "total_cost", "cogs", "cost_of_goods",
        "expense", "product_cost",
    ],
    "channel": [
        "channel", "source", "traffic_source", "acquisition_channel",
        "utm_source", "marketing_channel", "medium",
    ],
    "region": [
        "region", "location", "area", "zone", "city",
        "state", "country", "geography", "geo",
    ],
    "category": [
        "category", "product_category", "item_category",
        "department", "product_type", "type", "segment",
    ],
    "device": [
        "device", "device_type", "platform", "device_category",
    ],
    "marketing_spend": [
        "marketing_spend", "ad_spend", "spend", "marketing_cost",
        "advertising_cost", "campaign_cost", "media_spend",
    ],
}

#  Currency Symbols to Strip 
CURRENCY_SYMBOLS = ["₹", "$", "€", "£", "¥", ","]

#  Date Formats to Try 
DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m-%d-%Y",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y/%m/%d",
    "%d %b %Y",
    "%d %B %Y",
    "%b %d, %Y",
    "%B %d, %Y",
]

#  Chart Configuration 
CHART_TEMPLATE = "plotly_white"
CHART_HEIGHT = 350

CHART_COLORS = [
    "#636EFA",  # Blue
    "#EF553B",  # Red
    "#00CC96",  # Green
    "#AB63FA",  # Purple
    "#FFA15A",  # Orange
    "#19D3F3",  # Cyan
    "#FF6692",  # Pink
    "#B6E880",  # Lime
    "#FF97FF",  # Magenta
    "#FECB52",  # Yellow
]

#  Text Columns (for normalization) 
TEXT_COLUMNS = ["channel", "region", "category", "device"]

#  Safe Math Utilities 

def safe_divide(numerator, denominator, default=0.0):
    """Safe division that returns default when denominator is zero or None."""
    try:
        if denominator is None or denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def safe_pct_change(new_val, old_val, default=0.0):
    """Safe percentage change: ((new - old) / old) * 100."""
    try:
        if old_val is None or old_val == 0:
            return default
        return ((new_val - old_val) / old_val) * 100
    except (TypeError, ZeroDivisionError):
        return default
