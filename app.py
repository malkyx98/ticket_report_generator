# app.py
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import plotly.express as px
from src.styles import set_style, show_logo, kpi_card
from src.data_processing import clean_name, compute_kpis
from src.ppt_export import create_ppt

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Analytics BI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# CUSTOM STYLE & LOGO
# -------------------------------
set_style()
show_logo()

# -------------------------------
# PAGE TITLE
# -------------------------------
st.title("Analytics BI")
st.markdown(
    "Generate **board-ready ticket KPI reports** with filtering, anonymization, "
    "monthly comparison, and export to **Excel & PowerPoint**."
)

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
st.sidebar.markdown("## 🧭 Navigation")
page_selection = st.sidebar.radio(
    "Select Page",
    ["📊 Dashboard", "📈 Advanced Analytics", "📁 Data Explorer", "📤 Export Center", "⚙️ Settings"]
)

# -------------------------------
# FUNCTION TO LOAD DATA
# -------------------------------
def load_data():
    uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type="xlsx")
    if not uploaded_file:
        st.info("Please upload an Excel file to begin.")
        st.stop()
    df = pd.read_excel(uploaded_file)
    
    # Clean Names
    df["Company Name"] = clean_name(df, "Organization->Name")
    df["Technician Name"] = clean_name(df, "Agent->Full name")
    df["Caller Name"] = clean_name(df, "Caller->Full name")
    
    # Time Processing
    if "Start date" in df.columns:
        df["Start date"] = pd.to_datetime(df["Start date"], errors="coerce")
        df["Month"] = df["Start date"].dt.to_period("M").astype(str)
    else:
        df["Month"] = "Unknown"

    # KPI Computation
    df = compute_kpis(df)
    df["Duration (days)"] = pd.to_numeric(df.get("Duration (days)", 0), errors="coerce").fillna(0)
    
    return df

# -------------------------------
# DASHBOARD PAGE
# -------------------------------
if page_selection == "📊 Dashboard":
    st.markdown("## Upload Ticket Data")
    data = load_data()

    with st.expander("Preview Uploaded Data"):
        st.dataframe(data.head(), use_container_width=True)

    # Data Cleaning & Filtering
    st.markdown("## Data Cleaning & Filtering")
    col1, col2 = st.columns(2)
    with col1:
        remove_companies = st.multiselect("Exclude Companies", data["Company Name"].dropna().unique())
        if remove_companies: data = data[~data["Company Name"].isin(remove_companies)]
    with col2:
        persons = list(set(data["Technician Name"].dropna().tolist() + data["Caller Name"].dropna().tolist()))
        remove_persons = st.multiselect("Exclude Persons", persons)
        if remove_persons: data = data[~data["Technician Name"].isin(remove_persons) & ~data["Caller Name"].isin(remove_persons)]

    # Anonymization
    st.markdown("## Data Anonymization")
    sensitive_cols = st.multiselect("Select columns to anonymize", options=data.columns)
    for col in sensitive_cols:
        data[col] = [f"{col.split('->')[0]} {i+1}" for i in range(len(data))]

    # Time Filter
    months = sorted(data["Month"].dropna().unique(), reverse=True)
    months_count = st.selectbox("Select last N months", [1,2,3,4,6,12], index=2)
    data = data[data["Month"].isin(months[:months_count])]

    # Monthly KPI Summary
    monthly_summary = data.groupby("Month").agg(
        Total_Tickets=("Ref","count"),
        Closed_Tickets=("Done Tasks","sum"),
        Pending_Tickets=("Pending Tasks","sum"),
        SLA_TTO_Done=("SLA TTO Done","sum"),
        SLA_TTR_Done=("SLA TTR Done","sum"),
        Avg_Resolution_Days=("Duration (days)","mean")
    ).reset_index()
    monthly_summary["SLA TTO Violations"] = monthly_summary["Total_Tickets"] - monthly_summary["SLA_TTO_Done"]
    monthly_summary["SLA TTR Violations"] = monthly_summary["Total_Tickets"] - monthly_summary["SLA_TTR_Done"]
    monthly_summary["SLA Violations"] = ((monthly_summary["SLA TTO Violations"] + monthly_summary["SLA TTR Violations"])/2).round(0)
    monthly_summary["Closure %"] = (monthly_summary["Closed_Tickets"]/monthly_summary["Total_Tickets"]*100).round(1)
    monthly_summary["SLA %"] = ((monthly_summary["SLA_TTO_Done"]+monthly_summary["SLA_TTR_Done"])/(2*monthly_summary["Total_Tickets"])*100).round(1)
    monthly_summary["Avg_Resolution_Days"] = monthly_summary["Avg_Resolution_Days"].fillna(0)

    # KPI CARDS
    st.markdown("## Key Metrics")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    kpi_card("Total Tickets", int(monthly_summary["Total_Tickets"].sum()), "#06B6D4", c1)
    kpi_card("Closed Tickets", int(monthly_summary["Closed_Tickets"].sum()), "#22C55E", c2)
    kpi_card("Pending Tickets", int(monthly_summary["Pending_Tickets"].sum()), "#F59E0B", c3)
    kpi_card("SLA Violations", int(monthly_summary["SLA Violations"].sum()), "#EF4444", c4)
    kpi_card("Closure %", f"{monthly_summary['Closure %'].mean():.1f}%", "#0EA5A4", c5)
    kpi_card("SLA Compliance %", f"{monthly_summary['SLA %'].mean():.1f}%", "#06B6D4", c6)

    # Top 5 Technicians
    if "Technician Name" in data.columns:
        st.markdown("## Top 5 Performing Technicians")
        tech_summary = data.groupby("Technician Name").agg(
            Tickets=("Ref","count"), Done=("Done Tasks","sum"),
            SLA_Done=("SLA TTO Done","sum"), SLA_TTR=("SLA TTR Done","sum")
        ).reset_index()
        tech_summary["SLA %"] = ((tech_summary["SLA_Done"]+tech_summary["SLA_TTR"])/(tech_summary["Tickets"]*2)*100).round(1)
        top_techs = tech_summary.sort_values("SLA %", ascending=False).head(5)
        st.plotly_chart(px.bar(top_techs, x="Technician Name", y="SLA %", text="SLA %", color="SLA %", color_continuous_scale="Tealgrn"), use_container_width=True)
        st.dataframe(top_techs[["Technician Name","Tickets","Done","SLA %"]], use_container_width=True)

    # Monthly Summary Table
    st.markdown("## Monthly KPI Summary")
    st.dataframe(monthly_summary, use_container_width=True)

    # Trend Chart
    st.markdown("## Monthly KPI Trend")
    fig_trend = px.line(monthly_summary.sort_values("Month"), x="Month", y=["Closure %","SLA %"], markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

    # EXPORT
    st.markdown("## Export Reports")
    excel_buf = BytesIO()
    with pd.ExcelWriter(excel_buf, engine="xlsxwriter") as writer:
        data.to_excel(writer, sheet_name="Processed_Data", index=False)
        monthly_summary.to_excel(writer, sheet_name="Monthly_Summary", index=False)
        if "tech_summary" in locals(): tech_summary.to_excel(writer, sheet_name="Technician_Summary", index=False)
    excel_buf.seek(0)
    col1, col2 = st.columns(2)
    with col1: st.download_button("Download Excel", excel_buf, "ticket_report.xlsx")
    with col2:
        prs = create_ppt({"Monthly KPI": monthly_summary, "Technician KPI": tech_summary if 'tech_summary' in locals() else pd.DataFrame()})
        ppt_buf = BytesIO()
        prs.save(ppt_buf)
        ppt_buf.seek(0)
        st.download_button("Download PowerPoint", ppt_buf, "ticket_report.pptx")

# -------------------------------
# ADVANCED ANALYTICS PAGE
# -------------------------------
elif page_selection == "📈 Advanced Analytics":
    st.markdown("## Upload Ticket Data for Advanced Analytics")
    data = load_data()

    # Tickets Trend + Rolling Avg
    st.markdown("### Tickets Trend & Rolling Average")
    tickets_monthly = data.groupby("Month")["Ref"].count().reset_index()
    tickets_monthly["Rolling Avg"] = tickets_monthly["Ref"].rolling(3, min_periods=1).mean()
    tickets_monthly["Monthly Growth %"] = tickets_monthly["Ref"].pct_change().fillna(0)*100
    st.plotly_chart(px.line(tickets_monthly, x="Month", y=["Ref","Rolling Avg"], markers=True, title="Tickets Trend & Rolling Avg"), use_container_width=True)
    st.dataframe(tickets_monthly, use_container_width=True)

    # Linear Forecast
    st.markdown("### Linear Forecast")
    tickets_monthly["Month_Num"] = range(len(tickets_monthly))
    coef = np.polyfit(tickets_monthly["Month_Num"], tickets_monthly["Ref"], 1)
    tickets_monthly["Forecast"] = np.polyval(coef, tickets_monthly["Month_Num"])
    st.plotly_chart(px.line(tickets_monthly, x="Month", y=["Ref","Forecast"], markers=True, title="Tickets Forecast"), use_container_width=True)

    # Technician Heatmap
    st.markdown("### Technician Performance Heatmap")
    tech_perf = data.groupby(["Technician Name","Month"]).agg(Tickets=("Ref","count")).reset_index()
    pivot = tech_perf.pivot(index="Technician Name", columns="Month", values="Tickets").fillna(0)
    st.dataframe(pivot, use_container_width=True)

# -------------------------------
# DATA EXPLORER PAGE
# -------------------------------
elif page_selection == "📁 Data Explorer":
    st.markdown("## Upload Ticket Data for Exploration")
    data = load_data()

    search_term = st.text_input("Search Technician, Caller, Company")
    filtered_data = data.copy()
    if search_term:
        filtered_data = filtered_data[
            filtered_data["Technician Name"].str.contains(search_term, case=False, na=False) |
            filtered_data["Caller Name"].str.contains(search_term, case=False, na=False) |
            filtered_data["Company Name"].str.contains(search_term, case=False, na=False)
        ]
    st.dataframe(filtered_data, use_container_width=True)

    # Multi-column filter
    st.markdown("### Filter Columns")
    for col in filtered_data.select_dtypes(include=["object"]).columns:
        vals = filtered_data[col].dropna().unique()
        selected = st.multiselect(f"{col}", options=vals, default=vals)
        filtered_data = filtered_data[filtered_data[col].isin(selected)]
    st.dataframe(filtered_data, use_container_width=True)

    # Download
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        filtered_data.to_excel(writer, sheet_name="Filtered_Data", index=False)
    buf.seek(0)
    st.download_button("Download Filtered Data", buf, "filtered_data.xlsx")

# -------------------------------
# EXPORT CENTER PAGE
# -------------------------------
elif page_selection == "📤 Export Center":
    st.markdown("## Upload Ticket Data for Export")
    data = load_data()

    monthly_summary = data.groupby("Month").agg(
        Total_Tickets=("Ref","count"),
        Closed_Tickets=("Done Tasks","sum"),
        Pending_Tickets=("Pending Tasks","sum"),
        SLA_TTO_Done=("SLA TTO Done","sum"),
        SLA_TTR_Done=("SLA TTR Done","sum")
    ).reset_index()

    # Excel Export
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        data.to_excel(writer, sheet_name="Processed_Data", index=False)
        monthly_summary.to_excel(writer, sheet_name="Monthly_Summary", index=False)
    buf.seek(0)
    st.download_button("⬇️ Download Excel", buf, "analytics_full_report.xlsx")

    # PPT Export
    prs = create_ppt({"Monthly KPI": monthly_summary})
    ppt_buf = BytesIO()
    prs.save(ppt_buf)
    ppt_buf.seek(0)
    st.download_button("⬇️ Download PowerPoint", ppt_buf, "analytics_full_report.pptx")

# -------------------------------
# SETTINGS PAGE
# -------------------------------
elif page_selection == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.markdown("Adjust Dashboard Features and Preferences")
    show_kpis = st.checkbox("Show KPI Cards", value=True)
    show_trends = st.checkbox("Show Trend Charts", value=True)
    theme_color = st.color_picker("KPI Card Color", "#06B6D4")
    st.info("Changes reflect on the Dashboard page in real-time.")
