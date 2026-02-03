# =====================================================
# app.py – Streamlit Analytics BI Dashboard
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
    initial_sidebar_state="expanded"
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
    "anonymize_data": False
}
for key, default in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = default

# =====================================================
# SIDEBAR – NAVIGATION
# =====================================================
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Advanced Analytics", "Data Explorer", "Export Center", "Settings"]
)

# Safe session reset
if st.sidebar.button("Reset Session"):
    for key in st.session_state.keys():
        st.session_state[key] = None
    st.experimental_rerun()

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
# DASHBOARD PAGE
# =====================================================
if page == "Dashboard":
    st.header("📊 Dashboard Overview")
    data = st.session_state.data if not st.session_state.data.empty else upload_file()
    data = clean_data(data)

    # -------------------------------
    # FILTERS
    # -------------------------------
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

    # Monthly KPI summary
    data, monthly_summary = calculate_monthly_summary(data)
    st.session_state.data = data
    st.session_state.monthly_summary = monthly_summary

    # KPI CARDS
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
# ADVANCED ANALYTICS PAGE
# =====================================================
elif page == "Advanced Analytics":
    st.header("🔍 Advanced Analytics")
    data = st.session_state.data if not st.session_state.data.empty else upload_file()
    data = clean_data(data)
    data, monthly_summary = calculate_monthly_summary(data)

    st.subheader("SLA vs Resolution Days Scatter")
    if 'Duration (days)' in data.columns and 'SLA TTO Done' in data.columns:
        fig = px.scatter(
            data, x='Duration (days)', y='SLA TTO Done',
            color='Technician Name' if 'Technician Name' in data.columns else None,
            size='Done Tasks' if 'Done Tasks' in data.columns else None,
            hover_data=['Company Name'] if 'Company Name' in data.columns else None
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Technician SLA Heatmap")
    if 'Technician Name' in data.columns and 'Month' in data.columns:
        pivot = data.pivot_table(index='Technician Name', columns='Month', values='SLA TTO Done',
                                 aggfunc='sum', fill_value=0)
        fig_heat = ff.create_annotated_heatmap(z=pivot.values, x=list(pivot.columns), y=list(pivot.index),
                                               colorscale='Viridis', showscale=True)
        st.plotly_chart(fig_heat, use_container_width=True)

# =====================================================
# DATA EXPLORER PAGE
# =====================================================
elif page == "Data Explorer":
    st.header("📂 Data Explorer")
    data = st.session_state.data if not st.session_state.data.empty else upload_file()
    data = clean_data(data)

    search_term = st.text_input("Search Technician, Caller, or Company")
    filtered_data = data[
        data['Technician Name'].str.contains(search_term, case=False, na=False) |
        data['Caller Name'].str.contains(search_term, case=False, na=False) |
        data['Company Name'].str.contains(search_term, case=False, na=False)
    ] if search_term else data
    st.dataframe(filtered_data, use_container_width=True)

    # Download filtered data
    st.markdown("### Download Filtered Data")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_data.to_excel(writer, sheet_name='Filtered_Data', index=False)
    st.download_button("Download Excel", output.getvalue(), "filtered_data.xlsx")

# =====================================================
# EXPORT CENTER PAGE
# =====================================================
elif page == "Export Center":
    st.header("📤 Export Center")
    data = st.session_state.data if not st.session_state.data.empty else upload_file()
    monthly_summary = st.session_state.monthly_summary
    tech_summary = st.session_state.tech_summary
    caller_summary = st.session_state.caller_summary

    st.markdown("### Download Reports")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='Processed_Data', index=False)
        monthly_summary.to_excel(writer, sheet_name='Monthly_Summary', index=False)
        if not tech_summary.empty: tech_summary.to_excel(writer, sheet_name='Technician_Summary', index=False)
        if not caller_summary.empty: caller_summary.to_excel(writer, sheet_name='Caller_Summary', index=False)
    st.download_button("Download Excel", output.getvalue(), "analytics_report.xlsx")

    # PowerPoint export
    prs = create_ppt({
        'Monthly KPI': monthly_summary,
        'Technician-wise KPI': tech_summary,
        'Caller-wise KPI': caller_summary
    })
    ppt_output = BytesIO()
    prs.save(ppt_output)
    ppt_output.seek(0)
    st.download_button("Download PowerPoint", ppt_output, "analytics_report.pptx")

# =====================================================
# SETTINGS PAGE
# =====================================================
elif page == "Settings":
    st.header("⚙️ Settings")
    st.session_state.show_kpis = st.checkbox("Show KPI Cards", value=st.session_state.show_kpis)
    st.session_state.show_trends = st.checkbox("Show Trend Charts", value=st.session_state.show_trends)
    st.session_state.anonymize_data = st.checkbox("Enable Data Anonymization", value=st.session_state.anonymize_data)

