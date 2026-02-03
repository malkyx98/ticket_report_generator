# src/styles.py
import streamlit as st
from PIL import Image
import os

def set_style():
    """Apply Professional Blue Analytics Theme"""
    st.markdown(
        """
        <style>
        /* ===============================
           GLOBAL BACKGROUND
        ===============================*/
        .stApp {
            background-color: #F4F7FB; /* soft blue-gray */
            color: #1F2937;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }

        /* ===============================
           HEADERS
        ===============================*/
        h1, h2, h3, h4 {
            color: #1E3A8A; /* deep blue */
            font-weight: 600;
        }

        h1 {
            border-bottom: 3px solid #2563EB;
            padding-bottom: 8px;
            margin-bottom: 22px;
        }

        /* ===============================
           TEXT
        ===============================*/
        .stMarkdown p {
            color: #374151;
            font-size: 14px;
        }

        /* ===============================
           KPI CARDS
        ===============================*/
        .kpi-card {
            background-color: #FFFFFF;
            border-radius: 14px;
            padding: 22px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(37, 99, 235, 0.15);
            border-left: 6px solid #2563EB;
            margin-bottom: 20px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 40px rgba(37, 99, 235, 0.25);
        }

        .kpi-card h4 {
            font-size: 13px;
            color: #64748B;
            margin-bottom: 6px;
        }

        .kpi-card h2 {
            font-size: 34px;
            color: #1E40AF;
            margin: 0;
        }

        /* ===============================
           DATAFRAMES
        ===============================*/
        .stDataFrame {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 14px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        }

        .stDataFrame table {
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
            color: #1F2937;
        }

        .stDataFrame th {
            background-color: #E0E7FF;
            color: #1E3A8A;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }

        .stDataFrame td {
            padding: 8px;
            border-bottom: 1px solid #E5E7EB;
        }

        .stDataFrame tr:nth-child(even) {
            background-color: #F8FAFC;
        }

        .stDataFrame tr:hover {
            background-color: #EEF2FF;
        }

        /* ===============================
           SIDEBAR
        ===============================*/
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 2px solid #2563EB;
            box-shadow: 4px 0 20px rgba(0,0,0,0.05);
        }

        /* ===============================
           INPUTS
        ===============================*/
        input, textarea, select {
            background-color: #FFFFFF !important;
            color: #1F2937 !important;
            border-radius: 8px !important;
            border: 1px solid #CBD5E1 !important;
        }

        /* ===============================
           BUTTONS
        ===============================*/
        button {
            background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
            color: #FFFFFF !important;
            border-radius: 10px !important;
            padding: 0.6em 1.6em !important;
            font-weight: 600 !important;
            border: none !important;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 6px 20px rgba(37,99,235,0.35);
        }

        button:hover {
            background: linear-gradient(135deg, #1D4ED8, #2563EB) !important;
            box-shadow: 0 10px 30px rgba(37,99,235,0.45);
            transform: translateY(-1px);
        }

        /* ===============================
           PAGE PADDING
        ===============================*/
        .block-container {
            padding-top: 1.8rem;
            padding-left: 2.2rem;
            padding-right: 2.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def show_logo():
    logo_path = os.path.join(os.getcwd(), "assets", "logo.png")
    try:
        img = Image.open(logo_path)
        st.image(img, width=150)
    except FileNotFoundError:
        st.warning("Logo file not found in assets/logo.png")

def kpi_card(title, value, color="#2563EB"):
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{color}">
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
    """, unsafe_allow_html=True)

