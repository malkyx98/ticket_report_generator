# app.py
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from src.styles import set_style, show_logo, kpi_card
from src.data_processing import clean_name, compute_kpis
from src.ppt_export import create_ppt
import plotly.express as px
import plotly.figure_factory as ff

# -------------------------------
# PAGE CONFIG & CUSTOM STYLE
# -------------------------------
st.set_page_config(page_title="Alayticx BI", layout="wide")
set_style()
show_logo()

# -------------------------------
# SESSION STATE DEFAULTS
# -------------------------------
defaults = {
    "data": pd.DataFrame(),
    "monthly_summary": pd.DataFrame(),
    "tech_summary": pd.DataFrame(),
    "caller_summary": pd.DataFrame(),
    "show_kpis": True,
    "show_trends": True,
    "anonymize_data": False,
    "theme": "Light",
    "decimal_places": 1,
    "page": "Dashboard",
    "universal_search": ""
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -------------------------------
# FILE UPLOAD SECTION (ALWAYS VISIBLE)
# -------------------------------
st.markdown("## Analytics BI")
uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type="xlsx")
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.session_state.data = df.copy()
    with st.expander("Preview Uploaded Data"):
        st.dataframe(df.head(), use_container_width=True)
elif st.session_state.data.empty:
    st.info("Please upload an Excel file to continue.")
    st.stop()

# -------------------------------
# DATA CLEANING & ANONYMIZATION
# -------------------------------
def clean_data(df):
    if 'Organization->Name' in df.columns:
        df['Company Name'] = clean_name(df, 'Organization->Name')
    else:
        df['Company Name'] = ""
    if 'Agent->Full name' in df.columns:
        df['Technician Name'] = clean_name(df, 'Agent->Full name')
    else:
        df['Technician Name'] = ""
    if 'Caller->Full name' in df.columns:
        df['Caller Name'] = clean_name(df, 'Caller->Full name')
    else:
        df['Caller Name'] = ""
    return df

def anonymize(df, columns):
    for col in columns:
        df[col] = [f"{col.split('->')[0]} {i+1}" for i in range(len(df))]
    return df

# -------------------------------
# KPI & SUMMARY FUNCTIONS
# -------------------------------
def calculate_monthly_summary(df):
    if 'Start date' in df.columns:
        df['Start date'] = pd.to_datetime(df['Start date'], errors='coerce')
        df['Month'] = df['Start date'].dt.to_period('M').astype(str)
    else:
        df['Month'] = 'Unknown'

    df = compute_kpis(df)
    df['Duration (days)'] = pd.to_numeric(df.get('Duration (days)', 0), errors='coerce').fillna(0)

    monthly_summary = (
        df.groupby('Month')
        .agg({
            'Ref': 'count',
            'Done Tasks': 'sum',
            'Pending Tasks': 'sum',
            'SLA TTO Done': 'sum',
            'SLA TTR Done': 'sum',
            'Duration (days)': 'mean'
        })
        .rename(columns={
            'Ref': 'Total Tickets',
            'Done Tasks': 'Closed Tickets',
            'Pending Tasks': 'Pending Tickets',
            'Duration (days)': 'Avg Resolution Days'
        })
        .reset_index()
    )

    monthly_summary['SLA TTO Violations'] = monthly_summary['Total Tickets'] - monthly_summary['SLA TTO Done']
    monthly_summary['SLA TTR Violations'] = monthly_summary['Total Tickets'] - monthly_summary['SLA TTR Done']
    monthly_summary['SLA Violations'] = ((monthly_summary['SLA TTO Violations'] + monthly_summary['SLA TTR Violations']) / 2).round(0)
    monthly_summary['Closure %'] = (monthly_summary['Closed Tickets'] / monthly_summary['Total Tickets'] * 100).round(1)
    monthly_summary['SLA %'] = ((monthly_summary['SLA TTO Done'] + monthly_summary['SLA TTR Done']) / (2 * monthly_summary['Total Tickets']) * 100).round(1)
    monthly_summary['Avg Resolution Days'] = monthly_summary['Avg Resolution Days'].fillna(0)

    return df, monthly_summary

def top_performers(df, role_col):
    summary = (
        df.groupby(role_col)
        .agg(Tickets=('Ref','count'), Done=('Done Tasks','sum'),
             SLA_Done=('SLA TTO Done','sum'), SLA_TTR=('SLA TTR Done','sum'))
        .reset_index()
    )
    summary['SLA %'] = ((summary['SLA_Done'] + summary['SLA_TTR']) / (summary['Tickets']*2) * 100).round(1)
    top5 = summary.sort_values('SLA %', ascending=False).head(5)
    return summary, top5

def style_sla(df, column='SLA %'):
    def color(val):
        if val >= 90: return "green"
        elif val >= 75: return "orange"
        else: return "red"
    return df.style.applymap(lambda x: f"color:{color(x)}; font-weight:bold", subset=[column])

# -------------------------------
# UNIVERSAL SEARCH
# -------------------------------
def apply_universal_search(df):
    search = st.session_state.get("universal_search", "")
    if search:
        df = df[
            df['Technician Name'].str.contains(search, case=False, na=False) |
            df['Caller Name'].str.contains(search, case=False, na=False) |
            df['Company Name'].str.contains(search, case=False, na=False)
        ]
    return df

# -------------------------------
# FILTER LAST 3 MONTHS
# -------------------------------
def filter_last_3_months(df):
    if 'Start date' in df.columns:
        today = pd.Timestamp.today()
        three_months_ago = today - pd.DateOffset(months=3)
        df_filtered = df[df['Start date'] >= three_months_ago]
        return df_filtered
    return df

# -------------------------------
# PREPARE DATA FUNCTION
# -------------------------------
def prepare_data():
    data = st.session_state.data
    data = clean_data(data)
    data = apply_universal_search(data)
    data = filter_last_3_months(data)
    return data

# -------------------------------
# TOP NAVIGATION BAR
# -------------------------------
# Google-style search bar
st.markdown(
    """
    <style>
    .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
    .search-box { padding:5px; width:400px; border-radius:25px; border:1px solid #ccc; }
    </style>
    <div class="top-bar">
    </div>
    """,
    unsafe_allow_html=True
)

# Bind Streamlit input to session state
st.session_state.universal_search = st.text_input(
    "", value=st.session_state.get("universal_search",""),
    placeholder="Search Technician, Caller, or Company",
    key="search_input", label_visibility="collapsed"
)

# Top navigation buttons
pages = ["Dashboard", "Advanced Analytics", "Data Explorer", "Export Center", "Settings"]
cols = st.columns(len(pages))
for i, pg in enumerate(pages):
    if cols[i].button(pg):
        st.session_state.page = pg

page = st.session_state.get("page", "Dashboard")

# -------------------------------
# PAGE LOGIC
# -------------------------------
if page == "Dashboard":
    data = prepare_data()
    data, monthly_summary = calculate_monthly_summary(data)

    if st.session_state.show_kpis:
        st.markdown("### Key Metrics")
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("Total Tickets", int(monthly_summary['Total Tickets'].sum()))
        c2.metric("Closed Tickets", int(monthly_summary['Closed Tickets'].sum()))
        c3.metric("Pending Tickets", int(monthly_summary['Pending Tickets'].sum()))
        c4.metric("SLA Violations", int(monthly_summary['SLA Violations'].sum()))
        c5.metric("Closure %", f"{monthly_summary['Closure %'].mean():.1f}%")
        c6.metric("SLA Compliance %", f"{monthly_summary['SLA %'].mean():.1f}%")

elif page == "Advanced Analytics":
    data = prepare_data()
    data, monthly_summary = calculate_monthly_summary(data)
    st.markdown("Advanced Analytics Page - Work in Progress")

elif page == "Data Explorer":
    data = prepare_data()
    st.markdown("Data Explorer Page - Work in Progress")

elif page == "Export Center":
    data = prepare_data()
    st.markdown("Export Center Page - Work in Progress")

elif page == "Settings":
    st.markdown("Settings Page - Work in Progress")


