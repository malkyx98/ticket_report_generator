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
st.set_page_config(page_title="Alayticx BI", layout="wide", initial_sidebar_state="collapsed")

# -------------------------------
# CUSTOM STYLE & LOGO
# -------------------------------
set_style()
show_logo()

# -------------------------------
# SESSION STATE DEFAULTS
# -------------------------------
for key, default in {
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
    "show_tooltips": True,
    "universal_search": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ==============================
# GOOGLE-STYLE UNIVERSAL SEARCH BAR AT TOP
# ==============================
st.markdown("""
    <style>
    /* Top sticky search bar */
    .top-search {
        position: sticky;
        top: 0;
        z-index: 999;
        width: 100%;
        background-color: #fff;
        padding: 10px 20px;
        border-bottom: 1px solid #dfe1e5;
        display: flex;
        justify-content: center;
        box-shadow: 0 1px 6px rgba(32,33,36,.28);
    }
    .top-search input {
        width: 60%;
        max-width: 700px;
        border: 1px solid #dfe1e5;
        border-radius: 24px;
        padding: 10px 15px;
        font-size: 16px;
        outline: none;
    }

    /* Top navigation tabs */
    .top-nav {
        position: sticky;
        top: 60px;
        z-index: 998;
        width: 100%;
        background-color: #f8f9fa;
        border-bottom: 1px solid #ccc;
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 10px 0;
    }
    .top-nav button {
        background-color: #e2e6ea;
        border: none;
        padding: 8px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
    }
    .top-nav button:hover {
        background-color: #cfd3d7;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Top Search Bar
# -------------------------------
st.markdown(
    """
    <div class="top-search">
        <input type="text" id="universal_search_input" placeholder="🔍 Search Technician, Caller, or Company">
    </div>
    """,
    unsafe_allow_html=True
)

# Streamlit binding for search input
st.session_state.universal_search = st.text_input(
    "", value=st.session_state.universal_search, placeholder="Search Technician, Caller, or Company"
)

# -------------------------------
# Top Navigation Tabs
# -------------------------------
st.markdown("""
    <div class="top-nav">
        <button onclick="window.location.href='#Dashboard'">Dashboard</button>
        <button onclick="window.location.href='#Advanced Analytics'">Advanced Analytics</button>
        <button onclick="window.location.href='#Data Explorer'">Data Explorer</button>
        <button onclick="window.location.href='#Export Center'">Export Center</button>
        <button onclick="window.location.href='#Settings'">Settings</button>
    </div>
""", unsafe_allow_html=True)

# ==============================
# PAGE LOGIC
# ==============================
# Your existing functions for:
# - upload_file()
# - clean_data()
# - anonymize()
# - calculate_monthly_summary()
# - top_performers()
# - style_sla()
# - apply_universal_search()
# - filter_last_3_months()
# - prepare_data()
# And then handle pages based on selection
# ==============================

page_options = ["Dashboard", "Advanced Analytics", "Data Explorer", "Export Center", "Settings"]
page = st.selectbox("Go to Page", page_options, index=0, key="top_nav_page")  # linked with top nav

# -------------------------------
# Apply universal search filter in all pages
# -------------------------------
def apply_search(df):
    if st.session_state.universal_search:
        df = df[
            df['Technician Name'].str.contains(st.session_state.universal_search, case=False, na=False) |
            df['Caller Name'].str.contains(st.session_state.universal_search, case=False, na=False) |
            df['Company Name'].str.contains(st.session_state.universal_search, case=False, na=False)
        ]
    return df

# Then, inside each page you can do:
# data = prepare_data()
# data = apply_search(data)
# ... rest of your page logic remains the same


