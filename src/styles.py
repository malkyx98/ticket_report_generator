# src/styles.py
import streamlit as st
from PIL import Image
import os

def set_style():
    """Apply Dark Red Dashboard Theme (fonts unchanged)"""
    st.markdown(
        """
        <style>
        /* ===============================
           GLOBAL BACKGROUND
        ===============================*/
        .stApp {
            background-color: #2B0A0A;
            color: #FFFFFF;
            font-family: 'Courier New', monospace;
        }

        /* ===============================
           HEADERS
        ===============================*/
        h1, h2, h3, h4 {
            color: #FFD6D6;
            font-weight: 600;
            font-family: 'Courier New', monospace;
        }

        h1 {
            border-bottom: 2px solid #FF3D3D;
            padding-bottom: 6px;
            margin-bottom: 20px;
        }

        /* ===============================
           DESCRIPTION TEXT
        ===============================*/
        .stMarkdown p {
            color: #FFCCCC;
            font-size: 14px;
        }

        /* ===============================
           KPI CARDS
        ===============================*/
        .kpi-card {
            background-color: #3E0C0C;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 6px 20px rgba(255,61,61,0.5);
            border-left: 6px solid #FF3D3D;
            margin-bottom: 18px;
            transition: transform 0.2s ease-in-out;
        }

        .kpi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 28px rgba(255,61,61,0.7);
        }

        .kpi-card h4 {
            font-size: 13px;
            color: #FF6F6F;
            margin-bottom: 6px;
        }

        .kpi-card h2 {
            font-size: 32px;
            color: #FF1A1A;
            margin: 0;
            text-shadow: 0 0 6px rgba(255,26,26,0.8);
        }

        /* ===============================
           DATAFRAMES
        ===============================*/
        .stDataFrame {
            background-color: #3E0C0C;
            border-radius: 10px;
            padding: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        }

        .stDataFrame table {
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
            color: #FFFFFF;
        }

        .stDataFrame th {
            background-color: #FF3D3D;
            color: #FFFFFF;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }

        .stDataFrame td {
            padding: 8px;
            border-bottom: 1px solid #FF6F6F;
        }

        .stDataFrame tr:nth-child(even) {
            background-color: #4D1010;
        }

        .stDataFrame tr:hover {
            background-color: #660E0E;
        }

        /* ===============================
           SIDEBAR
        ===============================*/
        section[data-testid="stSidebar"] {
            background-color: #3E0C0C;
            border-right: 2px solid #FF3D3D;
        }

        /* ===============================
           INPUTS
        ===============================*/
        input, textarea, select {
            background-color: #4D1010 !important;
            color: #FFFFFF !important;
            border-radius: 6px !important;
            border: 1px solid #FF3D3D !important;
        }

        /* ===============================
           BUTTONS
        ===============================*/
        button {
            background: linear-gradient(135deg, #FF3D3D, #FF1A1A) !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            padding: 0.55em 1.4em !important;
            font-weight: 600 !important;
            border: none !important;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 0 6px rgba(255,61,61,0.6);
        }

        button:hover {
            background: linear-gradient(135deg, #FF1A1A, #FF3D3D) !important;
            box-shadow: 0 0 12px rgba(255,61,61,0.8);
            transform: translateY(-1px);
        }

        /* ===============================
           DOWNLOAD BUTTONS
        ===============================*/
        div.stDownloadButton > button {
            background: linear-gradient(135deg, #FF3D3D, #FF1A1A) !important;
            color: #FFFFFF !important;
        }

        div.stDownloadButton > button:hover {
            background: linear-gradient(135deg, #FF1A1A, #FF3D3D) !important;
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
    """Display a logo from assets folder"""
    logo_path = os.path.join(os.getcwd(), "assets", "logo.png")
    try:
        img = Image.open(logo_path)
        st.image(img, width=150)
    except FileNotFoundError:
        st.warning("Logo file not found in assets/logo.png")

def kpi_card(title, value, color="#FF3D3D"):
    """Dark Red-theme KPI card"""
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{color}">
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
    """, unsafe_allow_html=True)
