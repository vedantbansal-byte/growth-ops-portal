import streamlit as st
import pandas as pd

# 1. Page Config & Modern UI Styling
st.set_page_config(page_title="Growth Ops Command Center", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stMetric {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# 2. Direct Published CSV Import (Bypasses org domain restrictions)
PUBLISHED_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUaNVUbWKiScK0bdDM4aO3YU6MTkuYrwKUEKcBggmSK1eO5uEVHkQUpkL8jNsYvN1_8wVUT2WfyLwJ/pub?gid=247608123&single=true&output=csv"

@st.cache_data(ttl=0)
def load_data():
    return pd.read_csv(PUBLISHED_CSV_URL)

try:
    df = load_data()
except Exception as e:
    st.error(f"Failed to load published sheet data: {e}")
    st.stop()

# 3. Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select View:", ["🏠 Home Dashboard", "📋 Seller Details", "📈 Metabase View"])

# ---------------------------------------------------------
# PAGE 1: HOME DASHBOARD
# ---------------------------------------------------------
if page == "🏠 Home Dashboard":
    st.title("📊 Home Dashboard & KPI Overview")
    st.caption("Live metrics calculated directly from Published Master Sheet")
    
    # Calculate Numeric Totals
    total_start = df['startofweekbudget'].sum() if 'startofweekbudget' in df else 0
    total_current = df['Current_budget'].sum() if 'Current_budget' in df else 0
    total_target = df['week_target'].sum() if 'week_target' in df else 0
    total_unplanned = df['unplanned scaledown'].sum() if 'unplanned scaledown' in df else 0
    total_scaleup = df['Planned Scaleup Pending'].sum() if 'Planned Scaleup Pending' in df else 0
    total_scaledown = df['Planned Scaledown pending'].sum() if 'Planned Scaledown pending' in df else 0
    
    # Calculate Completion Rates as PERCENTAGES (%)
    total_sellers = len(df)
    ts_completed_count = (df['TS'] == 'Submitted').sum() if 'TS' in df else 0
    action_completed_count = (df['Action'] == 'Completed').sum() if 'Action' in df else 0
    
    ts_pct = (ts_completed_count / total_sellers * 100) if total_sellers > 0 else 0
    action_pct = (action_completed_count / total_sellers * 100) if total_sellers > 0 else 0

    # Display KPI Grid
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Start of Week Budget", f"₹{total_start:,.2f}")
    c2.metric("Current Budget", f"₹{total_current:,.2f}")
    c3.metric("Week Target", f"₹{total_target:,.2f}")
    c4.metric("TS Completion Rate (%)", f"{ts_pct:.1f}%")

    st.write("")
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Unplanned Scaledown", f"₹{total_unplanned:,.2f}")
    c6.metric("Planned Scaleup Pending", f"₹{total_scaleup:,.2f}")
    c7.metric("Planned Scaledown Pending", f"₹{total_scaledown:,.2f}")
    c8.metric("Action Completion Rate (%)", f"{action_pct:.1f}%")

    st.markdown("---")
    
    # Interactive Metric Drill-Down
    st.subheader("🔍 Interactive Metric Drill-Down")
    with st.expander("Click here to view Sellers with Unplanned Scaledown Amounts", expanded=False):
        if 'unplanned scaledown' in df and 'Seller Name' in df:
            unplanned_df = df[df['unplanned scaledown'] > 0][['Seller Name', 'unplanned scaledown']]
            st.dataframe(unplanned_df, use_container_width=True)
        else:
            st.info("No unplanned scaledown entries found.")

# ---------------------------------------------------------
# PAGE 2: SELLER DETAILS
# ---------------------------------------------------------
elif page == "📋 Seller Details":
    st.title("📋 Seller Master View")
    
    search = st.text_input("🔍 Search Seller by Name:")
    filtered_df = df
    if search and 'Seller Name' in df:
        filtered_df = df[df['Seller Name'].astype(str).str.contains(search, case=False, na=False)]

    st.dataframe(filtered_df, use_container_width=True, height=400)

# ---------------------------------------------------------
# PAGE 3: METABASE ANALYTICS VIEW
# ---------------------------------------------------------
elif page == "📈 Metabase View":
    st.title("📈 Metabase Directory View")
    st.caption("Direct overview of active Metabase queries")
    
    st.dataframe(df, use_container_width=True)
