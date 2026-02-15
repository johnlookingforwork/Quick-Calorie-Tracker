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
    </style>""",
    unsafe_allow_html=True,
)

# Initialize DB
db.init_db()

if "page" not in st.session_state:
    st.session_state.page = "home"

# --- Page Router ---
page = st.session_state.page

if page == "home":
    ui_home.render()
elif page == "calendar":
    ui_calendar.render()
elif page == "settings":
    ui_settings.render()

# --- Bottom Nav ---
st.divider()
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("🏠 Home", use_container_width=True, key="nav_home"):
        st.session_state.page = "home"
        st.rerun()
with c2:
    if st.button("📅 History", use_container_width=True, key="nav_cal"):
        st.session_state.page = "calendar"
        st.rerun()
with c3:
    if st.button("➕ Log", use_container_width=True, key="nav_log", type="primary"):
        ui_log_dialog.show()
with c4:
    if st.button("⚙️ Settings", use_container_width=True, key="nav_set"):
        st.session_state.page = "settings"
        st.rerun()
