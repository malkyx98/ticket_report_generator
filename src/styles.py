# src/styles.py
import streamlit as st
from PIL import Image
import os

def set_style():
    """Apply Red Theme Style for Analytics BI"""
    st.markdown(
        """
        <style>

        /* ===============================
           GLOBAL BACKGROUND (RED → PINK)
        ===============================*/
        .stApp {
            background: linear-gradient(135deg, #F87171, #FCA5A5);
            color: #1F2937;
            font-family: 'Segoe UI', sans-serif;
        }

        /* ===============================
           HEADERS
        ===============================*/
        h1, h2, h3, h4 {
            color: #1F2937;
            font-weight: 600;
        }

        h1 {
            border-bottom: 3px solid #EF4444;
            padding-bottom: 8px;
            margin-bottom: 20px;
        }

        /* ===============================
           DESCRIPTION TEXT
        ===============================*/
        .stMarkdown p {
            color: #991B1B;
            font-size: 14px;
        }

        /* ===============================
           KPI CARDS
        ===============================*/
        .kpi-card {
            background-color: #FEE2E2;
            border-radius: 10px;
            padding: 18px;
            text-align: center;
            box-shadow: 0 6px 14px rgba(0,0,0,0.15);
            border-left: 6px solid #EF4444;
            margin-bottom: 16px;
        }

        .kpi-card h4 {
            font-size: 13px;
            color: #B91C1C;
            margin-bottom: 6px;
        }

        .kpi-card h2 {
            font-size: 30px;
            color: #991B1B;
            margin: 0;
        }

        /* ===============================
           DATAFRAMES
        ===============================*/
        .stDataFrame {
            background-color: #FEE2E2;
            border-radius: 10px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .stDataFrame table {
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
        }

        .stDataFrame th {
            background-color: #EF4444;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }

        .stDataFrame td {
            padding: 8px;
            border-bottom: 1px solid #FCA5A5;
            color: #991B1B;
        }

        .stDataFrame tr:nth-child(even) {
            background-color: #FECACA;
        }

        .stDataFrame tr:hover {
            background-color: #FCA5A5;
        }

        /* ===============================
           SIDEBAR (SLICERS)
        ===============================*/
        section[data-testid="stSidebar"] {
            background-color: #FEE2E2;
            border-right: 2px solid #EF4444;
        }

        /* ===============================
           INPUTS
        ===============================*/
        input, textarea, select {
            background-color: #FEE2E2 !important;
            color: #991B1B !important;
            border-radius: 6px !important;
            border: 1px solid #EF4444 !important;
        }

        /* ===============================
           BUTTONS
        ===============================*/
        button {
            background: linear-gradient(135deg, #EF4444, #DC2626) !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 0.55em 1.4em !important;
            font-weight: 600 !important;
            border: none !important;
            transition: all 0.2s ease-in-out;
        }

        button:hover {
            background: linear-gradient(135deg, #B91C1C, #991B1B) !important;
            box-shadow: 0 6px 16px rgba(0,0,0,0.25);
            transform: translateY(-1px);
        }

        /* ===============================
           DOWNLOAD BUTTONS
        ===============================*/
        div.stDownloadButton > button {
            background: linear-gradient(135deg, #B91C1C, #DC2626) !important;
        }

        div.stDownloadButton > button:hover {
            background: linear-gradient(135deg, #991B1B, #B91C1C) !important;
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

def kpi_card(title, value, color="#EF4444"):
    """Red KPI card"""
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{color}">
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
    """, unsafe_allow_html=True)
