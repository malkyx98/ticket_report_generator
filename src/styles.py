# src/styles.py
import streamlit as st
from PIL import Image
import os

def set_style():
    """Apply Hacker-style Neon Theme for Analytics BI"""
    st.markdown(
        f"""
        <style>
        /* ===============================
           GLOBAL BACKGROUND (NEON LIGHT)
        ===============================*/
        .stApp {{
            background-color: #EAFDFC;
            color: #0F111A;
            font-family: 'Courier New', monospace;
        }}

        /* ===============================
           HEADERS
        ===============================*/
        h1, h2, h3, h4 {{
            color: #0F111A;
            font-weight: 600;
            font-family: 'Courier New', monospace;
        }}

        h1 {{
            border-bottom: 2px solid #0FF;
            padding-bottom: 6px;
            margin-bottom: 20px;
        }}

        /* ===============================
           DESCRIPTION TEXT
        ===============================*/
        .stMarkdown p {{
            color: #333333;
            font-size: 14px;
        }}

        /* ===============================
           KPI CARDS
        ===============================*/
        .kpi-card {{
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 6px 20px rgba(0,255,255,0.4);
            border-left: 6px solid #0FF;
            margin-bottom: 18px;
            transition: transform 0.2s ease-in-out;
        }}

        .kpi-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 28px rgba(0,255,255,0.6);
        }}

        .kpi-card h4 {{
            font-size: 13px;
            color: #0FF;
            margin-bottom: 6px;
        }}

        .kpi-card h2 {{
            font-size: 32px;
            color: #00CED1;
            margin: 0;
            text-shadow: 0 0 6px #00CED1;
        }}

        /* ===============================
           DATAFRAMES
        ===============================*/
        .stDataFrame {{
            background-color: #FFFFFF;
            border-radius: 10px;
            padding: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}

        .stDataFrame table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
            color: #0F111A;
        }}

        .stDataFrame th {{
            background-color: #0FF;
            color: #0F111A;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }}

        .stDataFrame td {{
            padding: 8px;
            border-bottom: 1px solid #D0F0F0;
        }}

        .stDataFrame tr:nth-child(even) {{
            background-color: #E0F7FA;
        }}

        .stDataFrame tr:hover {{
            background-color: #CFF8FA;
        }}

        /* ===============================
           SIDEBAR
        ===============================*/
        section[data-testid="stSidebar"] {{
            background-color: #FFFFFF;
            border-right: 2px solid #0FF;
        }}

        /* ===============================
           INPUTS
        ===============================*/
        input, textarea, select {{
            background-color: #F0FCFD !important;
            color: #0F111A !important;
            border-radius: 6px !important;
            border: 1px solid #0FF !important;
        }}

        /* ===============================
           BUTTONS
        ===============================*/
        button {{
            background: linear-gradient(135deg, #0FF, #00CED1) !important;
            color: #0F111A !important;
            border-radius: 8px !important;
            padding: 0.55em 1.4em !important;
            font-weight: 600 !important;
            border: none !important;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 0 6px #0FF;
        }}

        button:hover {{
            background: linear-gradient(135deg, #00CED1, #0FF) !important;
            box-shadow: 0 0 12px #0FF;
            transform: translateY(-1px);
        }}

        /* ===============================
           DOWNLOAD BUTTONS
        ===============================*/
        div.stDownloadButton > button {{
            background: linear-gradient(135deg, #0FF, #00CED1) !important;
            color: #0F111A !important;
        }}

        div.stDownloadButton > button:hover {{
            background: linear-gradient(135deg, #00CED1, #0FF) !important;
        }}

        /* ===============================
           PAGE PADDING
        ===============================*/
        .block-container {{
            padding-top: 1.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

def show_logo():
    """Display a logo from assets folder"""
    logo_path = os.path.join(os.getcwd(), "assets", "logo.png")
    try:
        img = Image.open(logo_path)
        st.image(img, width=150)
    except FileNotFoundError:
        st.warning("Logo file not found in assets/logo.png")

def kpi_card(title, value, color="#0FF"):
    """Hacker-style KPI card"""
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{color}">
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
    """, unsafe_allow_html=True)

