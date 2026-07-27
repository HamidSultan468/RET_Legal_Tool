"""
RET Legal - Internal Tools
Main entry point. Switches between tools via the sidebar.
"""

import streamlit as st

st.set_page_config(
    page_title="RET Legal Tools",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    :root {
        --brand-navy: #14374A;
        --brand-teal: #1B6E7A;
        --brand-teal-light: #2E96A3;
        --brand-gold: #C9962C;
        --brand-rose: #B5495B;
        --brand-bg-soft: #F6F9FA;
        --brand-border: #E3E8EB;
        --brand-purple: #6C5DD3;
        --brand-purple-light: #8B7FE8;

        /* Dark admin-panel sidebar palette */
        --sidebar-bg-top: #1A2030;
        --sidebar-bg-bottom: #10141F;
        --sidebar-text: #C9CEDA;
        --sidebar-text-muted: #6E7690;
        --sidebar-text-bright: #FFFFFF;
        --sidebar-hover-bg: rgba(255, 255, 255, 0.07);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] { background: transparent; }
    div[data-testid="stToolbar"] { visibility: hidden; }

    .stApp {
        background: linear-gradient(180deg, #FBFDFE 0%, #F4F8F9 100%);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3.5rem;
        max-width: 1200px;
    }

    /* Breathing room between widgets across the whole app */
    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
        margin-bottom: 0.75rem;
    }
    .stTextInput label, .stSelectbox label, .stNumberInput label,
    .stFileUploader label, .stTextArea label {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        color: var(--brand-navy) !important;
    }

    /* ---------- Header ---------- */
    .app-header {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        width: 50%;
        min-width: 320px;
        padding: 1.2rem 1.6rem;
        margin-bottom: 1.8rem;
        border-radius: 14px;
        background: linear-gradient(120deg, var(--brand-navy) 0%, var(--brand-teal) 100%);
        box-shadow: 0 6px 18px rgba(20, 55, 74, 0.2);
    }
    .app-header h1 {
        margin: 0;
        font-size: 1.9rem;
        color: #FFFFFF;
        letter-spacing: 0.2px;
    }
    .app-header p {
        margin: 0;
        color: #D7E9EC;
        font-size: 0.95rem;
    }

    /* =========================================================
       SIDEBAR -- dark admin-panel theme
       ========================================================= */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div,
    div[data-testid="stSidebarContent"],
    div[data-testid="stSidebarUserContent"] {
        background: linear-gradient(180deg, var(--sidebar-bg-top) 0%, var(--sidebar-bg-bottom) 100%) !important;
    }
    section[data-testid="stSidebar"] {
        border-right: none !important;
        box-shadow: 6px 0 24px -10px rgba(16, 20, 31, 0.35) !important;
        padding-top: 0.5rem;
    }
    div[data-testid="stSidebarResizeHandle"] {
        background: transparent !important;
        border: none !important;
    }
    section[data-testid="stSidebar"] * {
        color: var(--sidebar-text);
    }
    div[data-testid="stSidebarUserContent"] {
        padding: 1.6rem 1.3rem 2rem 1.3rem !important;
    }

    .sidebar-brand {
        font-size: 1.4rem;
        font-weight: 800;
        color: var(--sidebar-text-bright) !important;
        margin-bottom: 0;
        letter-spacing: 0.2px;
    }
    .sidebar-tagline {
        font-size: 0.78rem;
        color: var(--sidebar-text-muted) !important;
        margin-top: -2px;
        margin-bottom: 1.6rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .sidebar-group-label {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--sidebar-text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 1.1px;
        margin: 0.4rem 0 0.9rem 0.2rem;
    }
    .sidebar-group-label .chevron {
        font-size: 0.62rem;
        color: var(--brand-purple-light) !important;
    }

    /* Nav list */
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        display: flex;
        align-items: center;
        padding: 0.85rem 1.1rem !important;
        border-radius: 12px !important;
        margin-bottom: 0;
        transition: background 0.18s ease, transform 0.12s ease;
        border: 1px solid transparent;
        cursor: pointer;
    }
    /* hide the native radio dot -- these read as nav list items, not a form control */
    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
        display: none;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: var(--sidebar-text) !important;
        margin: 0;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: var(--sidebar-hover-bg) !important;
        transform: translateX(3px);
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover p {
        color: var(--sidebar-text-bright) !important;
    }
    /* Active tool: solid purple-to-teal pill */
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(120deg, var(--brand-purple) 0%, var(--brand-teal-light) 100%) !important;
        box-shadow: 0 6px 16px rgba(108, 93, 211, 0.45);
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
        margin: 1.6rem 0 1.2rem 0 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: var(--sidebar-text-muted) !important;
        font-size: 0.78rem !important;
    }

    /* ---------- Sidebar status badge ---------- */
    .sidebar-badge {
        display: inline-block;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 0.4rem 0.9rem;
        border-radius: 999px;
        background: #E4F5EA;
        color: #1E6B3E !important;
        border: 1px solid #BEE6CC;
        margin-top: 0.4rem;
    }
    .sidebar-badge, .sidebar-badge * { color: #1E6B3E !important; }

    /* =========================================================
       BUTTONS -- big, bold, gradient pills
       ========================================================= */
    div.stButton > button,
    div[data-testid="stDownloadButton"] > button,
    section[data-testid="stFileUploaderDropzone"] button {
        display: inline-flex !important;
        align-items: center;
        justify-content: center;
        gap: 0.45rem;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.5rem 1.2rem !important;
        min-height: 2.3rem;
        border: none !important;
        box-shadow: 0 2px 6px rgba(20, 55, 74, 0.12);
        transition: transform 0.12s ease, box-shadow 0.12s ease, background 0.2s ease;
        letter-spacing: 0.1px;
    }
    div.stButton > button:hover,
    div[data-testid="stDownloadButton"] > button:hover,
    section[data-testid="stFileUploaderDropzone"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 14px rgba(20, 55, 74, 0.22);
    }
    div.stButton > button:active,
    div[data-testid="stDownloadButton"] > button:active,
    section[data-testid="stFileUploaderDropzone"] button:active {
        transform: translateY(0);
    }

    div.stButton > button[kind="primary"], div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(120deg, var(--brand-teal) 0%, var(--brand-navy) 100%) !important;
        color: #FFFFFF !important;
    }
    div.stButton > button[kind="primary"]:hover, div[data-testid="stDownloadButton"] > button:hover {
        background: linear-gradient(120deg, var(--brand-teal-light) 0%, var(--brand-teal) 100%) !important;
    }
    div.stButton > button[kind="primary"]::after {
        content: "→";
        font-size: 1.2em;
        font-weight: 700;
        transition: transform 0.15s ease;
    }
    div.stButton > button[kind="primary"]:hover::after {
        transform: translateX(4px);
    }

    div.stButton > button[kind="secondary"] {
        background: #FFFFFF !important;
        color: var(--brand-navy) !important;
        border: 2px solid var(--brand-border) !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: var(--brand-gold) !important;
        color: var(--brand-gold) !important;
    }
    div.stButton > button[kind="secondary"]::after {
        content: "→";
        font-size: 1.2em;
        font-weight: 700;
        opacity: 0.7;
        transition: transform 0.15s ease;
    }
    div.stButton > button[kind="secondary"]:hover::after {
        transform: translateX(4px);
    }

    div[data-testid="stDownloadButton"] > button::before {
        content: "↓";
        font-size: 1.2em;
        font-weight: 700;
    }

    section[data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(120deg, var(--brand-gold) 0%, #B5852A 100%) !important;
        color: #FFFFFF !important;
        font-size: 0.85rem !important;
        padding: 0.45rem 1.1rem !important;
    }
    section[data-testid="stFileUploaderDropzone"] button::after {
        content: "↑";
        font-size: 1.2em;
        font-weight: 700;
    }
    section[data-testid="stFileUploaderDropzone"] button:hover {
        background: linear-gradient(120deg, #D6A83A 0%, var(--brand-gold) 100%) !important;
        box-shadow: 0 10px 22px rgba(201, 150, 44, 0.35);
    }

    /* ---------- Cards ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        border-color: var(--brand-border) !important;
        box-shadow: 0 2px 10px rgba(20, 55, 74, 0.07);
        background: #FFFFFF;
        padding: 0.4rem;
    }

    /* ---------- Expanders (case results) ---------- */
    details[data-testid="stExpander"] {
        border-radius: 10px !important;
        border-left: 4px solid var(--brand-teal-light) !important;
        margin-bottom: 0.6rem;
    }
    details[data-testid="stExpander"] summary {
        font-weight: 600;
        color: var(--brand-navy);
        padding: 0.9rem 1.1rem;
    }

    /* ---------- Alerts: colourful left accent ---------- */
    div[data-testid="stAlert"] {
        border-radius: 10px;
        border-left: 4px solid transparent;
        padding: 1rem 1.2rem;
    }
    div[data-testid="stAlertContentSuccess"] { color: #1E6B3E; }
    div[data-testid="stAlertContentInfo"] { color: #205C8C; }
    div[data-testid="stAlertContentWarning"] { color: #8A5A12; }
    div[data-testid="stAlertContentError"] { color: #A32E3D; }

    /* ---------- Inputs ---------- */
    div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
        border-radius: 9px !important;
        padding-top: 0.55rem !important;
        padding-bottom: 0.55rem !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<p class="sidebar-brand">⚖️ RET Legal</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-tagline">Internal Tools Platform</p>', unsafe_allow_html=True)

    st.markdown(
        '<p class="sidebar-group-label">'
        '<span class="chevron">&#9662;</span> Tools</p>',
        unsafe_allow_html=True,
    )
    tool_choice = st.radio(
        "Select a tool",
        ["📄 Document Ingestion Tool", "📚 CanLII Research Tool"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("RET Legal — Internal Platform")

if "Document Ingestion" in tool_choice:
    from tools import document_ingestion
    document_ingestion.run()
else:
    from tools import canlii_research
    canlii_research.run()
