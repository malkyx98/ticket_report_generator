# src/styles.py
import streamlit as st
from PIL import Image
import os

def set_style():
    """Apply Analytics BI – Dark Blue, White & Orange Theme"""
    st.markdown(
        """
        <style>
        /* ===============================
           GLOBAL APP BACKGROUND
        ===============================*/
        .stApp {
            background: linear-gradient(135deg, #0A1F44, #1C3B70);
            color: #FFFFFF;
            font-family: 'Segoe UI', sans-serif;
        }

        /* ===============================
           HEADERS
        ===============================*/
        h1, h2, h3, h4 {
            color: #FFA500;  /* Orange headers */
            font-weight: 600;
        }

        h1 { padding-bottom: 8px; margin-bottom: 20px; }

        /* ===============================
           TEXT
        ===============================*/
        .stMarkdown p {
            color: #E0E0E0;
            font-size: 14px;
        }

        /* ===============================
           KPI CARDS
        ===============================*/
        .kpi-card {
            background-color: #1C3B70;
            border-radius: 12px;
            padding: 18px;
            text-align: center;
            box-shadow: 0 6px 14px rgba(0,0,0,0.3);
            border-left: 6px solid #FFA500;  /* Orange accent */
            margin-bottom: 16px;
        }

        .kpi-card h4 {
            font-size: 13px;
            color: #FFD580;
            margin-bottom: 6px;
        }

        .kpi-card h2 {
            font-size: 30px;
            color: #FFFFFF;
            margin: 0;
        }

        /* ===============================
           DATAFRAMES
        ===============================*/
        .stDataFrame {
            background-color: #0A1F44;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        }

        .stDataFrame th {
            background-color: #1C3B70;
            color: #FFA500;
            padding: 10px;
            font-weight: 600;
        }

        .stDataFrame td {
            padding: 8px;
            border-bottom: 1px solid #333;
            color: #FFFFFF;
        }

        .stDataFrame tr:nth-child(even) {
            background-color: #162D57;
        }

        .stDataFrame tr:hover {
            background-color: #27468B;
        }

        /* ===============================
           SIDEBAR
        ===============================*/
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0A1F44, #1C3B70);
            padding-top: 1.2rem;
            border-right: 3px solid #FFA500;
        }

        section[data-testid="stSidebar"] * {
            color: #FFFFFF !important;
            font-size: 14px;
        }

        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] select {
            background-color: #1C3B70 !important;
            color: #FFFFFF !important;
            border-radius: 6px !important;
            border: 1px solid #FFA500 !important;
        }

        /* ===============================
           INPUTS (MAIN AREA)
        ===============================*/
        input, textarea, select {
            background-color: #27468B !important;
            color: #FFFFFF !important;
            border-radius: 6px !important;
            border: 1px solid #FFA500 !important;
        }

        /* ===============================
           BUTTONS
        ===============================*/
        button {
            background: linear-gradient(135deg, #1C3B70, #0A1F44) !important;
            color: #FFA500 !important;
            border-radius: 8px !important;
            padding: 0.55em 1.4em !important;
            font-weight: 600 !important;
            border: 1px solid #FFA500 !important;
            transition: all 0.2s ease-in-out;
        }

        button:hover {
            background: linear-gradient(135deg, #27468B, #1C3B70) !important;
            box-shadow: 0 6px 16px rgba(0,0,0,0.35);
            transform: translateY(-1px);
        }

        /* ===============================
           DOWNLOAD BUTTONS
        ===============================*/
        div.stDownloadButton > button {
            background: linear-gradient(135deg, #FFA500, #FFB84D) !important;
            color: #0A1F44 !important;
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


def kpi_card(title, value, color="#FFA500"):
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

