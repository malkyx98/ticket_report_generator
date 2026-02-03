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
st.set_page_config(page_title="Alayticx BI", layout="wide", initial_sidebar_state="collapsed")

# -------------------------------
# CUSTOM STYLE & LOGO
# -------------------------------
set_style()
show_logo()

# -------------------------------
# SESSION STATE DEFAULTS
# -------------------------------
for key, default in {
    "data": pd.DataFrame(),
    "monthly_summary": pd.DataFrame(),
    "tech_summary": pd.DataFrame(),
    "caller_summary": pd.DataFrame(),
    "show_kpis": True,
    "show_trends": True,
    "anonymize_data": False,
    "theme": "Light",
    "decimal_places": 1,
    "default_format": "Excel",
    "show_tooltips": True,
    "universal_search": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ==============================
# GOOGLE-STYLE UNIVERSAL SEARCH BAR AT TOP
# ==============================
st.markdown("""
    <style>
    /* Top sticky search bar */
    .top-search {
        position: sticky;
        top: 0;
        z-index: 999;
        width: 100%;
        background-color: #fff;
        padding: 10px 20px;
        border-bottom: 1px solid #dfe1e5;
        display: flex;
        justify-content: center;
        box-shadow: 0 1px 6px rgba(32,33,36,.28);
    }
    .top-search input {
        width: 60%;
        max-width: 700px;
        border: 1px solid #dfe1e5;
        border-radius: 24px;
        padding: 10px 15px;
        font-size: 16px;
        outline: none;
    }

    /* Top navigation tabs */
    .top-nav {
        position: sticky;
        top: 60px;
        z-index: 998;
        width: 100%;
        background-color: #f8f9fa;
        border-bottom: 1px solid #ccc;
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 10px 0;
    }
    .top-nav button {
        background-color: #e2e6ea;
        border: none;
        padding: 8px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
    }
    .top-nav button:hover {
        background-color: #cfd3d7;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Top Search Bar
# -------------------------------
st.markdown(
    """
    <div class="top-search">
        <input type="text" id="universal_search_input" placeholder="🔍 Search Technician, Caller, or Company">
    </div>
    """,
    unsafe_allow_html=True
)

# Streamlit binding for search input
st.session_state.universal_search = st.text_input(
    "", value=st.session_state.universal_search, placeholder="Search Technician, Caller, or Company"
)

# -------------------------------
# Top Navigation Tabs
# -------------------------------
st.markdown("""
    <div class="top-nav">
        <button onclick="window.location.href='#Dashboard'">Dashboard</button>
        <button onclick="window.location.href='#Advanced Analytics'">Advanced Analytics</button>
        <button onclick="window.location.href='#Data Explorer'">Data Explorer</button>
        <button onclick="window.location.href='#Export Center'">Export Center</button>
        <button onclick="window.location.href='#Settings'">Settings</button>
    </div>
""", unsafe_allow_html=True)

# ==============================
# PAGE LOGIC
# ==============================
# Your existing functions for:
# - upload_file()
# - clean_data()
# - anonymize()
# - calculate_monthly_summary()
# - top_performers()
# - style_sla()
# - apply_universal_search()
# - filter_last_3_months()
# - prepare_data()
# And then handle pages based on selection
# ==============================

page_options = ["Dashboard", "Advanced Analytics", "Data Explorer", "Export Center", "Settings"]
page = st.selectbox("Go to Page", page_options, index=0, key="top_nav_page")  # linked with top nav

# -------------------------------
# Apply universal search filter in all pages
# -------------------------------
def apply_search(df):
    if st.session_state.universal_search:
        df = df[
            df['Technician Name'].str.contains(st.session_state.universal_search, case=False, na=False) |
            df['Caller Name'].str.contains(st.session_state.universal_search, case=False, na=False) |
            df['Company Name'].str.contains(st.session_state.universal_search, case=False, na=False)
        ]
    return df
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
        fig = px.scatter(data, x='Duration (days)', y='SLA TTO Done',
                         color='Technician Name' if 'Technician Name' in data.columns else None,
                         size='Done Tasks' if 'Done Tasks' in data.columns else None,
                         hover_data=['Company Name'] if 'Company Name' in data.columns else None)
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
# DATA EXPLORER PAGE - IMPROVED
# =====================================================
elif page == "Data Explorer":
    st.markdown('<h1 class="page-title">DATA EXPLORER</h1>', unsafe_allow_html=True)
    st.markdown('<h4 class="page-subtitle">Search, filter, and analyze your ticket data</h4>', unsafe_allow_html=True)

    data = prepare_data()
    data, monthly_summary = calculate_monthly_summary(data)

    if data.empty:
        st.warning("No data available for display.")
        st.stop()

    # -------------------------------
    # KPI CARDS
    # -------------------------------
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
    c6.metric("SLA Violations", (total_tickets - closed_tickets))

    # -------------------------------
    # INLINE FILTERS
    # -------------------------------
    st.markdown("### Filters")
    filter_cols = st.columns([1,1,1,1])
    with filter_cols[0]:
        companies = st.multiselect("Company", data['Company Name'].dropna().unique())
    with filter_cols[1]:
        techs = st.multiselect("Technician", data['Technician Name'].dropna().unique())
    with filter_cols[2]:
        callers = st.multiselect("Caller", data['Caller Name'].dropna().unique())
    with filter_cols[3]:
        status_options = ['All', 'Closed', 'Pending']
        ticket_status = st.selectbox("Ticket Status", status_options, index=0)

    # Date Range Filter
    if 'Start date' in data.columns:
        start_date, end_date = st.date_input("Date Range", [data['Start date'].min(), data['Start date'].max()])
        data = data[(data['Start date'] >= pd.to_datetime(start_date)) & (data['Start date'] <= pd.to_datetime(end_date))]

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

    # -------------------------------
    # SEARCH IN ANY COLUMN
    # -------------------------------
    search_text = st.text_input("Search keyword in any column")
    if search_text:
        mask = data.apply(lambda row: row.astype(str).str.contains(search_text, case=False, na=False).any(), axis=1)
        data = data[mask]

    if data.empty:
        st.warning("No data matches your filters/search.")
        st.stop()

    # -------------------------------
    # INTERACTIVE CHARTS
    # -------------------------------
    st.markdown("### Ticket Status Distribution")
    ticket_counts = {
        'Closed': data['Done Tasks'].sum(),
        'Pending': data['Pending Tasks'].sum()
    }
    fig_pie = px.pie(
        names=list(ticket_counts.keys()),
        values=list(ticket_counts.values()),
        color=list(ticket_counts.keys()),
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

    st.markdown("### Monthly SLA Trend")
    if 'Month' in monthly_summary.columns and 'SLA %' in monthly_summary.columns:
        fig_line = px.line(
            monthly_summary.sort_values('Month'),
            x='Month',
            y='SLA %',
            markers=True,
            title="SLA % Trend Over Months"
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # -------------------------------
    # PAGINATED TABLE
    # -------------------------------
    st.markdown("### Ticket Data Table")
    rows_per_page = st.selectbox("Rows per page", [10, 25, 50, 100], index=1)
    total_rows = len(data)
    total_pages = (total_rows // rows_per_page) + (1 if total_rows % rows_per_page else 0)

    page_number = st.number_input("Page number", min_value=1, max_value=total_pages, value=1)
    start_idx = (page_number - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    table_to_show = data.iloc[start_idx:end_idx]

    # Conditional formatting for SLA
    if 'SLA %' in table_to_show.columns:
        def sla_color(val):
            if val >= 90: return 'color:green;font-weight:bold'
            elif val >= 75: return 'color:orange;font-weight:bold'
            else: return 'color:red;font-weight:bold'
        st.dataframe(table_to_show.style.applymap(sla_color, subset=['SLA %']), use_container_width=True)
    else:
        st.dataframe(table_to_show, use_container_width=True)

    # -------------------------------
    # DOWNLOAD OPTIONS
    # -------------------------------
    st.markdown("### Download Filtered Data")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='Filtered_Data', index=False)
    st.download_button("Download Excel", output.getvalue(), "filtered_data.xlsx")

    csv_output = data.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv_output, "filtered_data.csv", "text/csv")

# =====================================================
# EXPORT CENTER PAGE
# =====================================================
elif page == "Export Center":
    st.markdown('<h1 class="page-title">EXPORT CENTER</h1>', unsafe_allow_html=True)
    st.markdown('<h4 class="page-subtitle">Download processed reports and presentations safely</h4>', unsafe_allow_html=True)

    data = prepare_data()
    monthly_summary = st.session_state.get("monthly_summary", pd.DataFrame())
    tech_summary = st.session_state.get("tech_summary", pd.DataFrame())
    caller_summary = st.session_state.get("caller_summary", pd.DataFrame())

    # Warn if all tables are empty
    if data.empty and monthly_summary.empty and (tech_summary.empty if tech_summary is not None else True) \
       and (caller_summary.empty if caller_summary is not None else True):
        st.warning("⚠️ No data available to export. Please check your filters or upload a valid dataset.")
        st.stop()

    # -----------------------
    # Excel Export
    # -----------------------
    st.markdown("## Download Excel Reports")
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

    # -----------------------
    # PowerPoint Export
    # -----------------------
    st.markdown("## Download PowerPoint Presentation")
    tables_dict = {
        'Monthly KPI': monthly_summary,
        'Technician-wise KPI': tech_summary,
        'Caller-wise KPI': caller_summary
    }

    from src.ppt_export import create_ppt  # make sure the updated create_ppt is used
    try:
        prs = create_ppt(tables_dict)
        ppt_output = BytesIO()
        prs.save(ppt_output)
        ppt_output.seek(0)
        st.download_button("Download PowerPoint", ppt_output, "analytics_report.pptx")
    except Exception as e:
        st.error(f"❌ Failed to generate PowerPoint: {str(e)}")

# =====================================================
# SETTINGS PAGE – IMPROVED
# =====================================================
elif page == "Settings":
    st.markdown('<h1 class="page-title">SETTINGS</h1>', unsafe_allow_html=True)
    st.markdown('<h4 class="page-subtitle">Customize your dashboard preferences</h4>', unsafe_allow_html=True)

    # -------------------------------
    # DISPLAY OPTIONS
    # -------------------------------
    st.markdown("""
    <div style="background-color:white; padding:15px; border-radius:10px; box-shadow:1px 1px 5px #ccc;">
    <h3>Display Options</h3>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.show_kpis = st.checkbox(
        "Show KPI Cards", value=st.session_state.show_kpis,
        help="Toggle to show or hide KPI cards on the dashboard."
    )
    st.session_state.show_trends = st.checkbox(
        "Show Monthly Trends", value=st.session_state.show_trends,
        help="Toggle to display trend charts for monthly performance."
    )

    # -------------------------------
    # DATA PRIVACY & ANONYMIZATION
    # -------------------------------
    st.markdown("""
    <div style="background-color:white; padding:15px; border-radius:10px; box-shadow:1px 1px 5px #ccc; margin-top:10px;">
    <h3>Data Privacy</h3>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.anonymize_data = st.checkbox(
        "Anonymize Sensitive Data", value=st.session_state.anonymize_data,
        help="Enable to mask names and sensitive columns in the dashboard."
    )

    if st.session_state.anonymize_data:
        if st.session_state.data.empty:
            st.info("Upload data first to select columns for anonymization.")
        else:
            sensitive_columns = st.multiselect(
                "Select Columns to Anonymize",
                options=st.session_state.data.columns,
                default=getattr(st.session_state, "sensitive_columns", ['Technician Name','Caller Name','Company Name']),
                help="Choose which columns to anonymize when this option is enabled."
            )
            st.session_state.sensitive_columns = sensitive_columns

    # -------------------------------
    # REPORT FORMATTING
    # -------------------------------
    st.markdown("""
    <div style="background-color:white; padding:15px; border-radius:10px; box-shadow:1px 1px 5px #ccc; margin-top:10px;">
    <h3>Report Formatting</h3>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.decimal_places = st.slider(
        "Decimal Places in Reports", 0, 3, value=st.session_state.decimal_places,
        help="Choose the number of decimal places displayed in KPIs and reports."
    )

    # -------------------------------
    # THEME & APPEARANCE
    # -------------------------------
    st.markdown("""
    <div style="background-color:white; padding:15px; border-radius:10px; box-shadow:1px 1px 5px #ccc; margin-top:10px;">
    <h3>Theme & Appearance</h3>
    </div>
    """, unsafe_allow_html=True)

    theme_option = st.selectbox(
        "Theme", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1,
        help="Choose your dashboard theme. Light for bright view, Dark for low-light environments."
    )
    st.session_state.theme = theme_option

    st.markdown(f"**Current Theme:** {st.session_state.theme}")

    # -------------------------------
    # RESET & APPLY BUTTONS
    # -------------------------------
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Reset All Settings"):
            st.session_state.show_kpis = True
            st.session_state.show_trends = True
            st.session_state.anonymize_data = False
            st.session_state.sensitive_columns = []
            st.session_state.decimal_places = 1
            st.session_state.theme = "Light"
            st.success("⚡ Settings reset to default.")
            st.experimental_rerun()

    with col2:
        if st.button("Apply Changes"):
            st.success("✅ Settings applied successfully!")
            st.experimental_rerun()

# Then, inside each page you can do:
# data = prepare_data()
# data = apply_search(data)
# ... rest of your page logic remains the same


