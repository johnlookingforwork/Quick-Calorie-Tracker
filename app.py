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

    /* Mobile container */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 6rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 430px !important;
    }

    /* Smaller headers */
    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.2rem !important; }
    h3 { font-size: 1rem !important; }

    /* Compact metrics */
    [data-testid="stMetric"] { padding: 0.4rem 0 !important; }
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }

    /* Reduce vertical gaps */
    [data-testid="stVerticalBlock"] > div { gap: 0.4rem !important; }

    /* Compact buttons */
    .stButton > button {
        padding: 0.3rem 0.5rem !important;
        font-size: 0.85rem !important;
    }

    /* ---- Bottom nav bar ---- */
    .st-key-nav_bar {
        position: fixed !important;
        bottom: 0; left: 0; right: 0;
        background: #fff;
        border-top: 1px solid #E8E8E8;
        padding: 0 0 env(safe-area-inset-bottom, 0px) 0;
        z-index: 9999;
        display: flex !important;
        justify-content: center;
    }
    /* The columns wrapper inside the nav bar */
    .st-key-nav_bar [data-testid="stHorizontalBlock"] {
        max-width: 430px;
        margin: 0 auto;
        align-items: center !important;
        gap: 0 !important;
    }

    /* Nav button styling — icon stacked on label */
    .st-key-nav_bar .stButton > button {
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        color: #AAAAAA !important;
        font-size: 0.65rem !important;
        padding: 6px 4px 8px !important;
        line-height: 1.1 !important;
        width: 100% !important;
        white-space: pre-line !important;
        transition: color 0.15s;
    }
    .st-key-nav_bar .stButton > button:hover,
    .st-key-nav_bar .stButton > button:focus {
        color: #FF6B6B !important;
        background: none !important;
    }

    /* Active page highlight */
    .st-key-nav_bar .st-key-nav_home.nav-active .stButton > button,
    .st-key-nav_bar .st-key-nav_cal.nav-active .stButton > button,
    .st-key-nav_bar .st-key-nav_set.nav-active .stButton > button {
        color: #FF6B6B !important;
        font-weight: 600 !important;
    }

    /* FAB — the center + button */
    .st-key-nav_bar .st-key-nav_log .stButton > button {
        background: #FF6B6B !important;
        color: #fff !important;
        border-radius: 50% !important;
        width: 52px !important;
        height: 52px !important;
        font-size: 1.6rem !important;
        font-weight: 300 !important;
        padding: 0 !important;
        line-height: 52px !important;
        box-shadow: 0 2px 10px rgba(255,107,107,0.4) !important;
        margin: 0 auto !important;
        position: relative;
        top: -8px;
        display: flex !important;
        align-items: center;
        justify-content: center;
    }
    .st-key-nav_bar .st-key-nav_log .stButton > button:hover {
        transform: scale(1.08);
        box-shadow: 0 4px 16px rgba(255,107,107,0.5) !important;
        background: #FF6B6B !important;
    }
    .st-key-nav_bar .st-key-nav_log .stButton > button:active {
        transform: scale(0.95);
    }

    /* Hide the divider right before nav */
    .st-key-nav_bar hr { display: none !important; }
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

# --- Bottom Nav Bar ---
# Apply active class via JS after render
active = st.session_state.page
active_key_map = {"home": "nav_home", "calendar": "nav_cal", "settings": "nav_set"}
active_key = active_key_map.get(active, "")
if active_key:
    st.markdown(
        f"""<script>
        const el = document.querySelector('.st-key-{active_key}');
        if (el) el.classList.add('nav-active');
        </script>""",
        unsafe_allow_html=True,
    )

with st.container(key="nav_bar"):
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])

    with c1:
        with st.container(key="nav_home"):
            if st.button("🏠\nHome", use_container_width=True, key="btn_home"):
                st.session_state.page = "home"
                st.rerun()

    with c2:
        with st.container(key="nav_cal"):
            if st.button("📅\nCalendar", use_container_width=True, key="btn_cal"):
                st.session_state.page = "calendar"
                st.rerun()

    with c3:
        with st.container(key="nav_log"):
            if st.button("＋", use_container_width=True, key="btn_log", type="primary"):
                ui_log_dialog.show()

    with c4:
        with st.container(key="nav_set"):
            if st.button("⚙️\nSettings", use_container_width=True, key="btn_set"):
                st.session_state.page = "settings"
                st.rerun()
