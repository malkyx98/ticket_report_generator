# app.py (Fully Dynamic Universal Analytics Tool)
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
st.set_page_config(page_title="Analytics BI", layout="wide")
set_style()
show_logo()

# -------------------------------
# SESSION STATE DEFAULTS
# -------------------------------
defaults = {
    "data": pd.DataFrame(),
    "processed_data": pd.DataFrame(),
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
# UNIVERSAL SEARCH BAR (Top of Page)
# -------------------------------
st.markdown(
    """
    <style>
    .search-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .search-box {
        width: 60%;
        padding: 10px 20px;
        border-radius: 25px;
        border: 1px solid #ccc;
        font-size: 16px;
    }
    </style>
    <div class="search-container">
        <input class="search-box" placeholder="Search Technician, Caller, or Company" id="universal_search">
    </div>
    """,
    unsafe_allow_html=True
)

# Bind input to Streamlit session state
search_input = st.text_input(
    "", 
    value=st.session_state.get("universal_search", ""), 
    key="universal_search", 
    placeholder="Search Technician, Caller, or Company", 
    label_visibility="collapsed"
)

# Apply universal search
def apply_universal_search(df):
    search = st.session_state.get("universal_search", "")
    if search:
        mask = pd.Series(False, index=df.index)
        for col in ['Company Name', 'Technician Name', 'Caller Name']:
            if col in df.columns:
                mask |= df[col].str.contains(search, case=False, na=False)
        df = df[mask]
    return df
# -------------------------------
# FILE UPLOAD
# -------------------------------
st.markdown("## Analytics BI")
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
# UNIVERSAL SEARCH
# -------------------------------
st.session_state.universal_search = st.text_input(
    "Search Text Across All Columns", value=st.session_state.universal_search
)

def apply_universal_search(df):
    search = st.session_state.get("universal_search", "")
    if search:
        mask = pd.Series(False, index=df.index)
        for col in df.select_dtypes(include="object").columns:
            mask = mask | df[col].str.contains(search, case=False, na=False)
        df = df[mask]
    return df

# -------------------------------
# DATA ANONYMIZATION
# -------------------------------
def anonymize(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = [f"{col}_{i+1}" for i in range(len(df))]
    return df

# -------------------------------
# DATA PREPARATION
# -------------------------------
def prepare_data():
    df = st.session_state.data.copy()
    df = apply_universal_search(df)
    if st.session_state.anonymize_data:
        df = anonymize(df, st.session_state.sensitive_columns)
    return df

# -------------------------------
# TOP NAVIGATION
# -------------------------------
pages = ["Dashboard", "Advanced Analytics", "Data Explorer", "Export Center", "Settings"]
cols = st.columns(len(pages))
for i, pg in enumerate(pages):
    if cols[i].button(pg):
        st.session_state.page = pg

page = st.session_state.page
df = prepare_data()

# -------------------------------
# DASHBOARD PAGE
# -------------------------------
if page == "Dashboard":
    st.markdown("### Key Metrics (Dynamic KPIs)")
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if numeric_cols:
        kpi_cols = numeric_cols[:6]  # show up to 6 numeric columns
        cols_ui = st.columns(len(kpi_cols))
        for i, col_name in enumerate(kpi_cols):
            cols_ui[i].metric(
                label=f"{col_name} (Sum)",
                value=f"{df[col_name].sum():.{st.session_state.decimal_places}f}"
            )
    else:
        st.info("No numeric columns available for KPI display.")

# -------------------------------
# ADVANCED ANALYTICS PAGE
# -------------------------------
elif page == "Advanced Analytics":
    st.markdown("### Numeric Column Correlation (Dynamic)")
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if numeric_cols:
        corr = df[numeric_cols].corr()
        fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r')
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("No numeric columns available for correlation.")

    st.markdown("### Category Trends")
    text_cols = df.select_dtypes(include="object").columns.tolist()
    category_col = st.selectbox("Choose Category Column", options=[None]+text_cols)
    numeric_col = st.selectbox("Choose Numeric Column for Trends", options=[None]+numeric_cols)
    date_cols = df.select_dtypes(include="datetime").columns.tolist()
    date_col = st.selectbox("Choose Date Column (optional)", options=[None]+date_cols)

    if category_col and numeric_col:
        agg_df = df.groupby(category_col)[numeric_col].sum().reset_index()
        fig_bar = px.bar(agg_df, x=category_col, y=numeric_col, color=numeric_col, text=numeric_col)
        st.plotly_chart(fig_bar, use_container_width=True)

    if date_col and category_col and numeric_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        trend_df = df.groupby([pd.Grouper(key=date_col, freq='M'), category_col])[numeric_col].sum().reset_index()
        fig_trend = px.line(trend_df, x=date_col, y=numeric_col, color=category_col)
        st.plotly_chart(fig_trend, use_container_width=True)

# -------------------------------
# DATA EXPLORER PAGE
# -------------------------------
elif page == "Data Explorer":
    st.markdown("### Explore Your Data")
    # Dynamic filters for all text columns
    text_cols = df.select_dtypes(include="object").columns.tolist()
    for col in text_cols:
        unique_vals = df[col].dropna().unique().tolist()
        selected = st.multiselect(f"Filter {col}", unique_vals)
        if selected:
            df = df[df[col].isin(selected)]
    st.dataframe(df, use_container_width=True)

# -------------------------------
# EXPORT CENTER PAGE
# -------------------------------
elif page == "Export Center":
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

