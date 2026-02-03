# src/styles.py
import streamlit as st
from PIL import Image
import os

def set_style():
    """Apply Dark Hacker / Cyber Security Theme"""
    st.markdown(
        """
        <style>
        /* ===============================
           GLOBAL BACKGROUND (DARK TERMINAL)
        ===============================*/
        .stApp {
            background-color: #0B0F14;
            color: #C9D1D9;
            font-family: 'Courier New', monospace;
        }

        /* ===============================
           HEADERS
        ===============================*/
        h1, h2, h3, h4 {
            color: #58F7C5;
            font-weight: 600;
            font-family: 'Courier New', monospace;
        }

        h1 {
            border-bottom: 2px solid #00FF9C;
            padding-bottom: 6px;
            margin-bottom: 20px;
        }

        /* ===============================
           TEXT / PARAGRAPHS
        ===============================*/
        .stMarkdown p {
            color: #9AA4AF;
            font-size: 14px;
        }

        /* ===============================
           KPI CARDS (GLASS TERMINAL STYLE)
        ===============================*/
        .kpi-card {
            background: rgba(20, 25, 35, 0.9);
            border-radius: 10px;
            padding: 18px;
            text-align: center;
            border-left: 4px solid #00FF9C;
            margin-bottom: 16px;
            box-shadow: 0 0 18px rgba(0,255,156,0.25);
            transition: transform 0.2s ease-in-out;
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 28px rgba(0,255,156,0.45);
        }

        .kpi-card h4 {
            font-size: 12px;
            color: #7EE787;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .kpi-card h2 {
            font-size: 30px;
            color: #00FF9C;
            margin: 0;
            text-shadow: 0 0 10px rgba(0,255,156,0.6);
        }

        /* ===============================
           DATAFRAMES
        ===============================*/
        .stDataFrame {
            background-color: #0F141B;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 0 12px rgba(0,0,0,0.6);
        }

        .stDataFrame table {
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
            color: #C9D1D9;
        }

        .stDataFrame th {
            background-color: #00FF9C;
            color: #0B0F14;
            padding: 10px;
            text-align: left;
            font-weight: 700;
        }

        .stDataFrame td {
            padding: 8px;
            border-bottom: 1px solid #1F2937;
        }

        .stDataFrame tr:nth-child(even) {
            background-color: #0B1220;
        }

        .stDataFrame tr:hover {
            background-color: #12203A;
        }

        /* ===============================
           SIDEBAR
        ===============================*/
        section[data-testid="stSidebar"] {
            background-color: #0F141B;
            border-right: 1px solid #00FF9C;
        }

        /* ===============================
           INPUTS
        ===============================*/
        input, textarea, select {
            background-color: #0B1220 !important;
            color: #C9D1D9 !important;
            border-radius: 6px !important;
            border: 1px solid #00FF9C !important;
        }

        /* ===============================
           BUTTONS
        ===============================*/
        button {
            background: linear-gradient(135deg, #00FF9C, #00C8FF) !important;
            color: #0B0F14 !important;
            border-radius: 6px !important;
            padding: 0.55em 1.4em !important;
            font-weight: 700 !important;
            border: none !important;
            box-shadow: 0 0 10px rgba(0,255,156,0.5);
            transition: all 0.2s ease-in-out;
        }

        button:hover {
            box-shadow: 0 0 18px rgba(0,255,156,0.8);
            transform: translateY(-1px);
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
    logo_path = os.path.join(os.getcwd(), "assets", "logo.png")
    try:
        img = Image.open(logo_path)
        st.image(img, width=140)
    except FileNotFoundError:
        st.warning("Logo file not found in assets/logo.png")

def kpi_card(title, value, color="#00FF9C"):
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{color}">
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
    """, unsafe_allow_html=True)

