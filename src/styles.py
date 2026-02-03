import streamlit as st
from PIL import Image
import os

def set_style():
    """Apply White Background Theme with Multiple Accent Colors"""
    st.markdown(
        """
        <style>
        /* ===============================
           GLOBAL BACKGROUND
        ===============================*/
        .stApp {
            background-color: #FFFFFF; /* white background */
            color: #0B0F14; /* dark text for contrast */
            font-family: 'Courier New', monospace;
        }

        /* ===============================
           HEADERS
        ===============================*/
        h1, h2, h3, h4 {
            color: #00C8FF; /* blue accent */
            font-weight: 600;
            font-family: 'Courier New', monospace;
        }
        h1 {
            border-bottom: 2px solid #00FF9C; /* green underline */
            padding-bottom: 6px;
            margin-bottom: 20px;
        }

        /* ===============================
           TEXT / PARAGRAPHS
        ===============================*/
        .stMarkdown p {
            color: #333333; /* dark grey for readability */
            font-size: 14px;
        }

        /* ===============================
           KPI CARDS
        ===============================*/
        .kpi-card {
            background: #F0F4F8; /* light glass effect */
            border-radius: 10px;
            padding: 18px;
            text-align: center;
            border-left: 4px solid #00FF9C; /* default green accent */
            margin-bottom: 16px;
            box-shadow: 0 0 12px rgba(0,0,0,0.1);
            transition: transform 0.2s ease-in-out;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 18px rgba(0,255,156,0.25);
        }
        .kpi-card h4 {
            font-size: 12px;
            color: #FFB347; /* orange accent */
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .kpi-card h2 {
            font-size: 30px;
            color: #FFD700; /* yellow accent */
            margin: 0;
            text-shadow: 0 0 5px rgba(255,215,0,0.4);
        }

        /* ===============================
           DATAFRAMES
        ===============================*/
        .stDataFrame {
            background-color: #FFFFFF; /* white */
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 0 8px rgba(0,0,0,0.05);
        }
        .stDataFrame table {
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
            color: #0B0F14;
        }
        .stDataFrame th {
            background-color: #00C8FF; /* blue accent */
            color: #FFFFFF;
            padding: 10px;
            font-weight: 700;
        }
        .stDataFrame td {
            padding: 8px;
            border-bottom: 1px solid #E0E0E0;
        }
        .stDataFrame tr:nth-child(even) {
            background-color: #F7F9FA;
        }
        .stDataFrame tr:hover {
            background-color: #E8F0FE;
        }

        /* ===============================
           SIDEBAR
        ===============================*/
        section[data-testid="stSidebar"] {
            background-color: #F9FAFB;
            border-right: 1px solid #00FF9C;
        }

        /* ===============================
           INPUTS
        ===============================*/
        input, textarea, select {
            background-color: #FFFFFF !important;
            color: #0B0F14 !important;
            border-radius: 6px !important;
            border: 1px solid #00FF9C !important;
        }

        /* ===============================
           BUTTONS
        ===============================*/
        button {
            background: linear-gradient(135deg, #00FF9C, #00C8FF, #FFB347, #FFD700) !important;
            color: #0B0F14 !important;
            border-radius: 6px !important;
            padding: 0.55em 1.4em !important;
            font-weight: 700 !important;
            border: none !important;
            box-shadow: 0 0 8px rgba(0,255,156,0.3);
            transition: all 0.2s ease-in-out;
        }
        button:hover {
            box-shadow: 0 0 14px rgba(0,255,156,0.5);
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
    """Display a logo from assets folder"""
    logo_path = os.path.join(os.getcwd(), "assets", "logo.png")
    try:
        img = Image.open(logo_path)
        st.image(img, width=140)
    except FileNotFoundError:
        st.warning("Logo file not found in assets/logo.png")


def kpi_card(title, value, color="#00FF9C"):
    """KPI card with dynamic accent color"""
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{color}">
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
    """, unsafe_allow_html=True)



