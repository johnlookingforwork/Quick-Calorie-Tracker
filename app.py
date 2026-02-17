from datetime import datetime

import streamlit as st
import db
import ui_home
import ui_calendar
import ui_settings
import ui_log_dialog

st.set_page_config(
    page_title="Quick Calorie Tracker",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """<style>
    /* Hide sidebar */
    [data-testid="stSidebar"],
    section[data-testid="stSidebarNav"] { display: none; }

    /* Mobile container */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 430px !important;
    }

    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.2rem !important; }
    h3 { font-size: 1rem !important; }

    [data-testid="stMetric"] { padding: 0.4rem 0 !important; }
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }

    [data-testid="stVerticalBlock"] > div { gap: 0.4rem !important; }

    .stButton > button {
        padding: 0.3rem 0.5rem !important;
        font-size: 0.85rem !important;
    }

    /* Big Log button */
    .st-key-log_btn .stButton > button {
        font-size: 1.1rem !important;
        padding: 0.7rem 1rem !important;
        border-radius: 12px !important;
    }

    /* Pill-style segmented nav */
    .st-key-nav_pills [data-baseweb="segmented-control"] {
        background: #F5F5F5;
        border-radius: 10px;
    }
    </style>""",
    unsafe_allow_html=True,
)

# Initialize DB
db.init_db()

if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now().strftime("%Y-%m-%d")

# --- Log Button (always visible, top priority) ---
with st.container(key="log_btn"):
    if st.button("➕ Log Food or Workout", use_container_width=True, type="primary", key="btn_log"):
        ui_log_dialog.show()

# --- Page Nav (pill toggle) ---
page_options = {"🏠 Home": "home", "📅 History": "calendar", "⚙️ Settings": "settings"}
current_label = next(k for k, v in page_options.items() if v == st.session_state.page)

with st.container(key="nav_pills"):
    selected = st.segmented_control(
        "nav",
        options=list(page_options.keys()),
        default=current_label,
        label_visibility="collapsed",
        key="nav_select",
    )

if selected and page_options.get(selected) != st.session_state.page:
    st.session_state.page = page_options[selected]
    st.rerun()

st.divider()

# --- Page Router ---
page = st.session_state.page

if page == "home":
    ui_home.render()
elif page == "calendar":
    ui_calendar.render()
elif page == "settings":
    ui_settings.render()
