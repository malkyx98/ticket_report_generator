# app.py
import streamlit as st
import pandas as pd
from io import BytesIO
from src.styles import set_style, show_logo, kpi_card
from src.data_processing import clean_name, compute_kpis
from src.ppt_export import create_ppt
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Analytics BI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# SIMPLE LOGIN SYSTEM
# -------------------------------
USERS = {
    "admin@test.com": "1234",
    "malki.p@sits.com": "IklaM@9814",
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "login_attempted" not in st.session_state:
    st.session_state.login_attempted = False

def login_ui():
    st.title("Login")
    username_input = st.text_input("Username", key="username_input")
    password_input = st.text_input("Password", type="password", key="password_input")
    login_button = st.button("Login")
    
    if login_button:
        st.session_state.login_attempted = True
        if username_input in USERS and USERS[username_input] == password_input:
            st.session_state.logged_in = True
            st.session_state.username = username_input
        else:
            st.error("Incorrect username or password")

if not st.session_state.logged_in:
    login_ui()
    st.stop()

# -------------------------------
# CUSTOM STYLE & LOGO
# -------------------------------
set_style()
show_logo()

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Advanced Analytics", "Data Explorer", "Export Center", "Settings"]
)

# -------------------------------
# SETTINGS DEFAULTS
# -------------------------------
if 'show_kpis' not in st.session_state:
    st.session_state.show_kpis = True
if 'show_trends' not in st.session_state:
    st.session_state.show_trends = True
if 'anonymize_data' not in st.session_state:
    st.session_state.anonymize_data = False

# -------------------------------
# LOGOUT BUTTON
# -------------------------------
st.sidebar.markdown(f"**Logged in as:** {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.login_attempted = False
    st.experimental_rerun()

# -------------------------------
# FILE UPLOAD FUNCTION
# -------------------------------
def upload_file():
    st.markdown("## Upload Ticket Data")
    uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type="xlsx")
    if uploaded_file:
        data = pd.read_excel(uploaded_file)
        with st.expander("Preview Uploaded Data"):
            st.dataframe(data.head(), use_container_width=True)
        return data
    else:
        st.info("Please upload an Excel file to continue.")
        st.stop()

# ============================
# DASHBOARD PAGE
# ============================
if page == "Dashboard":
    st.title("Dashboard")
    st.markdown("Board-ready KPI reports with filtering, anonymization, trend analysis, and exports.")
    data = upload_file()

    # --- CLEANING ---
    data['Company Name'] = clean_name(data, 'Organization->Name') if 'Organization->Name' in data.columns else ""
    data['Technician Name'] = clean_name(data, 'Agent->Full name') if 'Agent->Full name' in data.columns else ""
    data['Caller Name'] = clean_name(data, 'Caller->Full name') if 'Caller->Full name' in data.columns else ""

    col1, col2 = st.columns(2)
    with col1:
        if 'Company Name' in data.columns:
            companies_to_remove = st.multiselect("Exclude Companies", data['Company Name'].dropna().unique())
            if companies_to_remove:
                data = data[~data['Company Name'].isin(companies_to_remove)]
    with col2:
        persons_options = list(set(
            data.get('Technician Name', pd.Series()).tolist() +
            data.get('Caller Name', pd.Series()).tolist()
        ))
        if persons_options:
            persons_to_remove = st.multiselect("Exclude Persons", persons_options)
            if persons_to_remove:
                mask_tech = data['Technician Name'].isin(persons_to_remove)
                mask_caller = data['Caller Name'].isin(persons_to_remove)
                data = data[~(mask_tech | mask_caller)]

    # --- ANONYMIZATION ---
    if st.session_state.anonymize_data:
        sensitive_columns = st.multiselect("Select columns to anonymize", options=data.columns)
        for col in sensitive_columns:
            data[col] = [f"{col.split('->')[0]} {i+1}" for i in range(len(data))]

    # --- TIME FILTER ---
    if 'Start date' in data.columns:
        data['Start date'] = pd.to_datetime(data['Start date'], errors='coerce')
        data['Month'] = data['Start date'].dt.to_period('M').astype(str)
    else:
        data['Month'] = 'Unknown'
    all_months = sorted(data['Month'].dropna().unique(), reverse=True)
    months_to_compare = st.selectbox("Select last N months", [1,2,3,4,6,12], index=2)
    selected_months = all_months[:months_to_compare]
    data = data[data['Month'].isin(selected_months)]

    # --- KPI CALCULATION ---
    data = compute_kpis(data)
    data['Duration (days)'] = pd.to_numeric(data.get('Duration (days)', 0), errors='coerce').fillna(0)

    monthly_summary = (
        data.groupby('Month')
        .agg({
            'Ref':'count', 'Done Tasks':'sum', 'Pending Tasks':'sum',
            'SLA TTO Done':'sum','SLA TTR Done':'sum','Duration (days)':'mean'
        })
        .rename(columns={
            'Ref':'Total Tickets','Done Tasks':'Closed Tickets','Pending Tasks':'Pending Tickets',
            'Duration (days)':'Avg Resolution Days'
        }).reset_index()
    )

    monthly_summary['SLA TTO Violations'] = monthly_summary['Total Tickets'] - monthly_summary['SLA TTO Done']
    monthly_summary['SLA TTR Violations'] = monthly_summary['Total Tickets'] - monthly_summary['SLA TTR Done']
    monthly_summary['SLA Violations'] = ((monthly_summary['SLA TTO Violations'] + monthly_summary['SLA TTR Violations']) / 2).round(0)
    monthly_summary['Closure %'] = (monthly_summary['Closed Tickets']/monthly_summary['Total Tickets']*100).round(1)
    monthly_summary['SLA %'] = ((monthly_summary['SLA TTO Done'] + monthly_summary['SLA TTR Done'])/(2*monthly_summary['Total Tickets'])*100).round(1)
    monthly_summary['Avg Resolution Days'] = monthly_summary['Avg Resolution Days'].fillna(0)

    # --- KPI CARDS ---
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: kpi_card("Total Tickets", int(monthly_summary['Total Tickets'].sum()))
    with c2: kpi_card("Closed Tickets", int(monthly_summary['Closed Tickets'].sum()), "#22C55E")
    with c3: kpi_card("Pending Tickets", int(monthly_summary['Pending Tickets'].sum()), "#F59E0B")
    with c4: kpi_card("SLA Violations", int(monthly_summary['SLA Violations'].sum()), "#EF4444")
    with c5: kpi_card("Closure %", f"{monthly_summary['Closure %'].mean():.1f}%", "#0EA5A4")
    with c6: kpi_card("SLA Compliance %", f"{monthly_summary['SLA %'].mean():.1f}%", "#06B6D4")

    # --- TOP 5 PERFORMERS ---
    def style_sla(df, column='SLA %'):
        return df.style.applymap(lambda x: f"color:{'green' if x>=90 else 'orange' if x>=75 else 'red'}; font-weight:bold", subset=[column])

    if 'Technician Name' in data.columns:
        tech_summary = data.groupby('Technician Name').agg(
            Tickets=('Ref','count'), Done=('Done Tasks','sum'),
            SLA_Done=('SLA TTO Done','sum'), SLA_TTR=('SLA TTR Done','sum')
        ).reset_index()
        tech_summary['SLA %'] = ((tech_summary['SLA_Done']+tech_summary['SLA_TTR'])/(tech_summary['Tickets']*2)*100).round(1)
        top_techs = tech_summary.sort_values('SLA %', ascending=False).head(5)
        fig_tech = px.bar(top_techs, x='Technician Name', y='SLA %', text='SLA %', color='SLA %', color_continuous_scale='Tealgrn')
        st.plotly_chart(fig_tech, use_container_width=True)
        st.dataframe(style_sla(top_techs[['Technician Name','Tickets','Done','SLA %']]), use_container_width=True)

    if 'Caller Name' in data.columns:
        caller_summary = data.groupby('Caller Name').agg(
            Tickets=('Ref','count'), Done=('Done Tasks','sum'),
            SLA_Done=('SLA TTO Done','sum'), SLA_TTR=('SLA TTR Done','sum')
        ).reset_index()
        caller_summary['SLA %'] = ((caller_summary['SLA_Done']+caller_summary['SLA_TTR'])/(caller_summary['Tickets']*2)*100).round(1)
        top_callers = caller_summary.sort_values('SLA %', ascending=False).head(5)
        fig_callers = px.bar(top_callers, x='Caller Name', y='SLA %', text='SLA %', color='SLA %', color_continuous_scale='Tealgrn')
        st.plotly_chart(fig_callers, use_container_width=True)
        st.dataframe(style_sla(top_callers[['Caller Name','Tickets','Done','SLA %']]), use_container_width=True)

    # --- MONTHLY TABLE & TREND ---
    st.dataframe(monthly_summary, use_container_width=True)
    if st.session_state.show_trends:
        fig_trend = px.line(monthly_summary.sort_values('Month'), x='Month', y=['Closure %','SLA %'], markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- EXPORT ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='Processed_Data', index=False)
        monthly_summary.to_excel(writer, sheet_name='Monthly_Summary', index=False)
        if 'tech_summary' in locals(): tech_summary.to_excel(writer, sheet_name='Technician_Summary', index=False)
        if 'caller_summary' in locals(): caller_summary.to_excel(writer, sheet_name='Caller_Summary', index=False)
    excel_data = output.getvalue()
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Download Excel", excel_data, "ticket_report.xlsx")
    with col2:
        prs = create_ppt({
            'Monthly KPI': monthly_summary,
            'Technician-wise KPI': tech_summary if 'tech_summary' in locals() else pd.DataFrame(),
            'Caller-wise KPI': caller_summary if 'caller_summary' in locals() else pd.DataFrame()
        })
        ppt_output = BytesIO()
        prs.save(ppt_output)
        ppt_output.seek(0)
        st.download_button("Download PowerPoint", ppt_output, "ticket_report.pptx")

# ============================
# ADVANCED ANALYTICS PAGE
# ============================
elif page == "Advanced Analytics":
    st.title("Advanced Analytics")
    data = upload_file()

    # --- PREPARE DATA ---
    data['Company Name'] = clean_name(data, 'Organization->Name') if 'Organization->Name' in data.columns else ""
    data['Technician Name'] = clean_name(data, 'Agent->Full name') if 'Agent->Full name' in data.columns else ""
    data['Caller Name'] = clean_name(data, 'Caller->Full name') if 'Caller->Full name' in data.columns else ""
    data['Month'] = pd.to_datetime(data['Start date'], errors='coerce').dt.to_period('M').astype(str) if 'Start date' in data.columns else 'Unknown'
    data['Duration (days)'] = pd.to_numeric(data.get('Duration (days)',0), errors='coerce').fillna(0)
    data = compute_kpis(data)

    # --- FILTERS ---
    months = sorted(data['Month'].dropna().unique(), reverse=True)
    selected_months = st.multiselect("Select Months", months, default=months[:3])
    if selected_months:
        data = data[data['Month'].isin(selected_months)]

    tech_options = data['Technician Name'].dropna().unique() if 'Technician Name' in data.columns else []
    selected_techs = st.multiselect("Select Technicians", tech_options, default=tech_options)
    if selected_techs:
        data = data[data['Technician Name'].isin(selected_techs)]

    caller_options = data['Caller Name'].dropna().unique() if 'Caller Name' in data.columns else []
    selected_callers = st.multiselect("Select Callers", caller_options, default=caller_options)
    if selected_callers:
        data = data[data['Caller Name'].isin(selected_callers)]

    # --- HEATMAP: Technician vs Month SLA ---
    if 'Technician Name' in data.columns:
        st.markdown("### SLA Heatmap (Technician vs Month)")
        pivot = data.pivot_table(index='Technician Name', columns='Month', values='SLA TTO Done', aggfunc='sum', fill_value=0)
        fig_heatmap = ff.create_annotated_heatmap(
            z=pivot.values,
            x=list(pivot.columns),
            y=list(pivot.index),
            colorscale='Viridis',
            showscale=True
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # --- SCATTER PLOT: SLA vs Duration ---
    if 'Duration (days)' in data.columns and 'SLA TTO Done' in data.columns:
        st.markdown("### SLA vs Resolution Days Scatter")
        fig_scatter = px.scatter(
            data, x='Duration (days)', y='SLA TTO Done',
            color='Technician Name' if 'Technician Name' in data.columns else None,
            size='Done Tasks' if 'Done Tasks' in data.columns else None,
            hover_data=['Company Name','Caller Name'] if 'Company Name' in data.columns else None
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- TREND LINE ---
    monthly_summary = data.groupby('Month').agg(
        Total_Tickets=('Ref','count'),
        Closed_Tickets=('Done Tasks','sum'),
        SLA_TTO_Done=('SLA TTO Done','sum'),
        SLA_TTR_Done=('SLA TTR Done','sum')
    ).reset_index()
    monthly_summary['Closure %'] = (monthly_summary['Closed_Tickets'] / monthly_summary['Total_Tickets'] *100).round(1)
    monthly_summary['SLA %'] = ((monthly_summary['SLA_TTO_Done']+monthly_summary['SLA_TTR_Done'])/(2*monthly_summary['Total_Tickets'])*100).round(1)
    st.markdown("### Monthly KPI Trends")
    fig_trend = px.line(monthly_summary.sort_values('Month'), x='Month', y=['Closure %','SLA %'], markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

