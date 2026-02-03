# app.py
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from src.styles import set_style, show_logo, kpi_card
from src.data_processing import clean_name, compute_kpis
from src.ppt_export import create_ppt
import plotly.express as px
import plotly.figure_factory as ff

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
    "monthly_summary": pd.DataFrame(),
    "tech_summary": pd.DataFrame(),
    "caller_summary": pd.DataFrame(),
    "show_kpis": True,
    "show_trends": True,
    "anonymize_data": False,
    "sensitive_columns": ['Technician Name', 'Caller Name', 'Company Name'],
    "theme": "Light",
    "decimal_places": 1,
    "page": "Dashboard",
    "universal_search": ""
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -------------------------------
# UNIVERSAL SEARCH BAR (TOP OF PAGE)
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
    """,
    unsafe_allow_html=True
)

st.text_input(
    "",
    value=st.session_state.get("universal_search", ""),
    key="universal_search",
    placeholder="Search any keyword here",
    label_visibility="collapsed"
)

# -------------------------------
# FILE UPLOAD
# -------------------------------
st.markdown("## ")
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
# DATA CLEANING & ANONYMIZATION
# -------------------------------
def clean_data(df):
    if 'Organization->Name' in df.columns:
        df['Company Name'] = clean_name(df, 'Organization->Name')
    else:
        df['Company Name'] = ""
    if 'Agent->Full name' in df.columns:
        df['Technician Name'] = clean_name(df, 'Agent->Full name')
    else:
        df['Technician Name'] = ""
    if 'Caller->Full name' in df.columns:
        df['Caller Name'] = clean_name(df, 'Caller->Full name')
    else:
        df['Caller Name'] = ""
    return df

def anonymize(df, columns):
    for col in columns:
        df[col] = [f"{col.split('->')[0]} {i+1}" for i in range(len(df))]
    return df

# -------------------------------
# KPI & SUMMARY FUNCTIONS
# -------------------------------
def calculate_monthly_summary(df):
    if 'Start date' in df.columns:
        df['Start date'] = pd.to_datetime(df['Start date'], errors='coerce')
        df['Month'] = df['Start date'].dt.to_period('M').astype(str)
    else:
        df['Month'] = 'Unknown'

    df = compute_kpis(df)
    df['Duration (days)'] = pd.to_numeric(df.get('Duration (days)', 0), errors='coerce').fillna(0)

    monthly_summary = (
        df.groupby('Month')
        .agg({
            'Ref': 'count',
            'Done Tasks': 'sum',
            'Pending Tasks': 'sum',
            'SLA TTO Done': 'sum',
            'SLA TTR Done': 'sum',
            'Duration (days)': 'mean'
        })
        .rename(columns={
            'Ref': 'Total Tickets',
            'Done Tasks': 'Closed Tickets',
            'Pending Tasks': 'Pending Tickets',
            'Duration (days)': 'Avg Resolution Days'
        })
        .reset_index()
    )

    monthly_summary['SLA TTO Violations'] = monthly_summary['Total Tickets'] - monthly_summary['SLA TTO Done']
    monthly_summary['SLA TTR Violations'] = monthly_summary['Total Tickets'] - monthly_summary['SLA TTR Done']
    monthly_summary['SLA Violations'] = ((monthly_summary['SLA TTO Violations'] + monthly_summary['SLA TTR Violations']) / 2).round(0)
    monthly_summary['Closure %'] = (monthly_summary['Closed Tickets'] / monthly_summary['Total Tickets'] * 100).round(1)
    monthly_summary['SLA %'] = ((monthly_summary['SLA TTO Done'] + monthly_summary['SLA TTR Done']) / (2 * monthly_summary['Total Tickets']) * 100).round(1)
    monthly_summary['Avg Resolution Days'] = monthly_summary['Avg Resolution Days'].fillna(0)

    return df, monthly_summary

def top_performers(df, role_col):
    summary = (
        df.groupby(role_col)
        .agg(Tickets=('Ref','count'), Done=('Done Tasks','sum'),
             SLA_Done=('SLA TTO Done','sum'), SLA_TTR=('SLA TTR Done','sum'))
        .reset_index()
    )
    summary['SLA %'] = ((summary['SLA_Done'] + summary['SLA_TTR']) / (summary['Tickets']*2) * 100).round(1)
    top5 = summary.sort_values('SLA %', ascending=False).head(5)
    return summary, top5

def style_sla(df, column='SLA %'):
    def color(val):
        if val >= 90: return "green"
        elif val >= 75: return "orange"
        else: return "red"
    return df.style.applymap(lambda x: f"color:{color(x)}; font-weight:bold", subset=[column])

# -------------------------------
# UNIVERSAL SEARCH FUNCTION
# -------------------------------
def apply_universal_search(df):
    search = st.session_state.get("universal_search", "")
    if search:
        for col in ['Technician Name','Caller Name','Company Name']:
            if col not in df.columns:
                df[col] = ""
        df = df[
            df['Technician Name'].str.contains(search, case=False, na=False) |
            df['Caller Name'].str.contains(search, case=False, na=False) |
            df['Company Name'].str.contains(search, case=False, na=False)
        ]
    return df

# -------------------------------
# FILTER LAST 3 MONTHS
# -------------------------------
def filter_last_3_months(df):
    if 'Start date' in df.columns:
        today = pd.Timestamp.today()
        three_months_ago = today - pd.DateOffset(months=3)
        df_filtered = df[df['Start date'] >= three_months_ago]
        return df_filtered
    return df

# -------------------------------
# PREPARE DATA FUNCTION
# -------------------------------
def prepare_data():
    data = st.session_state.data.copy()
    data = clean_data(data)
    data = apply_universal_search(data)
    data = filter_last_3_months(data)
    if st.session_state.anonymize_data and hasattr(st.session_state, 'sensitive_columns'):
        data = anonymize(data, st.session_state.sensitive_columns)
    return data

# -------------------------------
# TOP NAVIGATION
# -------------------------------
pages = ["Dashboard", "Advanced Analytics", "Data Explorer", "Export Center", "Settings"]
cols = st.columns(len(pages))
for i, pg in enumerate(pages):
    if cols[i].button(pg):
        st.session_state.page = pg

page = st.session_state.page

# =====================================================
# DASHBOARD PAGE
# =====================================================
if page == "Dashboard":
    data = prepare_data()
    data, monthly_summary = calculate_monthly_summary(data)

    if st.session_state.show_kpis:
        st.markdown("### Key Metrics")
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("Total Tickets", int(monthly_summary['Total Tickets'].sum()))
        c2.metric("Closed Tickets", int(monthly_summary['Closed Tickets'].sum()))
        c3.metric("Pending Tickets", int(monthly_summary['Pending Tickets'].sum()))
        c4.metric("SLA Violations", int(monthly_summary['SLA Violations'].sum()))
        c5.metric("Closure %", f"{monthly_summary['Closure %'].mean():.1f}%")
        c6.metric("SLA Compliance %", f"{monthly_summary['SLA %'].mean():.1f}%")

# =====================================================
# ADVANCED ANALYTICS PAGE
# =====================================================
elif page == "Advanced Analytics":
    st.markdown('<h1 class="page-title">ADVANCED ANALYTICS</h1>', unsafe_allow_html=True)
    st.markdown('<h4 class="page-subtitle">Explore trends, correlations, and performance metrics</h4>', unsafe_allow_html=True)

    data = prepare_data()
    data, monthly_summary = calculate_monthly_summary(data)

    # SLA vs Duration Scatter
    st.markdown("## SLA vs Resolution Days")
    if 'Duration (days)' in data.columns and 'SLA TTO Done' in data.columns:
        fig = px.scatter(
            data, x='Duration (days)', y='SLA TTO Done',
            color='Technician Name' if 'Technician Name' in data.columns else None,
            size='Done Tasks' if 'Done Tasks' in data.columns else None,
            hover_data=['Company Name'] if 'Company Name' in data.columns else None
        )
        st.plotly_chart(fig, use_container_width=True)

    # Technician SLA Heatmap
    st.markdown("## Technician SLA Heatmap")
    if 'Technician Name' in data.columns and 'Month' in data.columns:
        pivot = data.pivot_table(
            index='Technician Name',
            columns='Month',
            values='SLA TTO Done',
            aggfunc='sum',
            fill_value=0
        )
        fig_heat = ff.create_annotated_heatmap(
            z=pivot.values,
            x=list(pivot.columns),
            y=list(pivot.index),
            colorscale='YlOrRd',
            showscale=True,
            font_colors=['black'],
            annotation_text=pivot.values,
            hoverinfo='z'
        )
        fig_heat.update_layout(
            xaxis=dict(tickangle=-60, tickfont=dict(size=9)),
            yaxis=dict(tickfont=dict(size=8)),
            margin=dict(l=200, r=50, t=50, b=150),
            height=max(600, 30*len(pivot.index)),
        )
        fig_heat.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_heat, use_container_width=True)

    # Correlation Analysis
    st.markdown("## Correlation Matrix")
    numeric_cols = data.select_dtypes(include=np.number).columns.tolist()
    if numeric_cols:
        corr = data[numeric_cols].corr()
        fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("No numeric columns available for correlation analysis.")

# =====================================================
# DATA EXPLORER PAGE
# =====================================================
elif page == "Data Explorer":
    st.markdown('<h1 class="page-title">DATA EXPLORER</h1>', unsafe_allow_html=True)
    st.markdown('<h4 class="page-subtitle">Search, filter, and analyze your ticket data</h4>', unsafe_allow_html=True)

    data = prepare_data()
    data, monthly_summary = calculate_monthly_summary(data)

    if data.empty:
        st.warning("No data available.")
        st.stop()

    # KPI Cards
    total_tickets = len(data)
    closed_tickets = data['Done Tasks'].sum() if 'Done Tasks' in data.columns else 0
    pending_tickets = data['Pending Tasks'].sum() if 'Pending Tasks' in data.columns else 0
    avg_sla = data['SLA %'].mean() if 'SLA %' in data.columns else 0
    avg_duration = data['Duration (days)'].mean() if 'Duration (days)' in data.columns else 0

    st.markdown("### Key Metrics")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Tickets", total_tickets)
    c2.metric("Closed Tickets", closed_tickets)
    c3.metric("Pending Tickets", pending_tickets)
    c4.metric("Avg SLA %", f"{avg_sla:.1f}%")
    c5.metric("Avg Resolution Days", f"{avg_duration:.1f}")
    c6.metric("SLA Violations", total_tickets - closed_tickets)

    # Filters
    st.markdown("### Filters")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        companies = st.multiselect("Company", data['Company Name'].dropna().unique())
    with col2:
        techs = st.multiselect("Technician", data['Technician Name'].dropna().unique())
    with col3:
        callers = st.multiselect("Caller", data['Caller Name'].dropna().unique())
    with col4:
        ticket_status = st.selectbox("Ticket Status", ['All', 'Closed', 'Pending'])

    # Apply filters
    if companies:
        data = data[data['Company Name'].isin(companies)]
    if techs:
        data = data[data['Technician Name'].isin(techs)]
    if callers:
        data = data[data['Caller Name'].isin(callers)]
    if ticket_status == 'Closed':
        data = data[data['Done Tasks'] > 0]
    elif ticket_status == 'Pending':
        data = data[data['Pending Tasks'] > 0]

    if data.empty:
        st.warning("No data matches your filters.")
        st.stop()

    # Charts
    st.markdown("### Ticket Status Distribution")
    fig_pie = px.pie(
        names=['Closed','Pending'],
        values=[closed_tickets, pending_tickets],
        color=['Closed','Pending'],
        color_discrete_map={'Closed':'green','Pending':'orange'},
        hole=0.3
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("### Top 5 Technicians by SLA %")
    if 'Technician Name' in data.columns:
        _, top_techs = top_performers(data, 'Technician Name')
        fig_bar = px.bar(
            top_techs,
            x='Technician Name',
            y='SLA %',
            text='SLA %',
            color='SLA %',
            color_continuous_scale='Tealgrn'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# =====================================================
# EXPORT CENTER PAGE
# =====================================================
elif page == "Export Center":
    st.markdown('<h1 class="page-title">EXPORT CENTER</h1>', unsafe_allow_html=True)
    st.markdown('<h4 class="page-subtitle">Download processed reports and presentations</h4>', unsafe_allow_html=True)

    data = prepare_data()
    monthly_summary = st.session_state.get("monthly_summary", pd.DataFrame())
    tech_summary = st.session_state.get("tech_summary", pd.DataFrame())
    caller_summary = st.session_state.get("caller_summary", pd.DataFrame())

    if data.empty and monthly_summary.empty and (tech_summary.empty if tech_summary is not None else True) \
       and (caller_summary.empty if caller_summary is not None else True):
        st.warning("No data to export.")
        st.stop()

    # Excel Export
    st.markdown("### Download Excel Reports")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if not data.empty:
            data.to_excel(writer, sheet_name='Processed_Data', index=False)
        if not monthly_summary.empty:
            monthly_summary.to_excel(writer, sheet_name='Monthly_Summary', index=False)
        if tech_summary is not None and not tech_summary.empty:
            tech_summary.to_excel(writer, sheet_name='Technician_Summary', index=False)
        if caller_summary is not None and not caller_summary.empty:
            caller_summary.to_excel(writer, sheet_name='Caller_Summary', index=False)
    st.download_button("Download Excel", output.getvalue(), "analytics_report.xlsx")

    # PowerPoint Export
    st.markdown("### Download PowerPoint Presentation")
    tables_dict = {
        'Monthly KPI': monthly_summary,
        'Technician-wise KPI': tech_summary,
        'Caller-wise KPI': caller_summary
    }
    try:
        prs = create_ppt(tables_dict)
        ppt_output = BytesIO()
        prs.save(ppt_output)
        ppt_output.seek(0)
        st.download_button("Download PowerPoint", ppt_output, "analytics_report.pptx")
    except Exception as e:
        st.error(f"Failed to generate PowerPoint: {str(e)}")

# =====================================================
# SETTINGS PAGE
# =====================================================
elif page == "Settings":
    st.markdown('<h1 class="page-title">SETTINGS</h1>', unsafe_allow_html=True)
    st.markdown('<h4 class="page-subtitle">Customize your dashboard preferences</h4>', unsafe_allow_html=True)
    st.markdown("---")

    # Display Options
    st.markdown("### Display Options")
    st.session_state.show_kpis = st.checkbox("Show KPI Cards", value=st.session_state.show_kpis)
    st.session_state.show_trends = st.checkbox("Show Monthly Trends", value=st.session_state.show_trends)

    # Data Privacy
    st.markdown("### Data Privacy")
    st.session_state.anonymize_data = st.checkbox("Anonymize Sensitive Data", value=st.session_state.anonymize_data)
    if st.session_state.anonymize_data and not st.session_state.data.empty:
        sensitive_columns = st.multiselect(
            "Select Columns to Anonymize",
            options=st.session_state.data.columns.tolist(),
            default=st.session_state.sensitive_columns
        )
        st.session_state.sensitive_columns = sensitive_columns

    # Report Formatting
    st.markdown("### Report Formatting")
    st.session_state.decimal_places = st.slider("Decimal Places in Reports", 0, 3, value=st.session_state.decimal_places)

    # Theme
    st.markdown("### Theme & Appearance")
    theme_option = st.selectbox("Select Theme", ["Light", "Dark"], index=0 if st.session_state.theme=="Light" else 1)
    st.session_state.theme = theme_option
    st.markdown(f"**Current Theme:** {st.session_state.theme}")

    # Reset & Apply
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reset All Settings"):
            st.session_state.update({
                "show_kpis": True,
                "show_trends": True,
                "anonymize_data": False,
                "sensitive_columns": ['Technician Name', 'Caller Name', 'Company Name'],
                "decimal_places": 1,
                "theme": "Light"
            })
            st.success("Settings reset to default")
            st.experimental_rerun()
    with col2:
        if st.button("Apply Changes"):
            st.success("Settings applied successfully")
            st.experimental_rerun()


