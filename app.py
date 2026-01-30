# app.py
import streamlit as st
import pandas as pd
from io import BytesIO
from src.styles import set_style, show_logo, kpi_card
from src.data_processing import clean_name, compute_kpis
from src.ppt_export import create_ppt
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Analytics BI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# SIMPLE LOGIN SYSTEM
# -------------------------------
USERS = {
    "admin@test.com": "1234",
    "malki.p@sits.com": "IklaM@9814",
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "login_attempted" not in st.session_state:
    st.session_state.login_attempted = False

def login_ui():
    st.title("Login")
    username_input = st.text_input("Username", key="username_input")
    password_input = st.text_input("Password", type="password", key="password_input")
    login_button = st.button("Login")
    
    if login_button:
        st.session_state.login_attempted = True
        if username_input in USERS and USERS[username_input] == password_input:
            st.session_state.logged_in = True
            st.session_state.username = username_input
        else:
            st.error("Incorrect username or password")

if not st.session_state.logged_in:
    login_ui()
    st.stop()

# -------------------------------
# CUSTOM STYLE & LOGO
# -------------------------------
set_style()
show_logo()

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Advanced Analytics", "Data Explorer", "Export Center", "Settings"]
)

# -------------------------------
# SETTINGS DEFAULTS
# -------------------------------
if 'show_kpis' not in st.session_state:
    st.session_state.show_kpis = True
if 'show_trends' not in st.session_state:
    st.session_state.show_trends = True
if 'anonymize_data' not in st.session_state:
    st.session_state.anonymize_data = False

# -------------------------------
# LOGOUT BUTTON
# -------------------------------
st.sidebar.markdown(f"**Logged in as:** {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.login_attempted = False
    st.experimental_rerun()

# -------------------------------
# FILE UPLOAD FUNCTION
# -------------------------------
def upload_file():
    st.markdown("## Upload Ticket Data")
    uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type="xlsx")
    if uploaded_file:
        data = pd.read_excel(uploaded_file)
        with st.expander("Preview Uploaded Data"):
            st.dataframe(data.head(), use_container_width=True)
        return data
    else:
        st.info("Please upload an Excel file to continue.")
        st.stop()

# ============================
# DASHBOARD PAGE
# ============================
if page == "Dashboard":
    st.title("Dashboard")
    st.markdown("Board-ready KPI reports with filtering, anonymization, trend analysis, and exports.")
    data = upload_file()

    # --- CLEANING ---
    st.markdown("### Data Cleaning & Filtering")
    if 'Organization->Name' in data.columns:
        data['Company Name'] = clean_name(data, 'Organization->Name')
    else:
        data['Company Name'] = ""

    if 'Agent->Full name' in data.columns:
        data['Technician Name'] = clean_name(data, 'Agent->Full name')
    else:
        data['Technician Name'] = ""

    if 'Caller->Full name' in data.columns:
        data['Caller Name'] = clean_name(data, 'Caller->Full name')
    else:
        data['Caller Name'] = ""

    # --- EXCLUDE COMPANIES / PERSONS ---
    col1, col2 = st.columns(2)
    with col1:
        if 'Company Name' in data.columns:
            companies_to_remove = st.multiselect("Exclude Companies", data['Company Name'].dropna().unique())
            if companies_to_remove:
                data = data[~data['Company Name'].isin(companies_to_remove)]
    with col2:
        persons_options = list(set(
            data.get('Technician Name', pd.Series()).tolist() +
            data.get('Caller Name', pd.Series()).tolist()
        ))
        if persons_options:
            persons_to_remove = st.multiselect("Exclude Persons", persons_options)
            if persons_to_remove:
                mask_tech = data['Technician Name'].isin(persons_to_remove)
                mask_caller = data['Caller Name'].isin(persons_to_remove)
                data = data[~(mask_tech | mask_caller)]

    # --- ANONYMIZATION ---
    if st.session_state.anonymize_data:
        st.markdown("### Data Anonymization")
        sensitive_columns = st.multiselect("Select columns to anonymize", options=data.columns)
        for col in sensitive_columns:
            data[col] = [f"{col.split('->')[0]} {i+1}" for i in range(len(data))]

    # --- TIME FILTER ---
    st.markdown("### Time Period")
    if 'Start date' in data.columns:
        data['Start date'] = pd.to_datetime(data['Start date'], errors='coerce')
        data['Month'] = data['Start date'].dt.to_period('M').astype(str)
    else:
        data['Month'] = 'Unknown'
    all_months = sorted(data['Month'].dropna().unique(), reverse=True)
    months_to_compare = st.selectbox("Select last N months", [1,2,3,4,6,12], index=2)
    selected_months = all_months[:months_to_compare]
    data = data[data['Month'].isin(selected_months)]

    # --- KPI CALCULATION ---
    data = compute_kpis(data)

    # Safe numeric conversion
    numeric_columns = ['Duration (days)', 'SLA TTO Done', 'SLA TTR Done', 'Done Tasks', 'Pending Tasks']
    for col in numeric_columns:
        if col not in data.columns:
            data[col] = 0
        else:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

    monthly_summary = (
        data.groupby('Month')
        .agg({
            'Ref':'count', 'Done Tasks':'sum', 'Pending Tasks':'sum',
            'SLA TTO Done':'sum','SLA TTR Done':'sum','Duration (days)':'mean'
        })
        .rename(columns={
            'Ref':'Total Tickets','Done Tasks':'Closed Tickets','Pending Tasks':'Pending Tickets',
            'Duration (days)':'Avg Resolution Days'
        }).reset_index()
    )

    monthly_summary['SLA TTO Violations'] = monthly_summary['Total Tickets'] - monthly_summary['SLA TTO Done']
    monthly_summary['SLA TTR Violations'] = monthly_summary['Total Tickets'] - monthly_summary['SLA TTR Done']
    monthly_summary['SLA Violations'] = ((monthly_summary['SLA TTO Violations'] + monthly_summary['SLA TTR Violations']) / 2).round(0)
    monthly_summary['Closure %'] = (monthly_summary['Closed Tickets']/monthly_summary['Total Tickets']*100).round(1)
    monthly_summary['SLA %'] = ((monthly_summary['SLA TTO Done'] + monthly_summary['SLA TTR Done'])/(2*monthly_summary['Total Tickets'])*100).round(1)
    monthly_summary['Avg Resolution Days'] = monthly_summary['Avg Resolution Days'].fillna(0)

    # --- KPI CARDS ---
    st.markdown("### Key Metrics")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: kpi_card("Total Tickets", int(monthly_summary['Total Tickets'].sum()))
    with c2: kpi_card("Closed Tickets", int(monthly_summary['Closed Tickets'].sum()), "#22C55E")
    with c3: kpi_card("Pending Tickets", int(monthly_summary['Pending Tickets'].sum()), "#F59E0B")
    with c4: kpi_card("SLA Violations", int(monthly_summary['SLA Violations'].sum()), "#EF4444")
    with c5: kpi_card("Closure %", f"{monthly_summary['Closure %'].mean():.1f}%", "#0EA5A4")
    with c6: kpi_card("SLA Compliance %", f"{monthly_summary['SLA %'].mean():.1f}%", "#06B6D4")

    # --- Export logic (same as previous, omitted here for brevity) ---

# ============================
# DATA EXPLORER PAGE (FIXED)
# ============================
elif page == "Data Explorer":
    st.title("Data Explorer")
    data = upload_file()

    # Only filter if columns exist
    filter_cols = [col for col in ['Technician Name', 'Caller Name', 'Company Name'] if col in data.columns]

    search_term = st.text_input("Search Technician, Caller, or Company")
    if search_term and filter_cols:
        mask = pd.Series(False, index=data.index)
        for col in filter_cols:
            mask |= data[col].astype(str).str.contains(search_term, case=False, na=False)
        filtered_data = data[mask]
    else:
        filtered_data = data

    st.dataframe(filtered_data, use_container_width=True)
    st.markdown("### Download Filtered Data")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_data.to_excel(writer, sheet_name='Filtered_Data', index=False)
    st.download_button("Download Excel", output.getvalue(), "filtered_data.xlsx")
