# =====================================================
# app.py – Streamlit Analytics BI Dashboard (Top Nav)
# =====================================================

import streamlit as st
import pandas as pd
from io import BytesIO
from src.styles import set_style, show_logo, kpi_card
from src.data_processing import clean_name, compute_kpis
from src.ppt_export import create_ppt
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np

# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Analytics BI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# CUSTOM STYLE & LOGO
# =====================================================
set_style()
show_logo()

# =====================================================
# SESSION STATE DEFAULTS
# =====================================================
default_state = {
    "data": pd.DataFrame(),
    "monthly_summary": pd.DataFrame(),
    "tech_summary": pd.DataFrame(),
    "caller_summary": pd.DataFrame(),
    "show_kpis": True,
    "show_trends": True,
    "anonymize_data": False,
    "current_page": "Dashboard"
}
for key, default in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = default

# =====================================================
# TOP NAVIGATION BAR
# =====================================================
def top_navigation(pages):
    """Create a top navigation bar with buttons"""
    st.markdown(
        """
        <style>
        .nav-bar button {
            margin-right: 10px;
            background-color: #EF4444;
            color: white;
            border-radius: 6px;
            padding: 0.4em 1em;
            font-weight: 600;
            border: none;
        }
        .nav-bar button:hover {
            background-color: #B91C1C;
        }
        </style>
        """, unsafe_allow_html=True
    )
    cols = st.columns(len(pages))
    selected = None
    for i, page in enumerate(pages):
        if cols[i].button(page, key=f"nav_{page}"):
            selected = page
    return selected

pages = ["Dashboard", "Advanced Analytics", "Data Explorer", "Export Center", "Settings"]
selected_page = top_navigation(pages)

# Default to current session page if no button clicked
if not selected_page:
    selected_page = st.session_state.current_page
st.session_state.current_page = selected_page

# =====================================================
# FILE UPLOAD FUNCTION
# =====================================================
def upload_file():
    st.markdown("## Upload Ticket Data")
    uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type="xlsx")
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.session_state.data = df.copy()
        with st.expander("Preview Uploaded Data"):
            st.dataframe(df.head(), use_container_width=True)
        return df
    st.info("Please upload an Excel file to continue.")
    st.stop()

# =====================================================
# DATA CLEANING & ANONYMIZATION
# =====================================================
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

# =====================================================
# KPI & SUMMARY FUNCTIONS
# =====================================================
def calculate_monthly_summary(df):
    df = df.copy()
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
        .agg(Tickets=('Ref','count'),
             Done=('Done Tasks','sum'),
             SLA_Done=('SLA TTO Done','sum'),
             SLA_TTR=('SLA TTR Done','sum'))
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
# PAGE RENDERING
# =====================================================
if selected_page == "Dashboard":
    st.header("📊 Dashboard Overview")
    data = st.session_state.data if not st.session_state.data.empty else upload_file()
    data = clean_data(data)

    # Filters
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

    # KPI Summary
    data, monthly_summary = calculate_monthly_summary(data)
    st.session_state.data = data
    st.session_state.monthly_summary = monthly_summary

    # KPI Cards
    if st.session_state.show_kpis:
        st.markdown("### Key Metrics")
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("Total Tickets", int(monthly_summary['Total Tickets'].sum()))
        c2.metric("Closed Tickets", int(monthly_summary['Closed Tickets'].sum()))
        c3.metric("Pending Tickets", int(monthly_summary['Pending Tickets'].sum()))
        c4.metric("SLA Violations", int(monthly_summary['SLA Violations'].sum()))
        c5.metric("Closure %", f"{monthly_summary['Closure %'].mean():.1f}%")
        c6.metric("SLA Compliance %", f"{monthly_summary['SLA %'].mean():.1f}%")

    # Top Performers Charts
    if 'Technician Name' in data.columns:
        st.subheader("Top 5 Technicians")
        tech_summary, top_techs = top_performers(data, 'Technician Name')
        st.plotly_chart(px.bar(top_techs, x='Technician Name', y='SLA %', text='SLA %',
                               color='SLA %', color_continuous_scale='Tealgrn'), use_container_width=True)
        st.dataframe(style_sla(top_techs), use_container_width=True)
        st.session_state.tech_summary = tech_summary

    if 'Caller Name' in data.columns:
        st.subheader("Top 5 Callers")
        caller_summary, top_callers = top_performers(data, 'Caller Name')
        st.plotly_chart(px.bar(top_callers, x='Caller Name', y='SLA %', text='SLA %',
                               color='SLA %', color_continuous_scale='Tealgrn'), use_container_width=True)
        st.dataframe(style_sla(top_callers), use_container_width=True)
        st.session_state.caller_summary = caller_summary

    # Monthly Trend Chart
    if st.session_state.show_trends:
        st.subheader("Monthly KPI Trend")
        fig = px.line(monthly_summary.sort_values('Month'), x='Month', y=['Closure %','SLA %'], markers=True)
        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# Remaining pages (Advanced Analytics, Data Explorer, Export Center, Settings)
# =====================================================
# You can keep the existing logic from your current app.py
# but replace 'page' variable with 'selected_page'



