# app.py
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from PIL import Image
from src.styles import set_style, show_logo, kpi_card
from src.data_processing import clean_name, compute_kpis
from src.ppt_export import create_ppt
import plotly.express as px
import plotly.figure_factory as ff
import os

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Alayticx BI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# SESSION STATE DEFAULTS
# -----------------------------
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

# -----------------------------
# LOAD LOGO SAFELY
# -----------------------------
logo_path = "logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
else:
    st.warning("Logo file not found! Using placeholder logo.")
    logo = Image.new("RGB", (70, 70), color=(200, 200, 200))

# -----------------------------
# TOP NAVBAR
# -----------------------------
col_logo, col_search, col_nav = st.columns([1, 3, 3])

# Logo + App Name
with col_logo:
    st.image(logo, width=70)
    st.markdown(
        '<h2 style="color:#0B5394; display:inline; margin-left:10px; font-family:sans-serif;">Alayticx BI</h2>',
        unsafe_allow_html=True
    )

# Universal Search Bar
with col_search:
    st.session_state.universal_search = st.text_input(
        "🔍 Search Technician, Caller, or Company",
        value=st.session_state.universal_search,
        key="top_search",
        placeholder="Type to search...",
        help="Search across Technician, Caller, or Company"
    )

# Navigation Buttons
pages = ["Dashboard", "Advanced Analytics", "Data Explorer", "Export Center", "Settings"]
with col_nav:
    btn_cols = st.columns(len(pages))
    for i, pg in enumerate(pages):
        if btn_cols[i].button(pg):
            st.session_state.page = pg

# Horizontal Separator
st.markdown(
    '<hr style="border:2px solid #0B5394; margin-top:10px; margin-bottom:20px;">',
    unsafe_allow_html=True
)

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
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

def apply_universal_search(df):
    search = st.session_state.get("universal_search", "")
    if search:
        df = df[
            df['Technician Name'].str.contains(search, case=False, na=False) |
            df['Caller Name'].str.contains(search, case=False, na=False) |
            df['Company Name'].str.contains(search, case=False, na=False)
        ]
    return df

def filter_last_3_months(df):
    if 'Start date' in df.columns:
        today = pd.Timestamp.today()
        three_months_ago = today - pd.DateOffset(months=3)
        return df[df['Start date'] >= three_months_ago]
    return df

def prepare_data():
    data = st.session_state.data if not st.session_state.data.empty else upload_file()
    data = clean_data(data)
    data = apply_universal_search(data)
    data = filter_last_3_months(data)
    return data

# -----------------------------
# PAGE CONTENT
# -----------------------------
page = st.session_state.get("page", "Dashboard")
st.markdown(f"## 🏠 {page}")
st.markdown("---")

if page == "Dashboard":
    st.markdown('<h1 style="color:#0B5394;">📊 Dashboard Overview</h1>', unsafe_allow_html=True)
    st.markdown('<p>Real-time BI insights at a glance</p>', unsafe_allow_html=True)
    data = prepare_data()
    st.markdown("Dashboard content goes here...", unsafe_allow_html=True)

elif page == "Advanced Analytics":
    st.markdown('<h1 style="color:#0B5394;">📈 Advanced Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p>Explore trends, correlations, and performance metrics</p>', unsafe_allow_html=True)
    data = prepare_data()
    st.markdown("Analytics content goes here...", unsafe_allow_html=True)

elif page == "Data Explorer":
    st.markdown('<h1 style="color:#0B5394;">🔍 Data Explorer</h1>', unsafe_allow_html=True)
    data = prepare_data()
    st.markdown("Data explorer content goes here...", unsafe_allow_html=True)

elif page == "Export Center":
    st.markdown('<h1 style="color:#0B5394;">📤 Export Center</h1>', unsafe_allow_html=True)
    data = prepare_data()
    st.markdown("Export center content goes here...", unsafe_allow_html=True)

elif page == "Settings":
    st.markdown('<h1 style="color:#0B5394;">⚙️ Settings</h1>', unsafe_allow_html=True)
    st.markdown("Settings content goes here...", unsafe_allow_html=True)
