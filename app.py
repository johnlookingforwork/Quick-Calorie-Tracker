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

    /* Typography */
    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.2rem !important; }
    h3 { font-size: 1rem !important; }

    /* Compact metrics */
    [data-testid="stMetric"] { padding: 0.4rem 0 !important; }
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }

    /* Reduce vertical gaps */
    [data-testid="stVerticalBlock"] > div { gap: 0.4rem !important; }

    /* Compact buttons globally */
    .stButton > button {
        padding: 0.3rem 0.5rem !important;
        font-size: 0.85rem !important;
    }

    /* ---- Nav bar buttons ---- */
    .st-key-nav_home .stButton > button,
    .st-key-nav_cal .stButton > button,
    .st-key-nav_set .stButton > button {
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        color: #AAAAAA !important;
        font-size: 0.7rem !important;
        padding: 4px 2px 6px !important;
        white-space: pre-line !important;
        line-height: 1.2 !important;
    }
    .st-key-nav_home .stButton > button:hover,
    .st-key-nav_cal .stButton > button:hover,
    .st-key-nav_set .stButton > button:hover {
        color: #FF6B6B !important;
        background: none !important;
    }

    /* Active nav highlight */
    .st-key-nav_home.active .stButton > button,
    .st-key-nav_cal.active .stButton > button,
    .st-key-nav_set.active .stButton > button {
        color: #FF6B6B !important;
        font-weight: 600 !important;
    }

    /* FAB style for the + button */
    .st-key-nav_log .stButton > button {
        background: #FF6B6B !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        min-width: 48px !important;
        max-width: 48px !important;
        font-size: 1.5rem !important;
        font-weight: 300 !important;
        padding: 0 !important;
        line-height: 1 !important;
        box-shadow: 0 2px 8px rgba(255,107,107,0.35) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: -8px auto 0 !important;
    }
    .st-key-nav_log .stButton > button:hover {
        background: #e55a5a !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(255,107,107,0.5) !important;
    }
    .st-key-nav_log .stButton > button p {
        font-size: 1.5rem !important;
        line-height: 1 !important;
    }

    /* Nav row: top border, less gap */
    .st-key-nav_row {
        border-top: 1px solid #E8E8E8;
        padding-top: 4px;
        margin-top: 1rem;
    }
    .st-key-nav_row [data-testid="stHorizontalBlock"] {
        align-items: center !important;
    }
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
# Inject active class on the current page's nav container
active_map = {"home": "nav_home", "calendar": "nav_cal", "settings": "nav_set"}
active_cls = active_map.get(st.session_state.page, "")
if active_cls:
    st.markdown(
        f"<style>.st-key-{active_cls} {{ }} .st-key-{active_cls} {{ }}"
        f"</style>"
        f"<script>document.querySelector('.st-key-{active_cls}')?.classList.add('active')</script>",
        unsafe_allow_html=True,
    )

with st.container(key="nav_row"):
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
