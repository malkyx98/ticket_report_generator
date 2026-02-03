# src/styles.py
import streamlit as st
from PIL import Image
import os

def set_style():
    """Apply White Hacker-style Theme for Analytics BI"""
    st.markdown(
        """
        <style>

        /* ===============================
           GLOBAL BACKGROUND (WHITE)
        ===============================*/
        .stApp {
            background-color: #FFFFFF;
            color: #0F111A;
            font-family: 'Courier New', monospace;
        }

        /* ===============================
           HEADERS
        ===============================*/
        h1, h2, h3, h4 {
            color: #0F111A;
            font-weight: 600;
            font-family: 'Courier New', monospace;
        }

        h1 {
            border-bottom: 2px solid #0FF;
            padding-bottom: 6px;
            margin-bottom: 20px;
        }

        /* ===============================
           DESCRIPTION TEXT
        ===============================*/
        .stMarkdown p {
            color: #333333;
            font-size: 14px;
        }

        /* ===============================
           KPI CARDS
        ===============================*/
        .kpi-card {
            background-color: #F0F8FF;  /* light blue-ish background */
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 6px 20px rgba(0,255,255,0.3);
            border-left: 6px solid #0FF;
            margin-bottom: 18px;
            transition: transform 0.2s ease-in-out;
        }

        .kpi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 28px rgba(0,255,255,0.5);
        }

        .kpi-card h4 {
            font-size: 13px;
            color: #0F111A;
            margin-bottom: 6px;
        }

        .kpi-card h2 {
            font-size: 32px;
            color: #0FF;
            margin: 0;
            text-shadow: 0 0 6px #0FF;
        }

        /* ===============================
           DATAFRAMES
        ===============================*/
        .stDataFrame {
            background-color: #F9FAFB;
            border-radius: 10px;
            padding: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }

        .stDataFrame table {
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
            color: #0F111A;
        }

        .stDataFrame th {
            background-color: #E0F7FA;
            color: #0F111A;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }

        .stDataFrame td {
            padding: 8px;
            border-bottom: 1px solid #C0C0C0;
        }

        .stDataFrame tr:nth-child(even) {
            background-color: #F0F4F8;
        }

        .stDataFrame tr:hover {
            background-color: #D0EFFA;
        }

        /* ===============================
           SIDEBAR
        ===============================*/
        section[data-testid="stSidebar"] {
            background-color: #F8F9FA;
            border-right: 2px solid #0FF;
        }

        /* ===============================
           INPUTS
        ===============================*/
        input, textarea, select {
            background-color: #F0F8FF !important;
            color: #0F111A !important;
            border-radius: 6px !important;
            border: 1px solid #0FF !important;
        }

        /* ===============================
           BUTTONS
        ===============================*/
        button {
            background: linear-gradient(135deg, #0FF, #39FF14) !important;
            color: #0F111A !important;
            border-radius: 8px !important;
            padding: 0.55em 1.4em !important;
            font-weight: 600 !important;
            border: none !important;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 0 6px #0FF;
        }

        button:hover {
            background: linear-gradient(135deg, #39FF14, #0FF) !important;
            box-shadow: 0 0 12px #39FF14;
            transform: translateY(-1px);
        }

        /* ===============================
           DOWNLOAD BUTTONS
        ===============================*/
        div.stDownloadButton > button {
            background: linear-gradient(135deg, #0FF, #39FF14) !important;
            color: #0F111A !important;
        }

        div.stDownloadButton > button:hover {
            background: linear-gradient(135deg, #39FF14, #0FF) !important;
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

def kpi_card(title, value, color="#0FF"):
    """White Hacker-style KPI card"""
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{color}">
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
    """, unsafe_allow_html=True)
