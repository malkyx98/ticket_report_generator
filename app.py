# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from datetime import datetime

from src.styles import set_style, show_logo, kpi_card
from src.data_processing import clean_name, compute_kpis
from src.ppt_export import create_ppt

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Analytics BI", layout="wide", initial_sidebar_state="expanded")

# =====================================================
# STYLE & LOGO
# =====================================================
set_style()
show_logo()

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================
st.sidebar.markdown("## 🧭 Navigation")
page_selection = st.sidebar.radio(
    "Select Page",
    ["📊 Dashboard", "📈 Advanced Analytics", "📁 Data Explorer", "📤 Export Center", "⚙️ Settings"]
)

# =====================================================
# SETTINGS (Dashboard Impact)
# =====================================================
st.sidebar.markdown("## ⚙️ Dashboard Settings")
show_kpis = st.sidebar.checkbox("Show KPI Cards", value=True)
show_trends = st.sidebar.checkbox("Show Trend Charts", value=True)
theme_color = st.sidebar.color_picker("Pick KPI card color", "#06B6D4")

# =====================================================
# PAGE TITLE
# =====================================================
st.title("Analytics BI")
st.markdown(
    "Generate **board-ready ticket KPI reports** with filtering, anonymization, "
    "monthly comparison, and export to **Excel & PowerPoint**."
)

# =====================================================
# ------------------ DASHBOARD PAGE ------------------
# =====================================================
if page_selection == "📊 Dashboard":
    # Upload & Preview
    st.markdown("## Upload Ticket Data")
    uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type="xlsx")
    if not uploaded_file:
        st.info("Please upload an Excel file to begin.")
        st.stop()
    data = pd.read_excel(uploaded_file)
    with st.expander("Preview Uploaded Data"):
        st.dataframe(data.head(), use_container_width=True)

    # Cleaning & Filtering
    data["Company Name"] = clean_name(data, "Organization->Name")
    data["Technician Name"] = clean_name(data, "Agent->Full name")
    data["Caller Name"] = clean_name(data, "Caller->Full name")
    col1, col2 = st.columns(2)
    with col1:
        remove_companies = st.multiselect("Exclude Companies", data["Company Name"].dropna().unique())
        if remove_companies: data = data[~data["Company Name"].isin(remove_companies)]
    with col2:
        persons = list(set(data["Technician Name"].dropna().tolist() + data["Caller Name"].dropna().tolist()))
        remove_persons = st.multiselect("Exclude Persons", persons)
        if remove_persons: data = data[~data["Technician Name"].isin(remove_persons) & ~data["Caller Name"].isin(remove_persons)]

    # Anonymization
    sensitive_cols = st.multiselect("Select columns to anonymize", options=data.columns)
    for col in sensitive_cols:
        data[col] = [f"{col.split('->')[0]} {i+1}" for i in range(len(data))]

    # Time Filtering
    if "Start date" in data.columns:
        data["Start date"] = pd.to_datetime(data["Start date"], errors="coerce")
        data["Month"] = data["Start date"].dt.to_period("M").astype(str)
    else:
        data["Month"] = "Unknown"
    months = sorted(data["Month"].dropna().unique(), reverse=True)
    months_count = st.selectbox("Select last N months", [1, 2, 3, 4, 6, 12], index=2)
    selected_months = months[:months_count]
    data = data[data["Month"].isin(selected_months)]

    # KPI Calculation
    data = compute_kpis(data)
    data["Duration (days)"] = pd.to_numeric(data.get("Duration (days)", 0), errors="coerce").fillna(0)
    monthly_summary = data.groupby("Month").agg(
        Total_Tickets=("Ref", "count"),
        Closed_Tickets=("Done Tasks", "sum"),
        Pending_Tickets=("Pending Tasks", "sum"),
        SLA_TTO_Done=("SLA TTO Done", "sum"),
        SLA_TTR_Done=("SLA TTR Done", "sum"),
        Avg_Resolution_Days=("Duration (days)", "mean")
    ).reset_index()
    monthly_summary["SLA TTO Violations"] = monthly_summary["Total_Tickets"] - monthly_summary["SLA_TTO_Done"]
    monthly_summary["SLA TTR Violations"] = monthly_summary["Total_Tickets"] - monthly_summary["SLA_TTR_Done"]
    monthly_summary["SLA Violations"] = ((monthly_summary["SLA TTO Violations"] + monthly_summary["SLA TTR Violations"]) / 2).round(0)
    monthly_summary["Closure %"] = (monthly_summary["Closed_Tickets"] / monthly_summary["Total_Tickets"] * 100).round(1)
    monthly_summary["SLA %"] = ((monthly_summary["SLA_TTO_Done"] + monthly_summary["SLA_TTR_Done"]) / (2 * monthly_summary["Total_Tickets"]) * 100).round(1)

    # KPI Cards
    if show_kpis:
        st.markdown("## Key Metrics")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        kpi_card("Total Tickets", int(monthly_summary["Total_Tickets"].sum()), theme_color, c1)
        kpi_card("Closed Tickets", int(monthly_summary["Closed_Tickets"].sum()), "#22C55E", c2)
        kpi_card("Pending Tickets", int(monthly_summary["Pending_Tickets"].sum()), "#F59E0B", c3)
        kpi_card("SLA Violations", int(monthly_summary["SLA Violations"].sum()), "#EF4444", c4)
        kpi_card("Closure %", f"{monthly_summary['Closure %'].mean():.1f}%", "#0EA5A4", c5)
        kpi_card("SLA Compliance %", f"{monthly_summary['SLA %'].mean():.1f}%", "#06B6D4", c6)

    # KPI Trend
    if show_trends:
        st.markdown("## Monthly KPI Trend")
        trend_fig = px.line(monthly_summary.sort_values("Month"), x="Month", y=["Closure %", "SLA %"], markers=True)
        st.plotly_chart(trend_fig, use_container_width=True)

# =====================================================
# ------------------ ADVANCED ANALYTICS ------------------
# =====================================================
elif page_selection == "📈 Advanced Analytics":
    st.title("📈 Advanced Analytics")
    st.markdown("Interactive trend analysis, forecasting, and heatmaps.")

    if "data" in locals():
        # Tickets rolling average & growth
        tickets_monthly = data.groupby("Month")["Ref"].count().reset_index()
        tickets_monthly["Rolling Avg"] = tickets_monthly["Ref"].rolling(3, min_periods=1).mean()
        tickets_monthly["Monthly Growth %"] = tickets_monthly["Ref"].pct_change().fillna(0) * 100
        st.plotly_chart(px.line(tickets_monthly, x="Month", y=["Ref", "Rolling Avg"], markers=True, title="Tickets Trend & Rolling Avg"))
        st.dataframe(tickets_monthly)

        # Forecast linear trend
        tickets_monthly["Month_Num"] = range(len(tickets_monthly))
        coef = np.polyfit(tickets_monthly["Month_Num"], tickets_monthly["Ref"], 1)
        tickets_monthly["Forecast"] = np.polyval(coef, tickets_monthly["Month_Num"])
        st.plotly_chart(px.line(tickets_monthly, x="Month", y=["Ref", "Forecast"], markers=True, title="Tickets Forecast"))

        # Technician performance heatmap
        tech_perf = data.groupby(["Technician Name", "Month"]).agg(Tickets=("Ref","count")).reset_index()
        pivot = tech_perf.pivot(index="Technician Name", columns="Month", values="Tickets").fillna(0)
        st.markdown("### Technician Monthly Performance")
        st.dataframe(pivot)

# =====================================================
# ------------------ DATA EXPLORER ------------------
# =====================================================
elif page_selection == "📁 Data Explorer":
    st.title("📁 Data Explorer")
    st.markdown("Search, filter, sort, and export raw ticket data.")
    if "data" in locals():
        search_term = st.text_input("Search Technician, Caller, Company")
        filtered_data = data.copy()
        if search_term:
            filtered_data = filtered_data[
                filtered_data["Technician Name"].str.contains(search_term, case=False, na=False) |
                filtered_data["Caller Name"].str.contains(search_term, case=False, na=False) |
                filtered_data["Company Name"].str.contains(search_term, case=False, na=False)
            ]
        st.dataframe(filtered_data, use_container_width=True)

        # Multi-column filtering
        st.markdown("### Column Filters")
        for col in filtered_data.select_dtypes(include=["object"]).columns:
            vals = filtered_data[col].dropna().unique()
            selected = st.multiselect(f"{col}", options=vals, default=vals)
            filtered_data = filtered_data[filtered_data[col].isin(selected)]
        st.dataframe(filtered_data, use_container_width=True)

        # Export filtered data
        export_buf = BytesIO()
        with pd.ExcelWriter(export_buf, engine="xlsxwriter") as writer:
            filtered_data.to_excel(writer, sheet_name="Filtered_Data", index=False)
        export_buf.seek(0)
        st.download_button("Download Filtered Data", export_buf, "filtered_data.xlsx")

# =====================================================
# ------------------ EXPORT CENTER ------------------
# =====================================================
elif page_selection == "📤 Export Center":
    st.title("📤 Export Center")
    st.markdown("Download processed datasets and KPI summaries.")
    if "data" in locals() and "monthly_summary" in locals():
        full_buf = BytesIO()
        with pd.ExcelWriter(full_buf, engine="xlsxwriter") as writer:
            data.to_excel(writer, sheet_name="Processed_Data", index=False)
            monthly_summary.to_excel(writer, sheet_name="Monthly_Summary", index=False)
        full_buf.seek(0)
        st.download_button("⬇️ Download Full Excel", full_buf, "analytics_full_report.xlsx")

        prs = create_ppt({"Monthly KPI": monthly_summary})
        ppt_buf = BytesIO()
        prs.save(ppt_buf)
        ppt_buf.seek(0)
        st.download_button("⬇️ Download Full PowerPoint", ppt_buf, "analytics_full_report.pptx")

# =====================================================
# ------------------ SETTINGS ------------------
# =====================================================
elif page_selection == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.markdown("Adjust Dashboard Features")
    show_kpis = st.checkbox("Show KPI Cards", value=show_kpis)
    show_trends = st.checkbox("Show Trend Charts", value=show_trends)
    theme_color = st.color_picker("KPI Card Color", value=theme_color)
    st.info("Changes reflect on Dashboard page in real-time.")
