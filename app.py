# app.py (Universal Data Analysis Tool)
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import plotly.express as px
import plotly.figure_factory as ff
from src.styles import set_style, show_logo
from src.ppt_export import create_ppt

# -------------------------------
# PAGE CONFIG & STYLE
# -------------------------------
st.set_page_config(page_title="Universal Analytics BI", layout="wide")
set_style()
show_logo()

# -------------------------------
# SESSION STATE DEFAULTS
# -------------------------------
defaults = {
    "data": pd.DataFrame(),
    "processed_data": pd.DataFrame(),
    "kpi_columns": {},
    "show_kpis": True,
    "show_trends": True,
    "anonymize_data": False,
    "sensitive_columns": [],
    "theme": "Light",
    "decimal_places": 1,
    "page": "Dashboard",
    "universal_search": ""
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -------------------------------
# FILE UPLOAD
# -------------------------------
st.markdown("## Universal Analytics BI")
uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type="xlsx")
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.session_state.data = df.copy()
    with st.expander("Preview Uploaded Data"):
        st.dataframe(df.head(), use_container_width=True)
elif st.session_state.data.empty:
    st.info("Please upload an Excel file to continue.")
    st.stop()

# -------------------------------
# UNIVERSAL COLUMN MAPPING
# -------------------------------
st.markdown("### Map Your Columns for Analysis")
data_columns = st.session_state.data.columns.tolist()

with st.expander("Column Mapping (optional)"):
    date_col = st.selectbox("Select Date Column (optional)", [None]+data_columns)
    category_col = st.selectbox("Select Category Column (optional)", [None]+data_columns)
    subcategory_col = st.selectbox("Select Subcategory Column (optional)", [None]+data_columns)
    numeric_cols = st.multiselect("Select Numeric Columns for KPIs", data_columns)

st.session_state.kpi_columns = {
    "date": date_col,
    "category": category_col,
    "subcategory": subcategory_col,
    "numeric": numeric_cols
}

# -------------------------------
# DATA PREPARATION
# -------------------------------
def anonymize(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = [f"{col}_{i+1}" for i in range(len(df))]
    return df

def apply_universal_search(df):
    search = st.session_state.get("universal_search", "")
    if search:
        mask = pd.Series(False, index=df.index)
        for col in df.select_dtypes(include="object").columns:
            mask = mask | df[col].str.contains(search, case=False, na=False)
        df = df[mask]
    return df

def filter_last_3_months(df, date_col):
    if date_col and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        today = pd.Timestamp.today()
        three_months_ago = today - pd.DateOffset(months=3)
        df = df[df[date_col] >= three_months_ago]
    return df

def prepare_data():
    df = st.session_state.data.copy()
    df = apply_universal_search(df)
    df = filter_last_3_months(df, st.session_state.kpi_columns.get("date"))
    if st.session_state.anonymize_data:
        df = anonymize(df, st.session_state.sensitive_columns)
    return df

st.session_state.universal_search = st.text_input(
    "Search Text Across All Columns", value=st.session_state.universal_search
)

# -------------------------------
# TOP NAVIGATION
# -------------------------------
pages = ["Dashboard", "Advanced Analytics", "Data Explorer", "Export Center", "Settings"]
cols = st.columns(len(pages))
for i, pg in enumerate(pages):
    if cols[i].button(pg):
        st.session_state.page = pg

page = st.session_state.page

# -------------------------------
# DASHBOARD PAGE
# -------------------------------
if page == "Dashboard":
    df = prepare_data()

    st.markdown("### Key Metrics")
    c1, c2, c3, c4 = st.columns(4)
    total_records = len(df)
    total_numeric_sum = sum([df[col].sum() for col in st.session_state.kpi_columns.get("numeric", []) if col in df.columns])
    avg_numeric = np.mean([df[col].mean() for col in st.session_state.kpi_columns.get("numeric", []) if col in df.columns])
    c1.metric("Total Records", total_records)
    c2.metric("Sum of Numerics", total_numeric_sum)
    c3.metric("Average of Numerics", f"{avg_numeric:.{st.session_state.decimal_places}f}")
    c4.metric("Columns Analyzed", len(st.session_state.kpi_columns.get("numeric", [])))

# -------------------------------
# ADVANCED ANALYTICS PAGE
# -------------------------------
elif page == "Advanced Analytics":
    df = prepare_data()

    st.markdown("### Numeric Column Correlation")
    numeric_cols = st.session_state.kpi_columns.get("numeric", [])
    numeric_cols = [col for col in numeric_cols if col in df.columns]
    if numeric_cols:
        corr = df[numeric_cols].corr()
        fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r')
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("No numeric columns selected for correlation.")

    st.markdown("### Category Trends")
    category_col = st.session_state.kpi_columns.get("category")
    date_col = st.session_state.kpi_columns.get("date")
    if category_col and category_col in df.columns and date_col and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        trend = df.groupby([pd.Grouper(key=date_col, freq='M'), category_col]).size().reset_index(name="Count")
        fig_trend = px.line(trend, x=date_col, y="Count", color=category_col)
        st.plotly_chart(fig_trend, use_container_width=True)

# -------------------------------
# DATA EXPLORER PAGE
# -------------------------------
elif page == "Data Explorer":
    df = prepare_data()
    st.dataframe(df, use_container_width=True)

# -------------------------------
# EXPORT CENTER PAGE
# -------------------------------
elif page == "Export Center":
    df = prepare_data()
    if df.empty:
        st.warning("No data to export.")
        st.stop()

    # Excel Export
    st.markdown("### Download Excel")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Processed_Data', index=False)
    st.download_button("Download Excel", output.getvalue(), "analytics_report.xlsx")

    # PowerPoint Export
    st.markdown("### Download PowerPoint")
    try:
        prs = create_ppt({"Data": df})
        ppt_output = BytesIO()
        prs.save(ppt_output)
        ppt_output.seek(0)
        st.download_button("Download PowerPoint", ppt_output, "analytics_report.pptx")
    except Exception as e:
        st.error(f"Failed to generate PowerPoint: {str(e)}")

# -------------------------------
# SETTINGS PAGE
# -------------------------------
elif page == "Settings":
    st.markdown("### Dashboard Settings")
    st.session_state.show_kpis = st.checkbox("Show KPI Cards", value=st.session_state.show_kpis)
    st.session_state.show_trends = st.checkbox("Show Trends", value=st.session_state.show_trends)
    st.session_state.anonymize_data = st.checkbox("Anonymize Sensitive Data", value=st.session_state.anonymize_data)

    if st.session_state.anonymize_data:
        sensitive_columns = st.multiselect(
            "Select Columns to Anonymize",
            options=st.session_state.data.columns.tolist(),
            default=st.session_state.sensitive_columns
        )
        st.session_state.sensitive_columns = sensitive_columns

    st.session_state.decimal_places = st.slider("Decimal Places", 0, 3, value=st.session_state.decimal_places)
    st.session_state.theme = st.selectbox("Theme", ["Light", "Dark"], index=0 if st.session_state.theme=="Light" else 1)

