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

# Mobile-optimized CSS (iPhone 15: 393×852 logical px)
st.markdown(
    """<style>
    [data-testid="stSidebar"] { display: none; }
    section[data-testid="stSidebarNav"] { display: none; }

    /* Tight mobile padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 430px !important;
    }

    /* Smaller headers */
    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.2rem !important; }
    h3 { font-size: 1rem !important; }

    /* Compact metrics */
    [data-testid="stMetric"] {
        padding: 0.4rem 0 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
    }

    /* Reduce vertical gaps */
    [data-testid="stVerticalBlock"] > div {
        gap: 0.4rem !important;
    }

    /* Compact buttons */
    .stButton > button {
        padding: 0.3rem 0.5rem !important;
        font-size: 0.85rem !important;
    }

    /* Footer nav fixed at bottom */
    .footer-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 2px solid #F0F0F0;
        padding: 6px 8px env(safe-area-inset-bottom, 8px);
        z-index: 9999;
        display: flex;
        justify-content: space-around;
    }
    .footer-nav button {
        flex: 1;
        border: none;
        background: none;
        font-size: 0.8rem;
        padding: 6px 4px;
        cursor: pointer;
        color: #666;
        border-radius: 8px;
    }
    .footer-nav button:hover { background: #F5F5F5; }
    .footer-nav button.active { color: #FF6B6B; font-weight: 600; }
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
col1, col2, col3, col4 = st.columns(4)

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

with col4:
    if st.button("⚙️ Settings", use_container_width=True, key="nav_settings"):
        st.session_state.page = "settings"
        st.rerun()
