# src/styles.py
import streamlit as st
from PIL import Image
import os

def set_style():
    """Apply Analytics BI – White Background, Orange Boxes, Dark Blue Text Theme"""
    st.markdown(
        """
        <style>
        /* ===============================
           GLOBAL APP BACKGROUND
        ===============================*/
        .stApp {
            background-color: #FFFFFF;
            color: #0A1F44;  /* Dark blue text */
            font-family: 'Segoe UI', sans-serif;
        }

        /* ===============================
           HEADERS
        ===============================*/
        h1, h2, h3, h4 {
            color: #0A1F44;  /* Dark blue headers */
            font-weight: 600;
        }

        h1 { padding-bottom: 8px; margin-bottom: 20px; }

        /* ===============================
           TEXT
        ===============================*/
        .stMarkdown p {
            color: #0A1F44;  /* Dark blue text */
            font-size: 14px;
        }

        /* ===============================
           KPI CARDS
        ===============================*/
        .kpi-card {
            background-color: #FFA500;  /* Orange boxes */
            border-radius: 12px;
            padding: 18px;
            text-align: center;
            box-shadow: 0 6px 14px rgba(0,0,0,0.15);
            border-left: 6px solid #FF8C00;  /* Darker orange accent */
            margin-bottom: 16px;
        }

        .kpi-card h4 {
            font-size: 13px;
            color: #0A1F44;  /* Dark blue text */
            margin-bottom: 6px;
        }

        .kpi-card h2 {
            font-size: 30px;
            color: #0A1F44;  /* Dark blue text */
            margin: 0;
        }

        /* ===============================
           DATAFRAMES
        ===============================*/
        .stDataFrame {
            background-color: #FFA500;  /* Orange boxes */
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .stDataFrame th {
            background-color: #FF8C00;
            color: #FFFFFF;
            padding: 10px;
            font-weight: 600;
        }

        .stDataFrame td {
            padding: 8px;
            border-bottom: 1px solid #FFB84D;
            color: #0A1F44;  /* Dark blue text */
        }

        .stDataFrame tr:nth-child(even) {
            background-color: #FFD580;  /* Light orange rows */
        }

        .stDataFrame tr:hover {
            background-color: #FFC04D;
        }

        /* ===============================
           SIDEBAR
        ===============================*/
        section[data-testid="stSidebar"] {
            background-color: #FFA500;  /* Orange sidebar */
            padding-top: 1.2rem;
            border-right: 3px solid #FF8C00;
        }

        section[data-testid="stSidebar"] * {
            color: #0A1F44 !important;  /* Dark blue text */
            font-size: 14px;
        }

        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] select {
            background-color: #FFFFFF !important;
            color: #0A1F44 !important;
            border-radius: 6px !important;
            border: 1px solid #0A1F44 !important;
        }

        /* ===============================
           INPUTS (MAIN AREA)
        ===============================*/
        input, textarea, select {
            background-color: #FFFFFF !important;
            color: #0A1F44 !important;
            border-radius: 6px !important;
            border: 1px solid #FFA500 !important;
        }

        /* ===============================
           BUTTONS
        ===============================*/
        button {
            background-color: #FFA500 !important;
            color: #0A1F44 !important;
            border-radius: 8px !important;
            padding: 0.55em 1.4em !important;
            font-weight: 600 !important;
            border: none !important;
            transition: all 0.2s ease-in-out;
        }

        button:hover {
            background-color: #FF8C00 !important;
            box-shadow: 0 6px 16px rgba(0,0,0,0.25);
            transform: translateY(-1px);
        }

        /* ===============================
           DOWNLOAD BUTTONS
        ===============================*/
        div.stDownloadButton > button {
            background-color: #FFA500 !important;
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

