# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

from src.styles import set_style, show_logo, kpi_card
from src.data_processing import clean_name, compute_kpis
from src.ppt_export import create_ppt

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Analytics BI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# STYLE & LOGO
# =====================================================
set_style()
show_logo()

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.checkbox("Dark Mode (experimental)", value=False)

# =====================================================
# TITLE
# =====================================================
st.title("Analytics BI")
st.markdown(
    "Generate **board-ready ticket KPI reports** with filtering, anonymization, "
    "monthly comparison, and export to **Excel & PowerPoint**."
)

# =====================================================
# 1️⃣ FILE UPLOAD
# =====================================================
st.markdown("## Upload Ticket Data")
uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type="xlsx")

if not uploaded_file:
    st.info("Please upload an Excel file to begin.")
    st.stop()

data = pd.read_excel(uploaded_file)

with st.expander("Preview Uploaded Data"):
    st.dataframe(data.head(), use_container_width=True)

# =====================================================
# 2️⃣ DATA CLEANING & FILTERING
# =====================================================
st.markdown("## Data Cleaning & Filtering")

data["Company Name"] = clean_name(data, "Organization->Name")
data["Technician Name"] = clean_name(data, "Agent->Full name")
data["Caller Name"] = clean_name(data, "Caller->Full name")

col1, col2 = st.columns(2)

with col1:
    companies = data["Company Name"].dropna().unique()
    remove_companies = st.multiselect("Exclude Companies", companies)
    if remove_companies:
        data = data[~data["Company Name"].isin(remove_companies)]

with col2:
    persons = list(set(
        data["Technician Name"].dropna().tolist() +
        data["Caller Name"].dropna().tolist()
    ))
    remove_persons = st.multiselect("Exclude Persons", persons)
    if remove_persons:
        data = data[
            ~(data["Technician Name"].isin(remove_persons) |
              data["Caller Name"].isin(remove_persons))
        ]

# =====================================================
# 3️⃣ DATA ANONYMIZATION
# =====================================================
st.markdown("## Data Anonymization")

sensitive_cols = st.multiselect(
    "Select columns to anonymize",
    options=data.columns
)

for col in sensitive_cols:
    data[col] = [f"{col.split('->')[0]} {i+1}" for i in range(len(data))]

# =====================================================
# 4️⃣ TIME FILTERING
# =====================================================
st.markdown("## Time Period")

if "Start date" in data.columns:
    data["Start date"] = pd.to_datetime(data["Start date"], errors="coerce")
    data["Month"] = data["Start date"].dt.to_period("M").astype(str)
else:
    data["Month"] = "Unknown"

months = sorted(data["Month"].dropna().unique(), reverse=True)
months_count = st.selectbox("Select last N months", [1, 2, 3, 4, 6, 12], index=2)

selected_months = months[:months_count]
data = data[data["Month"].isin(selected_months)]

# =====================================================
# 5️⃣ KPI CALCULATION
# =====================================================
data = compute_kpis(data)
data["Duration (days)"] = pd.to_numeric(
    data.get("Duration (days)", 0), errors="coerce"
).fillna(0)

monthly_summary = (
    data.groupby("Month")
    .agg(
        Total_Tickets=("Ref", "count"),
        Closed_Tickets=("Done Tasks", "sum"),
        Pending_Tickets=("Pending Tasks", "sum"),
        SLA_TTO_Done=("SLA TTO Done", "sum"),
        SLA_TTR_Done=("SLA TTR Done", "sum"),
        Avg_Resolution_Days=("Duration (days)", "mean")
    )
    .reset_index()
)

monthly_summary["SLA TTO Violations"] = (
    monthly_summary["Total_Tickets"] - monthly_summary["SLA_TTO_Done"]
)
monthly_summary["SLA TTR Violations"] = (
    monthly_summary["Total_Tickets"] - monthly_summary["SLA_TTR_Done"]
)

monthly_summary["SLA Violations"] = (
    (monthly_summary["SLA TTO Violations"] +
     monthly_summary["SLA TTR Violations"]) / 2
).round(0)

monthly_summary["Closure %"] = (
    monthly_summary["Closed_Tickets"] /
    monthly_summary["Total_Tickets"] * 100
).round(1)

monthly_summary["SLA %"] = (
    (monthly_summary["SLA_TTO_Done"] +
     monthly_summary["SLA_TTR_Done"]) /
    (2 * monthly_summary["Total_Tickets"]) * 100
).round(1)

# =====================================================
# 6️⃣ KPI CARDS
# =====================================================
st.markdown("## Key Metrics")

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    kpi_card("Total Tickets", int(monthly_summary["Total_Tickets"].sum()))
with c2:
    kpi_card("Closed Tickets", int(monthly_summary["Closed_Tickets"].sum()), "#22C55E")
with c3:
    kpi_card("Pending Tickets", int(monthly_summary["Pending_Tickets"].sum()), "#F59E0B")
with c4:
    kpi_card("SLA Violations", int(monthly_summary["SLA Violations"].sum()), "#EF4444")
with c5:
    kpi_card("Closure %", f"{monthly_summary['Closure %'].mean():.1f}%", "#0EA5A4")
with c6:
    kpi_card("SLA Compliance %", f"{monthly_summary['SLA %'].mean():.1f}%", "#06B6D4")

# =====================================================
# 7️⃣ TOP 5 PERFORMERS
# =====================================================
def sla_color(val):
    if val >= 90:
        return "color: green; font-weight: bold"
    elif val >= 75:
        return "color: orange; font-weight: bold"
    return "color: red; font-weight: bold"

def style_sla(df):
    return df.style.applymap(sla_color, subset=["SLA %"])

# Technicians
if "Technician Name" in data.columns:
    st.markdown("## Top 5 Performing Technicians")

    tech_summary = (
        data.groupby("Technician Name")
        .agg(
            Tickets=("Ref", "count"),
            Done=("Done Tasks", "sum"),
            SLA_Done=("SLA TTO Done", "sum"),
            SLA_TTR=("SLA TTR Done", "sum")
        )
        .reset_index()
    )

    tech_summary["SLA %"] = (
        (tech_summary["SLA_Done"] + tech_summary["SLA_TTR"]) /
        (tech_summary["Tickets"] * 2) * 100
    ).round(1)

    top_techs = tech_summary.sort_values("SLA %", ascending=False).head(5)

    st.plotly_chart(
        px.bar(top_techs, x="Technician Name", y="SLA %", text="SLA %"),
        use_container_width=True
    )

    st.dataframe(style_sla(top_techs), use_container_width=True)

# =====================================================
# 8️⃣ MONTHLY SUMMARY TABLE
# =====================================================
st.markdown("## Monthly KPI Summary")
st.dataframe(monthly_summary, use_container_width=True)

# =====================================================
# 9️⃣ KPI TREND
# =====================================================
st.markdown("## Monthly KPI Trend")
trend_fig = px.line(
    monthly_summary.sort_values("Month"),
    x="Month",
    y=["Closure %", "SLA %"],
    markers=True
)
st.plotly_chart(trend_fig, use_container_width=True)

# =====================================================
# 🔟 EXPORT
# =====================================================
st.markdown("## Export Reports")

excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    data.to_excel(writer, sheet_name="Processed_Data", index=False)
    monthly_summary.to_excel(writer, sheet_name="Monthly_Summary", index=False)
excel_buffer.seek(0)

col1, col2 = st.columns(2)

with col1:
    st.download_button("Download Excel", excel_buffer, "ticket_report.xlsx")

with col2:
    prs = create_ppt({"Monthly KPI": monthly_summary})
    ppt_buffer = BytesIO()
    prs.save(ppt_buffer)
    ppt_buffer.seek(0)
    st.download_button("Download PowerPoint", ppt_buffer, "ticket_report.pptx")

