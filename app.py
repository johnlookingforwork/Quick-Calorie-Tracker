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

# Hide sidebar
st.markdown(
    """<style>
    [data-testid="stSidebar"] { display: none; }
    section[data-testid="stSidebarNav"] { display: none; }
    .block-container { padding-bottom: 80px; }
    .fixed-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 1px solid #E0E0E0;
        padding: 8px 0;
        z-index: 999;
    }
    .fixed-footer button { width: 100%; }
    </style>""",
    unsafe_allow_html=True,
)

# Initialize DB
db.init_db()

# Session state defaults
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

# --- Footer Navigation ---
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Home", use_container_width=True, key="nav_home"):
        st.session_state.page = "home"
        st.rerun()

with col2:
    if st.button("➕ Log", use_container_width=True, key="nav_log", type="primary"):
        ui_log_dialog.show()

with col3:
    if st.button("📅 Calendar", use_container_width=True, key="nav_calendar"):
        st.session_state.page = "calendar"
        st.rerun()
