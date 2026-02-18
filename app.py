"""
app.py — Streamlit Entry Point
E-Commerce Growth Intelligence Tool
Tab router, data pipeline orchestration, and UI rendering.
"""

import streamlit as st
import sample_data
from modules import uploader
from modules import schema_detection
from modules import data_cleaning
from modules import aggregation
from modules import kpi_engine
from modules import growth_quality
from modules import unit_economics
from modules import segment_analysis
from modules import cohort_analysis
from modules import seasonality
from modules import cagr
from modules import visualization as viz
from modules.load_image import img_to_base64


# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Growth Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Load External CSS ──────────────────────────────────────────────────────
def load_css(file_path):
    """Load and inject CSS from an external file."""
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


load_css("assets/styles.css")


# ─── Sidebar: Profile + Uploader ────────────────────────────────────────────
with st.sidebar:
    # Profile section
    img_base64 = img_to_base64("assets/me.jpg")
    if img_base64:
        st.markdown(
            f'<div style="text-align:center; padding: 1rem 0;">'
            f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img">'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("<h3 style='text-align:center; margin-bottom:0;'>Raja Poddar</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#6b7280; font-size:0.85rem;'>"
        "Data Analyst | GST Consultant | Founder Of NaviData"
        "</p>",
        unsafe_allow_html=True,
    )

    st.divider()

    # File Uploader
    st.markdown("### 📁 Data Source")
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx"],
        help="Upload an e-commerce dataset with columns like date, order_id, "
             "customer_id, revenue. If no file is uploaded, sample data is used.",
    )

    st.divider()

    # Data source status
    df = None
    data_source = ""

    if uploaded_file is not None:
        df, status_msg = uploader.parse_file(uploaded_file)
        if df is not None:
            data_source = "uploaded"
            st.success("📁 **Using Uploaded Dataset**")
            st.caption(status_msg)
        else:
            st.error(status_msg)
            df = sample_data.generate()
            data_source = "sample"
            st.info("📊 Falling back to Sample Dataset")
    else:
        df = sample_data.generate()
        data_source = "sample"
        st.info("📊 **Using Sample Dataset**")
        st.caption("Upload a file above to analyze your own data.")


# ─── Main Area: Header ──────────────────────────────────────────────────────
st.markdown(
    '<div class="main-header">'
    '<h1>🚀 E-Commerce Growth Intelligence Tool</h1>'
    '<p>Production-grade analytics for growth diagnostics, unit economics, and investor readiness</p>'
    '</div>',
    unsafe_allow_html=True,
)


# ─── Data Preview ────────────────────────────────────────────────────────────
with st.expander("👀 Data Preview", expanded=False):
    st.dataframe(df.head(100), width="stretch", height=300)
    st.caption(f"Showing first {min(100, len(df))} rows of {len(df):,} total rows")


# ─── Schema Detection ───────────────────────────────────────────────────────
mapped_df, mapping, missing_required = schema_detection.detect_and_map(df)

mapping_report = schema_detection.format_mapping_report(mapping, missing_required)
with st.expander("🗺️ Column Mapping Summary", expanded=False):
    for line in mapping_report["summary"]:
        st.markdown(line)
    st.caption(f"Total columns mapped: {mapping_report['total_mapped']}")

if missing_required:
    st.error(
        f"❌ **Missing required columns:** {', '.join(missing_required)}\n\n"
        f"Your dataset must have columns that match: `date`, `order_id`, `customer_id`, `revenue`. "
        f"Please check your column names and re-upload."
    )
    st.stop()


# ─── Data Cleaning ───────────────────────────────────────────────────────────
clean_df, cleaning_report = data_cleaning.clean(mapped_df)

cleaning_messages = data_cleaning.format_cleaning_report(cleaning_report)
with st.expander("🧹 Data Cleaning Report", expanded=False):
    for msg in cleaning_messages:
        st.markdown(msg)

if len(clean_df) < 5:
    st.warning("⚠️ **Very small dataset** — results may not be meaningful with fewer than 5 rows.")

if clean_df.empty:
    st.error("❌ No valid data remaining after cleaning. Please check your dataset.")
    st.stop()


# ─── Aggregation & KPIs ─────────────────────────────────────────────────────
monthly_df = aggregation.build_monthly_summary(clean_df)
kpis = kpi_engine.compute_kpis(clean_df, monthly_df)


# ─── Helpers ─────────────────────────────────────────────────────────────────
def render_kpi_cards(kpi_list):
    """Render a row of KPI cards using Streamlit native st.metric()."""
    if not kpi_list:
        return
    cols = st.columns(len(kpi_list))
    for col, kpi in zip(cols, kpi_list):
        with col:
            st.metric(
                label=kpi["label"],
                value=kpi["value"],
                delta=kpi.get("delta"),
            )


def render_insights(insights):
    """Render insight messages."""
    for insight in insights:
        st.info(insight)


def render_tab(module, tab_name, *args, **kwargs):
    """Safely render a tab's content from a module's analyze function."""
    try:
        result = module.analyze(*args, **kwargs)

        if result.get("kpis"):
            render_kpi_cards(result["kpis"])

        for chart in result.get("charts", []):
            st.plotly_chart(chart, width="stretch")

        if result.get("insights"):
            st.markdown("### 💡 Business Insights")
            render_insights(result["insights"])

    except Exception:
        st.error(
            f"⚠️ Something went wrong while rendering **{tab_name}**. "
            f"Please check your data."
        )


# ─── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Overview",
    "🔍 Growth Quality",
    "💰 Unit Economics",
    "📦 Segment Analysis",
    "👥 Cohort Analysis",
    "📅 Seasonality",
    "📈 CAGR & Investor View",
])


# ─── Tab 1: Overview ────────────────────────────────────────────────────────
with tab1:
    st.markdown("## Top-Line Growth Overview")

    overview_kpis = [
        {"label": "Total Revenue", "value": f"₹{kpis['total_revenue']:,.0f}", "delta": None},
        {"label": "Total Orders", "value": f"{kpis['total_orders']:,}", "delta": None},
        {"label": "Unique Customers", "value": f"{kpis['unique_customers']:,}", "delta": None},
        {"label": "Avg Order Value", "value": f"₹{kpis['avg_order_value']:,.2f}", "delta": None},
    ]

    mom = kpis.get("mom_revenue_growth")
    if mom is not None:
        overview_kpis.append({
            "label": "MoM Revenue Growth",
            "value": f"{mom}%",
            "delta": "latest month",
        })

    render_kpi_cards(overview_kpis)

    if not monthly_df.empty:
        st.plotly_chart(
            viz.line_chart(
                monthly_df, x="year_month", y="total_revenue",
                title="Monthly Revenue Trend",
                y_label="Revenue (₹)",
            ),
            width="stretch",
        )

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                viz.bar_chart(
                    monthly_df, x="year_month", y="total_orders",
                    title="Monthly Orders",
                    y_label="Orders",
                ),
                width="stretch",
            )
        with col2:
            st.plotly_chart(
                viz.bar_chart(
                    monthly_df, x="year_month", y="unique_customers",
                    title="Monthly Unique Customers",
                    y_label="Customers",
                ),
                width="stretch",
            )

    st.markdown("### 💡 Business Insights")
    overview_insights = []

    if kpis["total_revenue"] > 0:
        overview_insights.append(
            f"💰 Total revenue across the period: **₹{kpis['total_revenue']:,.0f}** "
            f"from **{kpis['total_orders']:,}** orders by **{kpis['unique_customers']:,}** customers."
        )
    if mom is not None:
        if mom > 0:
            overview_insights.append(f"📈 Latest month revenue grew **{mom}%** month-over-month.")
        elif mom < 0:
            overview_insights.append(f"📉 Latest month revenue declined **{mom}%** month-over-month.")
        else:
            overview_insights.append("➡️ Latest month revenue was flat compared to previous month.")

    if kpis.get("gross_margin") is not None:
        overview_insights.append(f"📊 Overall gross margin: **{kpis['gross_margin']}%**")

    render_insights(overview_insights)


# ─── Tab 2–7 ─────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("## Growth Quality Analysis")
    render_tab(growth_quality, "Growth Quality", clean_df, monthly_df, kpis)

with tab3:
    st.markdown("## Unit Economics")
    render_tab(unit_economics, "Unit Economics", clean_df, monthly_df, kpis)

with tab4:
    st.markdown("## Segment Analysis")
    render_tab(segment_analysis, "Segment Analysis", clean_df, monthly_df, kpis)

with tab5:
    st.markdown("## Cohort Analysis")
    render_tab(cohort_analysis, "Cohort Analysis", clean_df, monthly_df, kpis)

with tab6:
    st.markdown("## Seasonality & Patterns")
    render_tab(seasonality, "Seasonality", clean_df, monthly_df, kpis)

with tab7:
    st.markdown("## CAGR & Investor View")
    render_tab(cagr, "CAGR & Investor View", clean_df, monthly_df, kpis)


# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p class="footer-text">'
    '🚀 E-Commerce Growth Intelligence Tool | Built with Streamlit & Plotly'
    '</p>',
    unsafe_allow_html=True,
)
