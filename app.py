# app.py
import streamlit as st
import pandas as pd
from io import BytesIO
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
from src.styles import set_style, show_logo, kpi_card
from src.data_processing import clean_name, compute_kpis
from src.ppt_export import create_ppt

# -------------------------------
# PAGE CONFIG & STYLE
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
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -------------------------------
# TOP NAVIGATION BAR
# -------------------------------
tabs = ["Dashboard", "Advanced Analytics", "Data Explorer", "Export Center", "Settings"]
tab = st.tabs(tabs)

# ==============================
# GOOGLE-STYLE UNIVERSAL SEARCH BAR
# ==============================
st.markdown("""
    <style>
    .search-box {
        max-width: 700px;
        margin: 10px auto;
        padding: 10px 15px;
        border: 1px solid #dfe1e5;
        border-radius: 24px;
        box-shadow: 0 1px 6px rgba(32,33,36,.28);
        display: flex;
        align-items: center;
        background-color: #fff;
    }
    .search-box input {
        border: none;
        outline: none;
        width: 100%;
        font-size: 16px;
        padding: 5px 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Centered Google-style search bar
search_col1, search_col2, search_col3 = st.columns([1,6,1])
with search_col2:
    universal_search = st.text_input("🔍 Search Technician, Caller, or Company", "", key="universal_search", placeholder="Type to search...", help="Search across Technician, Caller, or Company")


# -------------------------------
# FILE UPLOAD & DATA PREPARATION
# -------------------------------
def upload_file():
    uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type="xlsx")
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.session_state.data = df.copy()
        with st.expander("Preview Uploaded Data"):
            st.dataframe(df.head(), use_container_width=True)
        return df
    else:
        st.stop()

def anonymize(df, columns):
    for col in columns:
        df[col] = [f"{col.split('->')[0]} {i+1}" for i in range(len(df))]
    return df

def prepare_data():
    df = st.session_state.data if not st.session_state.data.empty else upload_file()
    df['Company Name'] = clean_name(df, 'Organization->Name') if 'Organization->Name' in df.columns else ""
    df['Technician Name'] = clean_name(df, 'Agent->Full name') if 'Agent->Full name' in df.columns else ""
    df['Caller Name'] = clean_name(df, 'Caller->Full name') if 'Caller->Full name' in df.columns else ""
    if universal_search:
        df = df[df['Company Name'].str.contains(universal_search, case=False, na=False) |
                df['Technician Name'].str.contains(universal_search, case=False, na=False) |
                df['Caller Name'].str.contains(universal_search, case=False, na=False)]
    # Filter last 3 months
    if 'Start date' in df.columns:
        df['Start date'] = pd.to_datetime(df['Start date'], errors='coerce')
        three_months_ago = pd.Timestamp.today() - pd.DateOffset(months=3)
        df = df[df['Start date'] >= three_months_ago]
    # Anonymize if enabled
    if st.session_state.anonymize_data and hasattr(st.session_state, "sensitive_columns"):
        df = anonymize(df, st.session_state.sensitive_columns)
    return df

# -------------------------------
# KPI & SUMMARY FUNCTIONS
# -------------------------------
def calculate_monthly_summary(df):
    if 'Start date' in df.columns:
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

# =====================================================
# DASHBOARD TAB
# =====================================================
with tab[0]:
    st.header("Dashboard Overview")
    data = prepare_data()
    data, monthly_summary = calculate_monthly_summary(data)
    st.session_state.data = data
    st.session_state.monthly_summary = monthly_summary

    # KPI Cards
    if st.session_state.show_kpis:
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("Total Tickets", int(monthly_summary['Total Tickets'].sum()))
        c2.metric("Closed Tickets", int(monthly_summary['Closed Tickets'].sum()))
        c3.metric("Pending Tickets", int(monthly_summary['Pending Tickets'].sum()))
        c4.metric("SLA Violations", int(monthly_summary['SLA Violations'].sum()))
        c5.metric("Closure %", f"{monthly_summary['Closure %'].mean():.1f}%")
        c6.metric("SLA Compliance %", f"{monthly_summary['SLA %'].mean():.1f}%")

    # Charts
    st.subheader("Ticket Status Distribution")
    ticket_counts = monthly_summary[['Closed Tickets','Pending Tickets']].sum()
    fig_pie = px.pie(names=ticket_counts.index, values=ticket_counts.values,
                     color=ticket_counts.index, color_discrete_map={'Closed Tickets':'green','Pending Tickets':'orange'},
                     hole=0.3)
    st.plotly_chart(fig_pie, use_container_width=True)

# =====================================================
# ADVANCED ANALYTICS TAB
# =====================================================
with tab[1]:
    st.header("Advanced Analytics")
    data = prepare_data()
    data, monthly_summary = calculate_monthly_summary(data)

    st.subheader("SLA vs Resolution Days")
    if 'Duration (days)' in data.columns and 'SLA TTO Done' in data.columns:
        fig = px.scatter(data, x='Duration (days)', y='SLA TTO Done',
                         color='Technician Name' if 'Technician Name' in data.columns else None,
                         size='Done Tasks' if 'Done Tasks' in data.columns else None,
                         hover_data=['Company Name'] if 'Company Name' in data.columns else None)
        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# DATA EXPLORER TAB
# =====================================================
with tab[2]:
    st.header("Data Explorer")
    data = prepare_data()
    st.dataframe(data, use_container_width=True)

# =====================================================
# EXPORT CENTER TAB
# =====================================================
with tab[3]:
    st.header("Export Center")
    data = prepare_data()
    monthly_summary = st.session_state.get("monthly_summary", pd.DataFrame())
    tech_summary = st.session_state.get("tech_summary", pd.DataFrame())
    caller_summary = st.session_state.get("caller_summary", pd.DataFrame())

    st.subheader("Download Excel Reports")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if not data.empty:
            data.to_excel(writer, sheet_name='Processed_Data', index=False)
        if not monthly_summary.empty:
            monthly_summary.to_excel(writer, sheet_name='Monthly_Summary', index=False)
        if tech_summary is not None and not tech_summary.empty:
            tech_summary.to_excel(writer, sheet_name='Technician_Summary', index=False)
        if caller_summary is not None and not caller_summary.empty:
            caller_summary.to_excel(writer, sheet_name='Caller_Summary', index=False)
    st.download_button("Download Excel", output.getvalue(), "analytics_report.xlsx")

# =====================================================
# SETTINGS TAB
# =====================================================
with tab[4]:
    st.header("Settings")
    st.checkbox("Show KPI Cards", value=st.session_state.show_kpis, key="show_kpis")
    st.checkbox("Show Monthly Trends", value=st.session_state.show_trends, key="show_trends")
    st.checkbox("Anonymize Data", value=st.session_state.anonymize_data, key="anonymize_data")
    st.slider("Decimal Places", 0, 3, value=st.session_state.decimal_places, key="decimal_places")
    st.selectbox("Theme", ["Light", "Dark"], index=0 if st.session_state.theme=="Light" else 1, key="theme")

# =====================================================
# The rest of pages (Advanced Analytics, Data Explorer, Export Center, Settings) will follow the same SITS BI structure.
# For brevity, I can complete the full rewritten app with all pages in the next step.
# =====================================================



