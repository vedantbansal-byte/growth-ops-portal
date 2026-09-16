import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Page Config & Modern UI Styling
st.set_page_config(page_title="Growth Ops Command Center", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #4F46E5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stMetric {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# 2. Live Google Sheets Connection (0-second caching delay)
conn = st.connection("gsheets", type=GSheetsConnection)
sheet_url = "https://docs.google.com/spreadsheets/d/1TBqrGanctrLd3tVNm8OQTuxErXD1j5d_egMEgENtyZ8/export?format=csv&gid=1524369576"
df = conn.read(spreadsheet=sheet_url, ttl=0)

# 3. Sidebar Navigation
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1828/1828884.png", width=40)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select View:", ["🏠 Home Dashboard", "📋 Seller Details", "📈 Metabase View"])

# ---------------------------------------------------------
# PAGE 1: HOME DASHBOARD
# ---------------------------------------------------------
if page == "🏠 Home Dashboard":
    st.title("📊 Home Dashboard & KPI Overview")
    st.caption("Live totals and completion rates calculated directly from Master Sheet")
    
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
    
    # Interactive Unplanned Amount Drill-Down
    st.subheader("🔍 Interactive Metric Drill-Down")
    with st.expander("Click here to view Sellers with Unplanned Scaledown Amounts", expanded=False):
        if 'unplanned scaledown' in df and 'Seller Name' in df:
            unplanned_df = df[df['unplanned scaledown'] > 0][['Seller ID', 'Seller Name', 'unplanned scaledown']]
            st.dataframe(unplanned_df, use_container_width=True)
        else:
            st.info("No unplanned scaledown entries found.")

# ---------------------------------------------------------
# PAGE 2: SELLER DETAILS
# ---------------------------------------------------------
elif page == "📋 Seller Details":
    st.title("📋 Seller Master View")
    
    # Live Search Bar
    search = st.text_input("🔍 Search Seller by Name or ID:")
    filtered_df = df
    if search:
        filtered_df = df[df['Seller Name'].astype(str).str.contains(search, case=False, na=False)]

    st.dataframe(filtered_df, use_container_width=True, height=400)
    
    st.markdown("---")
    st.subheader("🔎 Detailed Seller Expand View")
    
    if 'Seller Name' in df:
        selected_seller = st.selectbox("Select a Seller to inspect in-depth:", filtered_df['Seller Name'].unique())
        
        if selected_seller:
            s_row = df[df['Seller Name'] == selected_seller].iloc[0]
            
            with st.container():
                col_a, col_b = st.columns(2)
                with col_a:
                    st.info(f"**Seller ID:** {s_row.get('Seller ID', 'N/A')}")
                    st.write(f"**Growth Lead:** {s_row.get('Growth Lead', 'N/A')}")
                    st.write(f"**Current Budget:** ₹{s_row.get('Current_budget', 0):,}")
                with col_b:
                    st.success(f"**TS Status:** {s_row.get('TS', 'N/A')}")
                    st.write(f"**Action Status:** {s_row.get('Action', 'N/A')}")
                    st.write(f"**Week Target:** ₹{s_row.get('week_target', 0):,}")
            
                st.markdown("#### 💬 WhatsApp Messages")
                tab1, tab2 = st.tabs(["Part A SOP Message", "Part B SOP Message"])
                with tab1:
                    st.text_area("Copy Part A:", s_row.get('Part A Message', 'No message generated'), height=150)
                with tab2:
                    st.text_area("Copy Part B:", s_row.get('Part B Message', 'No message generated'), height=150)

# ---------------------------------------------------------
# PAGE 3: METABASE ANALYTICS
# ---------------------------------------------------------
elif page == "📈 Metabase View":
    st.title("📈 Metabase Analytics Dashboard")
    
    s_id = st.text_input("Enter Seller ID to load Metabase metrics:")
    
    if s_id:
        match = df[df['Seller ID'].astype(str) == s_id]
        if not match.empty:
            data = match.iloc[0]
            st.success(f"Displaying Metabase profile for: **{data.get('Seller Name', 'Unknown')}**")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Start of Week Budget", f"₹{data.get('startofweekbudget', 0):,}")
            m2.metric("Current Budget", f"₹{data.get('Current_budget', 0):,}")
            m3.metric("Target Budget", f"₹{data.get('week_target', 0):,}")
            
            # Interactive Bar Chart Representation
            chart_df = pd.DataFrame({
                "Stage": ["Start of Week", "Current Budget", "Week Target"],
                "Amount (₹)": [data.get('startofweekbudget', 0), data.get('Current_budget', 0), data.get('week_target', 0)]
            })
            st.bar_chart(chart_df.set_index("Stage"))
        else:
            st.warning("Seller ID not found in sheet.")
