"""
sample_data.py — Built-in Sample Dataset Generator
Generates a realistic 12-month, 1000-order e-commerce dataset.
Cached to avoid regeneration on every Streamlit rerun.
"""

import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data
def generate():
    """Generate a realistic sample e-commerce dataset.

    Returns:
        pd.DataFrame with columns: date, order_id, customer_id, revenue,
        cost, channel, region, category, device, marketing_spend.
    """
    np.random.seed(42)
    n_orders = 1000
    n_customers = 300

    # 12-month date range
    start_date = pd.Timestamp("2024-01-01")
    end_date = pd.Timestamp("2024-12-31")
    date_range_days = (end_date - start_date).days
    random_days = np.random.randint(0, date_range_days + 1, size=n_orders)
    dates = [start_date + pd.Timedelta(days=int(d)) for d in random_days]

    # Customer IDs — ~300 unique (repeat buyers)
    customer_ids = [f"CUST-{i:04d}" for i in range(1, n_customers + 1)]
    assigned_customers = np.random.choice(customer_ids, size=n_orders)

    # Revenue — normal distribution, mean ₹1500, std ₹500, clipped > 100
    revenue = np.random.normal(loc=1500, scale=500, size=n_orders)
    revenue = np.clip(revenue, 100, None).round(2)

    # Cost — 60-80% of revenue
    cost_ratio = np.random.uniform(0.60, 0.80, size=n_orders)
    cost = (revenue * cost_ratio).round(2)

    # Categorical columns
    channels = ["Organic", "Paid", "Social", "Email", "Referral"]
    regions = ["North", "South", "East", "West"]
    categories = ["Electronics", "Fashion", "Home", "Beauty"]
    devices = ["Mobile", "Desktop", "Tablet"]

    channel_picks = np.random.choice(channels, size=n_orders)
    region_picks = np.random.choice(regions, size=n_orders)
    category_picks = np.random.choice(categories, size=n_orders)
    device_picks = np.random.choice(devices, size=n_orders, p=[0.55, 0.35, 0.10])

    # Marketing spend correlated with channel
    channel_spend_map = {
        "Organic": (5, 20),
        "Paid": (50, 200),
        "Social": (20, 80),
        "Email": (2, 15),
        "Referral": (10, 40),
    }
    marketing_spend = np.array([
        round(np.random.uniform(*channel_spend_map[ch]), 2)
        for ch in channel_picks
    ])

    df = pd.DataFrame({
        "date": dates,
        "order_id": [f"ORD-{i:04d}" for i in range(1, n_orders + 1)],
        "customer_id": assigned_customers,
        "revenue": revenue,
        "cost": cost,
        "channel": channel_picks,
        "region": region_picks,
        "category": category_picks,
        "device": device_picks,
        "marketing_spend": marketing_spend,
    })

    # Sort by date for time-series consistency
    df = df.sort_values("date").reset_index(drop=True)

    return df
