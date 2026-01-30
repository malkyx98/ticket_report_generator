# src/styles.py
import streamlit as st
from PIL import Image
import os

def set_style():
    """Apply Analytics BI – Cyan Green Enterprise Theme"""
    st.markdown(
        """
        <style>

        /* ===============================
           GLOBAL APP BACKGROUND
        ===============================*/
        .stApp {
            background: linear-gradient(135deg, #00C9A7, #2EE59D);
            color: #0F172A;
            font-family: 'Segoe UI', sans-serif;
        }

        /* ===============================
           HEADERS
        ===============================*/
        h1, h2, h3, h4 {
            color: #0F172A;
            font-weight: 600;
        }

        h1 {
            padding-bottom: 8px;
            margin-bottom: 20px;
        }

        /* ===============================
           TEXT
        ===============================*/
        .stMarkdown p {
            color: #064E3B;
            font-size: 14px;
        }

        /* ===============================
           KPI CARDS
        ===============================*/
        .kpi-card {
            background-color: #ECFEFF;
            border-radius: 12px;
            padding: 18px;
            text-align: center;
            box-shadow: 0 6px 14px rgba(0,0,0,0.15);
            border-left: 6px solid #14B8A6;
            margin-bottom: 16px;
        }

        .kpi-card h4 {
            font-size: 13px;
            color: #047857;
            margin-bottom: 6px;
        }

        .kpi-card h2 {
            font-size: 30px;
            color: #0F766E;
            margin: 0;
        }

        /* ===============================
           DATAFRAMES
        ===============================*/
        .stDataFrame {
            background-color: #ECFEFF;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .stDataFrame th {
            background-color: #0EA5A4;
            color: white;
            padding: 10px;
            font-weight: 600;
        }

        .stDataFrame td {
            padding: 8px;
            border-bottom: 1px solid #A7F3D0;
            color: #064E3B;
        }

        .stDataFrame tr:nth-child(even) {
            background-color: #D1FAE5;
        }

        .stDataFrame tr:hover {
            background-color: #99F6E4;
        }

        /* ===============================
           SIDEBAR – FIXED VISIBILITY
        ===============================*/
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0F766E, #115E59);
            padding-top: 1.2rem;
            border-right: 3px solid #5EEAD4;
        }

        section[data-testid="stSidebar"] * {
            color: #ECFEFF !important;
            font-size: 14px;
        }

        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] select {
            background-color: #ECFEFF !important;
            color: #064E3B !important;
            border-radius: 6px !important;
            border: 1px solid #5EEAD4 !important;
        }

        /* ===============================
           INPUTS (MAIN AREA)
        ===============================*/
        input, textarea, select {
            background-color: #F0FDFA !important;
            color: #064E3B !important;
            border-radius: 6px !important;
            border: 1px solid #5EEAD4 !important;
        }

        /* ===============================
           BUTTONS
        ===============================*/
        button {
            background: linear-gradient(135deg, #06B6D4, #22C55E) !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 0.55em 1.4em !important;
            font-weight: 600 !important;
            border: none !important;
            transition: all 0.2s ease-in-out;
        }

        button:hover {
            background: linear-gradient(135deg, #0891B2, #16A34A) !important;
            box-shadow: 0 6px 16px rgba(0,0,0,0.25);
            transform: translateY(-1px);
        }

        /* ===============================
           DOWNLOAD BUTTONS
        ===============================*/
        div.stDownloadButton > button {
            background: linear-gradient(135deg, #16A34A, #22C55E) !important;
        }

        /* ===============================
           PAGE PADDING
        ===============================*/
        .block-container {
            padding-top: 1.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


def show_logo():
    """Display logo from assets folder"""
    logo_path = os.path.join(os.getcwd(), "assets", "logo.png")
    try:
        img = Image.open(logo_path)
        st.image(img, width=150)
    except FileNotFoundError:
        st.warning("Logo file not found in assets/logo.png")


def kpi_card(title, value, color="#14B8A6"):
    """Analytics BI KPI Card"""
    st.markdown(
        f"""
        <div class="kpi-card" style="border-left-color:{color}">
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

