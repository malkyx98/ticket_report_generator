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
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Alayticx BI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# CUSTOM STYLE & LOGO
# -------------------------------
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
    "default_format": "Excel",
    "show_tooltips": True
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.title("Navigation")

# Universal Search
st.sidebar.markdown("### Universal Search")
universal_search = st.sidebar.text_input("Search Technician, Caller, or Company")

# Page selection
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Advanced Analytics", "Data Explorer", "Export Center", "Settings"]
)

# Reset Session
if st.sidebar.button("Reset Session"):
    for key in st.session_state.keys():
        st.session_state[key] = None
    st.experimental_rerun()

# -------------------------------
# FILE UPLOAD
# -------------------------------
def upload_file():
    st.markdown("## Upload Ticket Data")
    uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type="xlsx")
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.session_state.data = df.copy()
        with st.expander("Preview Uploaded Data"):
            st.dataframe(df.head(), use_container_width=True)
        return df
    else:
        st.info("Please upload an Excel file to continue.")
        st.stop()

# -------------------------------
# DATA CLEANING & ANONYMIZATION
# -------------------------------
def clean_data(df):
    df['Company Name'] = clean_name(df, 'Organization->Name') if 'Organization->Name' in df.columns else ""
    df['Technician Name'] = clean_name(df, 'Agent->Full name') if 'Agent->Full name' in df.columns else ""
    df['Caller Name'] = clean_name(df, 'Caller->Full name') if 'Caller->Full name' in df.columns else ""
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
    if universal_search:
        df = df[
            df['Technician Name'].str.contains(universal_search, case=False, na=False) |
            df['Caller Name'].str.contains(universal_search, case=False, na=False) |
            df['Company Name'].str.contains(universal_search, case=False, na=False)
        ]
    return df

# -------------------------------
# FILTER LAST 3 MONTHS
# -------------------------------
def filter_last_3_months(df):
    if 'Start date' in df.columns:
        df['Start date'] = pd.to_datetime(df['Start date'], errors='coerce')
        today = pd.Timestamp.today()
        three_months_ago = today - pd.DateOffset(months=3)
        df_filtered = df[df['Start date'] >= three_months_ago]
        return df_filtered
    return df

# -------------------------------
# PREPARE DATA
# -------------------------------
def prepare_data():
    data = st.session_state.data if not st.session_state.data.empty else upload_file()
    data = clean_data(data)
    data = apply_universal_search(data)
    data = filter_last_3_months(data)
    return data

# =====================================================
# DASHBOARD PAGE
# =====================================================
if page == "Dashboard":
    st.markdown('<h1 class="page-title">DASHBOARD OVERVIEW</h1>', unsafe_allow_html=True)
    st.markdown('<h4 class="page-subtitle">Your real-time BI insights at a glance</h4>', unsafe_allow_html=True)

    data = prepare_data()

    # Exclude filters
    col1, col2 = st.columns(2)
    with col1:
        companies_to_remove = st.multiselect("Exclude Companies", data['Company Name'].dropna().unique())
        if companies_to_remove:
            data = data[~data['Company Name'].isin(companies_to_remove)]
    with col2:
        persons_options = list(set(data['Technician Name'].tolist() + data['Caller Name'].tolist()))
        persons_to_remove = st.multiselect("Exclude Persons", persons_options)
        if persons_to_remove:
            mask_tech = data['Technician Name'].isin(persons_to_remove)
            mask_caller = data['Caller Name'].isin(persons_to_remove)
            data = data[~(mask_tech | mask_caller)]

    # Anonymization
    if st.session_state.anonymize_data:
        sensitive_columns = st.multiselect("Select columns to anonymize", options=data.columns)
        data = anonymize(data, sensitive_columns)

    # KPI calculations
    data, monthly_summary = calculate_monthly_summary(data)
    st.session_state.data = data
    st.session_state.monthly_summary = monthly_summary

    # SLA Alert
    if 'SLA %' in monthly_summary.columns:
        avg_sla = monthly_summary['SLA %'].mean()
        if avg_sla < 75:
            st.warning(f"⚠️ SLA Compliance is low: {avg_sla:.1f}%")
        elif avg_sla < 90:
            st.info(f"ℹ️ SLA Compliance is moderate: {avg_sla:.1f}%")
        else:
            st.success(f"✅ SLA Compliance is excellent: {avg_sla:.1f}%")

    # KPI Cards
    if st.session_state.show_kpis:
        st.markdown("## Key Metrics")
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("Total Tickets", int(monthly_summary['Total Tickets'].sum()))
        c2.metric("Closed Tickets", int(monthly_summary['Closed Tickets'].sum()))
        c3.metric("Pending Tickets", int(monthly_summary['Pending Tickets'].sum()))
        c4.metric("SLA Violations", int(monthly_summary['SLA Violations'].sum()))
        c5.metric("Closure %", f"{monthly_summary['Closure %'].mean():.1f}%")
        c6.metric("SLA Compliance %", f"{monthly_summary['SLA %'].mean():.1f}%")

    # KPI Summary Table
    st.markdown("## KPI Summary")
    st.dataframe(monthly_summary, use_container_width=True)

    # Pie Chart
    if 'Closed Tickets' in monthly_summary.columns and 'Pending Tickets' in monthly_summary.columns:
        st.markdown("## Ticket Status Distribution")
        ticket_counts = monthly_summary[['Closed Tickets','Pending Tickets']].sum()
        fig_pie = px.pie(
            names=ticket_counts.index,
            values=ticket_counts.values,
            color=ticket_counts.index,
            color_discrete_map={'Closed Tickets':'green','Pending Tickets':'orange'},
            hole=0.3
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Top Performers
    if 'Technician Name' in data.columns:
        st.markdown("## Top 5 Technicians")
        tech_summary, top_techs = top_performers(data, 'Technician Name')
        st.plotly_chart(px.bar(top_techs, x='Technician Name', y='SLA %', text='SLA %', color='SLA %', color_continuous_scale='Tealgrn'))
        st.dataframe(style_sla(top_techs), use_container_width=True)
        st.session_state.tech_summary = tech_summary

    if 'Caller Name' in data.columns:
        st.markdown("## Top 5 Callers")
        caller_summary, top_callers = top_performers(data, 'Caller Name')
        st.plotly_chart(px.bar(top_callers, x='Caller Name', y='SLA %', text='SLA %', color='SLA %', color_continuous_scale='Tealgrn'))
        st.dataframe(style_sla(top_callers), use_container_width=True)
        st.session_state.caller_summary = caller_summary

    # Monthly Trend
    if st.session_state.show_trends:
        st.markdown("## Monthly KPI Trend")
        fig = px.line(monthly_summary.sort_values('Month'), x='Month', y=['Closure %','SLA %'], markers=True)
        st.plotly_chart(fig, use_container_width=True)

    # Download Filtered CSV
    if not data.empty:
        st.markdown("## Download Filtered Data as CSV")
        csv_output = data.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv_output, "filtered_data.csv", "text/csv")

# =====================================================
# The rest of pages (Advanced Analytics, Data Explorer, Export Center, Settings) will follow the same SITS BI structure.
# For brevity, I can complete the full rewritten app with all pages in the next step.
# =====================================================



