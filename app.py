import os
import sqlite3

import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from database import DATABASE_NAME, create_tables
from data_generator import generate_data
from text_cleaning import clean_text, process_complaints


st.set_page_config(
    page_title="Citizen Grievance Analytics",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------------------------------------------------------------
# Icon helper (Google Material Symbols)
# ----------------------------------------------------------------------
def icon(name: str, size: int = 20, align: str = "middle") -> str:
    """Return an inline Google Material Symbols icon span."""
    return (
        f'<span class="material-symbols-outlined" '
        f'style="font-size:{size}px; vertical-align:{align}; line-height:1;">'
        f'{name}</span>'
    )


def icon_title(name: str, text: str, size: int = 26):
    """Render a page title with a leading Material icon."""
    st.markdown(
        f'<div class="page-title">{icon(name, size)}<span>{text}</span></div>',
        unsafe_allow_html=True,
    )


NAV_ITEMS = [
    ("City Overview", "dashboard"),
    ("Complaint Intake", "edit_note"),
    ("Complaint Preview", "search"),
    ("Ward Scorecard", "location_on"),
    ("Model Performance", "smart_toy"),
    ("Setup", "settings"),
]


# ----------------------------------------------------------------------
# Global CSS / layout scaffolding
# ----------------------------------------------------------------------
def inject_base_styles():
    topbar_icon = icon("location_city", 24)
    st.markdown(
        """
        <link rel="stylesheet"
              href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
        <link rel="stylesheet"
              href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" />

        <style>
            :root {
                --app-primary: #818CF8;
                --app-primary-dark: #6366F1;
                --app-bg: #0F1117;
                --app-surface: #171A23;
                --app-surface-hover: #1E2230;
                --app-border: #2A2E3A;
                --app-text: #E8E9ED;
                --app-muted: #9094A3;
                --header-height: 68px;
            }

            html, body, [class*="css"] {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }

            .material-symbols-outlined {
                font-variation-settings:
                    'FILL' 0,
                    'wght' 500,
                    'GRAD' 0,
                    'opsz' 24;
            }

            /* Hide Streamlit's default chrome, but keep the header bar itself
               so its toolbar buttons (menu / deploy / status) live inside
               our colored header instead of floating as a separate black strip */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}

            header[data-testid="stHeader"] {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: var(--header-height);
                background: transparent !important;
                box-shadow: none;
                z-index: 999997;
            }

            div[data-testid="stDecoration"] {
                background: transparent;
            }

            /* Toolbar (hamburger menu / deploy / status widget) sits
               transparently on top of our gradient .app-topbar below,
               so the two read as one merged header bar */
            div[data-testid="stToolbar"] {
                position: fixed;
                top: 0;
                right: 14px;
                height: var(--header-height);
                display: flex;
                align-items: center;
                z-index: 1000000;
            }

            div[data-testid="stToolbarActions"] {
                display: flex;
                align-items: center;
            }

            div[data-testid="stToolbar"] button,
            div[data-testid="stToolbarActions"] button,
            div[data-testid="stToolbar"] svg,
            div[data-testid="stStatusWidget"],
            div[data-testid="stStatusWidget"] * {
                color: #FFFFFF !important;
                fill: #FFFFFF !important;
                background: transparent !important;
            }

            div[data-testid="stToolbar"] button:hover {
                background: rgba(255, 255, 255, 0.15) !important;
                border-radius: 6px;
            }

            div[data-testid="stMainMenu"] {
                color: #FFFFFF !important;
            }

            .stApp {
                background: var(--app-bg);
                color: var(--app-text);
            }

            /* ---------- Streamlit widget dark theming ---------- */
            div[data-testid="stAppViewContainer"],
            div[data-testid="stMain"] {
                background: var(--app-bg);
                color: var(--app-text);
            }

            section[data-testid="stSidebar"] * {
                color: var(--app-text);
            }

            p, span, label, li, div[data-testid="stMarkdownContainer"] {
                color: var(--app-text);
            }

            h1, h2, h3, h4, h5, h6 {
                color: var(--app-text) !important;
            }

            /* Buttons */
            .stButton > button,
            div[data-testid="stFormSubmitButton"] > button {
                background: var(--app-surface);
                color: var(--app-text);
                border: 1px solid var(--app-border);
                border-radius: 8px;
            }

            .stButton > button:hover,
            div[data-testid="stFormSubmitButton"] > button:hover {
                background: var(--app-surface-hover);
                border-color: var(--app-primary);
                color: var(--app-primary);
            }

            .stButton > button:focus:not(:active),
            div[data-testid="stFormSubmitButton"] > button:focus:not(:active) {
                border-color: var(--app-primary);
                color: var(--app-text);
            }

            /* Inputs, selects, text areas */
            div[data-baseweb="input"],
            div[data-baseweb="base-input"],
            div[data-baseweb="select"] > div,
            div[data-baseweb="textarea"],
            textarea,
            input {
                background-color: var(--app-surface) !important;
                color: var(--app-text) !important;
                border-color: var(--app-border) !important;
            }

            div[data-baseweb="popover"] li,
            ul[role="listbox"] {
                background-color: var(--app-surface) !important;
                color: var(--app-text) !important;
            }

            /* Number input steppers */
            button[data-testid="stNumberInputStepUp"],
            button[data-testid="stNumberInputStepDown"] {
                background-color: var(--app-surface);
                border-color: var(--app-border);
            }

            /* Dataframes / tables */
            div[data-testid="stDataFrame"] {
                background: var(--app-surface);
                border: 1px solid var(--app-border);
                border-radius: 10px;
            }

            div[data-testid="stForm"] {
                background: var(--app-surface);
                border: 1px solid var(--app-border);
                border-radius: 12px;
                padding: 1.25rem;
            }

            /* Alerts */
            div[data-testid="stAlert"] {
                background: var(--app-surface);
                border: 1px solid var(--app-border);
            }

            /* Plotly charts sit in cards matching the metric tiles */
            div[data-testid="stPlotlyChart"] {
                background: var(--app-surface);
                border: 1px solid var(--app-border);
                border-radius: 12px;
                padding: 8px;
            }

            /* ---------- Single visible header bar (brand gradient) ----------
               The native Streamlit header is made fully transparent above,
               and its toolbar (menu/deploy) is fixed on top of this bar,
               so this is the only bar the user actually sees. */
            .app-topbar {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: var(--header-height);
                background: linear-gradient(90deg, var(--app-primary) 0%, var(--app-primary-dark) 100%);
                box-shadow: 0 2px 10px rgba(79, 70, 229, 0.25);
                display: flex;
                align-items: center;
                padding: 0 28px;
                z-index: 999990;
                pointer-events: none;
            }

            .app-topbar .brand-icon {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 10px;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 14px;
                flex-shrink: 0;
            }

            .app-topbar .brand-icon .material-symbols-outlined {
                color: #FFFFFF;
                font-size: 24px;
            }

            .app-topbar .brand-text {
                display: flex;
                flex-direction: column;
                line-height: 1.15;
            }

            .app-topbar .brand-text .brand-title {
                color: #FFFFFF;
                font-size: 19px;
                font-weight: 700;
                letter-spacing: 0.2px;
            }

            .app-topbar .brand-text .brand-subtitle {
                color: rgba(255, 255, 255, 0.78);
                font-size: 12px;
                font-weight: 400;
            }

            /* Push everything below the fixed header */
            div[data-testid="stAppViewContainer"] {
                padding-top: var(--header-height);
            }

            /* ---------- Sidebar (left, flush against header) ---------- */
            section[data-testid="stSidebar"] {
                top: 0;
                height: 100vh;
                background: var(--app-surface);
                border-right: 1px solid var(--app-border);
            }

            /* The native collapse-control row takes its own space; hide it
               (our own nav replaces it) so nothing is reserved above the list */
            div[data-testid="stSidebarHeader"],
            div[data-testid="stSidebarCollapseButton"] {
                display: none !important;
            }

            section[data-testid="stSidebar"] > div {
                padding-top: 0;
            }

            div[data-testid="stSidebarUserContent"] {
                padding-top: 2.4rem !important;
            }

            /* ---------- Sidebar nav list ---------- */
            .nav-list {
                display: flex;
                flex-direction: column;
                gap: 2px;
                margin-top: 0;
            }

            .nav-item,
            .nav-item:link,
            .nav-item:visited {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 11px 12px;
                border-radius: 8px;
                color: var(--app-text) !important;
                text-decoration: none !important;
                font-size: 14px;
                font-weight: 500;
                transition: background 0.15s ease, color 0.15s ease;
            }

            .nav-item:hover,
            .nav-item:focus {
                text-decoration: none !important;
            }

            /* Divider between rows, inset like the rounded buttons */
            .nav-divider {
                height: 1px;
                margin: 2px 12px;
                background: var(--app-border);
            }

            .nav-item .material-symbols-outlined {
                color: var(--app-muted);
                font-size: 20px;
                transition: color 0.15s ease;
            }

            .nav-item:hover {
                background: var(--app-surface-hover);
                color: var(--app-primary) !important;
            }

            .nav-item:hover .material-symbols-outlined {
                color: var(--app-primary);
            }

            .nav-item.active {
                background: var(--app-primary);
                color: #0F1117 !important;
                font-weight: 700;
                box-shadow: 0 2px 10px rgba(129, 140, 248, 0.35);
            }

            .nav-item.active .material-symbols-outlined {
                color: #0F1117;
            }

            /* ---------- Working area ---------- */
            .block-container {
                padding-top: 1.75rem;
                padding-bottom: 6.5rem;
                max-width: 1400px;
            }

            .page-title {
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 26px;
                font-weight: 700;
                color: var(--app-text);
                margin-bottom: 4px;
            }

            .page-title .material-symbols-outlined {
                color: var(--app-primary);
            }

            .page-subtitle {
                color: var(--app-muted);
                font-size: 14px;
                margin-bottom: 1.25rem;
            }

            div[data-testid="stMetric"] {
                background: var(--app-surface);
                border: 1px solid var(--app-border);
                border-radius: 12px;
                padding: 14px 18px;
            }

            h3, .stSubheader, div[data-testid="stMarkdownContainer"] h3 {
                color: var(--app-text);
            }
        </style>

        <div class="app-topbar">
            <div class="brand-icon">""" + topbar_icon + """</div>
            <div class="brand-text">
                <span class="brand-title">Citizen Grievance &amp; Service Analytics</span>
                <span class="brand-subtitle">Civic complaints · departments · wards · resolution tracking</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_data(query, params=()):
    connection = sqlite3.connect(DATABASE_NAME)
    try:
        return pd.read_sql_query(query, connection, params=params)
    finally:
        connection.close()


def get_complaint_count():
    data = load_data("SELECT COUNT(*) AS total FROM complaints")
    return int(data.iloc[0]["total"])


# ----------------------------------------------------------------------
# Chart helpers (Plotly, themed to match the dark UI)
# ----------------------------------------------------------------------
# Consistent colors per category so charts look intentional
STATUS_COLORS = {
    "Open": "#F87171",
    "In Progress": "#FBBF24",
    "Resolved": "#34D399",
}
PRIORITY_COLORS = {
    "High": "#F87171",
    "Medium": "#FBBF24",
    "Low": "#34D399",
}


def donut_chart(df, names_col, values_col, color_map=None, center_label="Total"):
    """Build a dark-themed donut chart with the total in the center."""
    total = int(df[values_col].sum())

    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        hole=0.62,
        color=names_col,
        color_discrete_map=color_map or {},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        textfont_color="#E8E9ED",
        marker=dict(line=dict(color="#0F1117", width=3)),
        hovertemplate="<b>%{label}</b><br>%{value:,} complaints (%{percent})<extra></extra>",
        sort=False,
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color="#E8E9ED"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#E8E9ED"),
        margin=dict(t=30, b=80, l=40, r=40),
        height=340,
        annotations=[
            dict(
                text=f"<b style='font-size:22px'>{total:,}</b><br>"
                     f"<span style='font-size:12px;color:#9094A3'>{center_label}</span>",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(color="#E8E9ED"),
            )
        ],
    )
    return fig


def _base_layout(fig, height=420):
    """Apply the shared dark theme to a Plotly figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#E8E9ED"),
        margin=dict(t=30, b=10, l=10, r=10),
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            title=None,
            font=dict(color="#E8E9ED"),
        ),
    )
    return fig


def stacked_status_chart(df, category_col, columns, labels, colors):
    """Stacked bar chart of complaint statuses per category."""
    long_df = df.melt(
        id_vars=category_col,
        value_vars=columns,
        var_name="Status",
        value_name="Complaints",
    )
    long_df["Status"] = long_df["Status"].map(dict(zip(columns, labels)))

    fig = px.bar(
        long_df,
        x=category_col,
        y="Complaints",
        color="Status",
        color_discrete_map=colors,
        category_orders={"Status": labels},
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:,}<extra></extra>",
    )
    fig.update_layout(
        barmode="stack",
        bargap=0.3,
        xaxis=dict(title=None, tickangle=-25, showgrid=False, color="#9094A3"),
        yaxis=dict(title=None, gridcolor="#2A2E3A", color="#9094A3"),
    )
    return _base_layout(fig, height=440)


def ward_volume_chart(df, top_n=15):
    """Horizontal bars of busiest wards, colored by resolution rate."""
    top = df.nlargest(top_n, "total_complaints").sort_values("total_complaints")

    fig = px.bar(
        top,
        x="total_complaints",
        y="ward_name",
        orientation="h",
        text="total_complaints",
        color="resolution_rate_percent",
        color_continuous_scale=["#F87171", "#FBBF24", "#34D399"],
        range_color=[0, 100],
        labels={"resolution_rate_percent": "Resolved %"},
    )
    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        textfont_color="#E8E9ED",
        marker_line_width=0,
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>%{x:,} complaints"
            "<br>Resolved: %{marker.color:.1f}%<extra></extra>"
        ),
    )
    fig.update_layout(
        bargap=0.3,
        xaxis=dict(title=None, gridcolor="#2A2E3A", color="#9094A3"),
        yaxis=dict(title=None, color="#E8E9ED"),
        coloraxis_colorbar=dict(
            title="Resolved %",
            tickfont=dict(color="#9094A3"),
            title_font=dict(color="#E8E9ED"),
            thickness=12,
        ),
    )
    return _base_layout(fig, height=520)


def ward_resolution_chart(df, bottom_n=15):
    """Horizontal bars of wards with the lowest resolution rate."""
    low = (
        df[df["total_complaints"] > 0]
        .nsmallest(bottom_n, "resolution_rate_percent")
        .sort_values("resolution_rate_percent", ascending=False)
    )

    fig = px.bar(
        low,
        x="resolution_rate_percent",
        y="ward_name",
        orientation="h",
        text="resolution_rate_percent",
        color="resolution_rate_percent",
        color_continuous_scale=["#F87171", "#FBBF24", "#34D399"],
        range_color=[0, 100],
    )
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        textfont_color="#E8E9ED",
        marker_line_width=0,
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Resolved: %{x:.1f}%<extra></extra>",
    )
    fig.update_layout(
        coloraxis_showscale=False,
        bargap=0.3,
        xaxis=dict(
            title=None, range=[0, 110], gridcolor="#2A2E3A", color="#9094A3"
        ),
        yaxis=dict(title=None, color="#E8E9ED"),
    )
    return _base_layout(fig, height=520)


def model_accuracy_chart(results, model_col="Model", metric_col="Accuracy"):
    """Bar chart of model accuracy with the best model highlighted."""
    df = results.sort_values(metric_col, ascending=False).reset_index(drop=True)
    is_fraction = df[metric_col].max() <= 1
    best = df[metric_col].max()

    df["Best"] = df[metric_col].apply(
        lambda v: "Best model" if v == best else "Other models"
    )

    fig = px.bar(
        df,
        x=model_col,
        y=metric_col,
        text=metric_col,
        color="Best",
        color_discrete_map={"Best model": "#34D399", "Other models": "#818CF8"},
        category_orders={"Best": ["Best model", "Other models"]},
    )
    fig.update_traces(
        texttemplate="%{text:.2%}" if is_fraction else "%{text:.2f}",
        textposition="outside",
        textfont_color="#E8E9ED",
        marker_line_width=0,
        cliponaxis=False,
        hovertemplate=(
            "<b>%{x}</b><br>"
            + metric_col
            + (": %{y:.2%}" if is_fraction else ": %{y:.2f}")
            + "<extra></extra>"
        ),
    )
    fig.update_layout(
        bargap=0.4,
        xaxis=dict(title=None, showgrid=False, color="#9094A3"),
        yaxis=dict(
            title=None,
            gridcolor="#2A2E3A",
            color="#9094A3",
            tickformat=".0%" if is_fraction else None,
            range=[0, (1.1 if is_fraction else best * 1.15)],
        ),
    )
    return _base_layout(fig, height=420)


def dashboard_page():
    icon_title("dashboard", "City Overview")
    st.markdown(
        '<div class="page-subtitle">Monitor civic complaints, department workloads, '
        "ward performance, and complaint resolution.</div>",
        unsafe_allow_html=True,
    )

    try:
        total = get_complaint_count()

        if total == 0:
            st.warning(
                "No complaints found. Open the Setup page to generate sample data."
            )
            return

        summary = load_data("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) AS open_count,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END)
                    AS in_progress,
                SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END)
                    AS resolved_count
            FROM complaints
        """)

        row = summary.iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Complaints", f"{int(row['total']):,}")
        c2.metric("Open", f"{int(row['open_count'] or 0):,}")
        c3.metric("In Progress", f"{int(row['in_progress'] or 0):,}")
        c4.metric("Resolved", f"{int(row['resolved_count'] or 0):,}")

        # ---- Row 1: two donuts side by side ----
        left, right = st.columns(2)

        with left:
            st.subheader("Complaints by Status")
            status_data = load_data("""
                SELECT status, COUNT(*) AS total
                FROM complaints
                GROUP BY status
            """)
            st.plotly_chart(
                donut_chart(status_data, "status", "total", STATUS_COLORS),
                use_container_width=True,
            )

        with right:
            st.subheader("Complaints by Priority")
            priority_data = load_data("""
                SELECT priority, COUNT(*) AS total
                FROM complaints
                GROUP BY priority
            """)
            st.plotly_chart(
                donut_chart(priority_data, "priority", "total", PRIORITY_COLORS),
                use_container_width=True,
            )

        # ---- Row 2: department status breakdown, full width ----
        department_data = load_data("""
            SELECT
                d.department_name,
                COUNT(c.complaint_id) AS total_complaints,
                SUM(CASE WHEN c.status = 'Open' THEN 1 ELSE 0 END)
                    AS open_complaints,
                SUM(CASE WHEN c.status = 'In Progress' THEN 1 ELSE 0 END)
                    AS in_progress_complaints,
                SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END)
                    AS resolved_complaints
            FROM departments d
            LEFT JOIN complaints c
                ON d.department_id = c.department_id
            GROUP BY d.department_id, d.department_name
            ORDER BY total_complaints DESC
        """).fillna(0)

        st.subheader("Status Breakdown by Department")
        st.plotly_chart(
            stacked_status_chart(
                department_data,
                "department_name",
                ["open_complaints", "in_progress_complaints", "resolved_complaints"],
                ["Open", "In Progress", "Resolved"],
                STATUS_COLORS,
            ),
            use_container_width=True,
        )

        # ---- Row 3: department table ----
        st.subheader("Complaints by Department")
        st.dataframe(department_data, use_container_width=True)

    except Exception as error:
        st.error(f"Could not load the dashboard: {error}")
        st.info("Try initializing the database and generating sample data.")


def complaint_preview_page():
    icon_title("search", "Complaint Preview")
    st.markdown(
        '<div class="page-subtitle">Monitor recently uploaded complaints '
        "and search them.</div>",
        unsafe_allow_html=True,
    )

    try:
        # ---- Filter row (one control per table column) ----
        category_options = load_data(
            "SELECT DISTINCT category FROM complaints "
            "WHERE category IS NOT NULL ORDER BY category"
        )["category"].tolist()

        f_id, f_citizen, f_ward, f_cat, f_text, f_status, f_priority, f_date = st.columns(
            [1, 1, 1, 1.6, 3, 1.3, 1.3, 1.7]
        )

        id_term = f_id.text_input(
            "Complaint ID", placeholder="🔍 Complaint ID",
            label_visibility="collapsed", key="flt_id",
        )
        citizen_term = f_citizen.text_input(
            "Citizen ID", placeholder="🔍 Citizen ID",
            label_visibility="collapsed", key="flt_citizen_id",
        )
        ward_term = f_ward.text_input(
            "Ward ID", placeholder="🔍 Ward ID",
            label_visibility="collapsed", key="flt_ward_id",
        )
        category = f_cat.selectbox(
            "Category", ["All Categories"] + category_options,
            label_visibility="collapsed", key="flt_category",
        )
        text_term = f_text.text_input(
            "Complaint text", placeholder="🔍 Search complaint text",
            label_visibility="collapsed", key="flt_text",
        )
        status = f_status.selectbox(
            "Status", ["All Status", "Open", "In Progress", "Resolved"],
            label_visibility="collapsed", key="flt_status",
        )
        priority = f_priority.selectbox(
            "Priority", ["All Priority", "High", "Medium", "Low"],
            label_visibility="collapsed", key="flt_priority",
        )
        date_term = f_date.text_input(
            "Date", placeholder="🔍 Date (e.g. 2025-03)",
            label_visibility="collapsed", key="flt_date",
        )

        # ---- Build the filtered query ----
        where, params = [], []

        if id_term.strip():
            where.append("CAST(complaint_id AS TEXT) LIKE ?")
            params.append(f"%{id_term.strip()}%")
        if citizen_term.strip():
            where.append("CAST(citizen_id AS TEXT) LIKE ?")
            params.append(f"%{citizen_term.strip()}%")
        if ward_term.strip():
            where.append("CAST(ward_id AS TEXT) LIKE ?")
            params.append(f"%{ward_term.strip()}%")
        if category != "All Categories":
            where.append("category = ?")
            params.append(category)
        if text_term.strip():
            where.append("complaint_text LIKE ?")
            params.append(f"%{text_term.strip()}%")
        if status != "All Status":
            where.append("status = ?")
            params.append(status)
        if priority != "All Priority":
            where.append("priority = ?")
            params.append(priority)
        if date_term.strip():
            where.append("created_at LIKE ?")
            params.append(f"%{date_term.strip()}%")

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""

        matching = int(
            load_data(
                f"SELECT COUNT(*) AS n FROM complaints {where_sql}",
                tuple(params),
            ).iloc[0]["n"]
        )

        recent = load_data(
            f"""
            SELECT complaint_id, citizen_id, ward_id,
                   category, complaint_text, status, priority, created_at
            FROM complaints
            {where_sql}
            ORDER BY created_at DESC
            LIMIT 20
            """,
            tuple(params),
        )

        st.caption(f"Showing {len(recent):,} of {matching:,} matching complaints")
        st.dataframe(recent, use_container_width=True)

    except Exception as error:
        st.error(f"Could not load complaints: {error}")
        st.info("Try initializing the database and generating sample data.")


def intake_page():
    icon_title("edit_note", "Register a Complaint")

    st.markdown(
        '<div class="page-subtitle">File a complaint mentioning your identity'
        ",problem and to which department.</div>",
        unsafe_allow_html=True,
    )

    departments = load_data("""
        SELECT department_id, department_name
        FROM departments
        ORDER BY department_name
    """)

    if departments.empty:
        st.warning("Set up the database before registering complaints.")
        return

    with st.form("complaint_form"):
        citizen_id = st.number_input(
            "Citizen ID",
            min_value=1,
            value=1,
            step=1,
        )

        ward_id = st.number_input(
            "Ward ID",
            min_value=1,
            max_value=40,
            value=1,
            step=1,
        )

        department_name = st.selectbox(
            "Department",
            departments["department_name"].tolist(),
        )

        complaint_text = st.text_area(
            "Describe the complaint",
            placeholder="Explain the civic issue...",
        )

        priority = st.selectbox(
            "Priority",
            ["Low", "Medium", "High"],
            index=1,
        )

        submitted = st.form_submit_button("Submit Complaint")

    if submitted:
        if not complaint_text.strip():
            st.error("Please enter a complaint description.")
            return

        department_id = int(
            departments.loc[
                departments["department_name"] == department_name,
                "department_id",
            ].iloc[0]
        )

        connection = sqlite3.connect(DATABASE_NAME)

        try:
            cursor = connection.cursor()

            citizen_exists = cursor.execute(
                "SELECT 1 FROM citizens WHERE citizen_id = ?",
                (int(citizen_id),),
            ).fetchone()

            if not citizen_exists:
                st.error(
                    "Citizen ID not found. Use an existing sample citizen ID."
                )
                return

            cursor.execute(
                """
                INSERT INTO complaints (
                    citizen_id, ward_id, department_id,
                    complaint_text, category, status,
                    created_at, priority
                )
                VALUES (?, ?, ?, ?, ?, 'Open', ?, ?)
                """,
                (
                    int(citizen_id),
                    int(ward_id),
                    department_id,
                    complaint_text.strip(),
                    department_name,
                    pd.Timestamp.now().isoformat(timespec="seconds"),
                    priority,
                ),
            )

            complaint_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO status_history (
                    complaint_id, old_status, new_status, changed_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    complaint_id,
                    None,
                    "Open",
                    pd.Timestamp.now().isoformat(timespec="seconds"),
                ),
            )

            connection.commit()
            st.success(
                f"Complaint registered successfully. ID: {complaint_id}"
            )

        except Exception as error:
            connection.rollback()
            st.error(f"Could not register complaint: {error}")

        finally:
            connection.close()


def ward_scorecard_page():
    icon_title("location_on", "Ward Scorecard")

    data = load_data("""
        SELECT
            w.ward_name,
            w.population,
            COUNT(c.complaint_id) AS total_complaints,
            SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END)
                AS resolved_complaints
        FROM wards w
        LEFT JOIN complaints c ON w.ward_id = c.ward_id
        GROUP BY w.ward_id, w.ward_name, w.population
        ORDER BY total_complaints DESC
    """)

    data["resolution_rate_percent"] = (
        data["resolved_complaints"].fillna(0)
        / data["total_complaints"].replace(0, 1)
        * 100
    ).round(2)

    st.markdown(
        '<div class="page-subtitle">Complaint volume and resolution '
        "performance across wards.</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Busiest Wards")
        st.plotly_chart(ward_volume_chart(data), use_container_width=True)

    with right:
        st.subheader("Lowest Resolution Rate")
        st.plotly_chart(ward_resolution_chart(data), use_container_width=True)

    st.subheader("All Wards")
    st.dataframe(data, use_container_width=True)


def model_performance_page():
    icon_title("smart_toy", "Model Performance")

    path = "model_artifacts/model_comparison.csv"

    if os.path.exists(path):
        results = pd.read_csv(path)

        best_row = results.loc[results["Accuracy"].idxmax()]
        best_acc = best_row["Accuracy"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Best Model", str(best_row["Model"]))
        c2.metric(
            "Best Accuracy",
            f"{best_acc:.2%}" if best_acc <= 1 else f"{best_acc:.2f}",
        )
        c3.metric("Models Compared", len(results))

        st.subheader("Accuracy by Model")
        st.plotly_chart(
            model_accuracy_chart(results), use_container_width=True
        )

        st.subheader("Full Comparison")
        st.dataframe(results, use_container_width=True)
    else:
        st.info(
            "Model results are not available yet. Run the training steps first."
        )


def setup_page():
    icon_title("settings", "Project Setup")
    st.markdown(
        '<div class="page-subtitle">Use these controls to initialize the '
        "database and prepare sample data.</div>",
        unsafe_allow_html=True,
    )

    if st.button("1. Create Database Tables"):
        try:
            create_tables()
            st.success("Database tables are ready.")
        except Exception as error:
            st.error(str(error))

    if st.button("2. Generate 60,000 Sample Complaints"):
        with st.spinner("Generating sample data. This may take a while..."):
            try:
                generate_data()
                st.success("Sample data generated.")
            except Exception as error:
                st.error(str(error))

    if st.button("3. Clean Complaint Text"):
        with st.spinner("Cleaning complaint text..."):
            try:
                process_complaints()
                st.success("Complaint text cleaned.")
            except Exception as error:
                st.error(str(error))


def sidebar_nav() -> str:
    """Render an icon-based nav list in the sidebar and return the active page."""
    labels = [label for label, _ in NAV_ITEMS]

    if "page" not in st.session_state:
        st.session_state.page = labels[0]

    # Support deep-linking / link clicks via ?page=
    query_page = st.query_params.get("page")
    if query_page in labels and query_page != st.session_state.page:
        st.session_state.page = query_page

    with st.sidebar:
        items_html = []
        for position, (label, icon_name) in enumerate(NAV_ITEMS):
            is_active = st.session_state.page == label
            if position > 0:
                items_html.append('<div class="nav-divider"></div>')
            items_html.append(
                f'<a href="?page={label.replace(" ", "+")}" '
                f'target="_self" class="nav-item {"active" if is_active else ""}">'
                f'{icon(icon_name, 20)}<span>{label}</span></a>'
            )

        st.markdown(
            f'<div class="nav-list">{"".join(items_html)}</div>',
            unsafe_allow_html=True,
        )

    return st.session_state.page


def main():
    inject_base_styles()
    page = sidebar_nav()

    if page == "City Overview":
        dashboard_page()
    elif page == "Complaint Intake":
        intake_page()
    elif page == "Complaint Preview":
        complaint_preview_page()
    elif page == "Ward Scorecard":
        ward_scorecard_page()
    elif page == "Model Performance":
        model_performance_page()
    elif page == "Setup":
        setup_page()


if __name__ == "__main__":
    main()