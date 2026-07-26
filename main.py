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
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] { background: transparent; }
    div[data-testid="stToolbar"] { visibility: hidden; }

    .stApp {
        background: linear-gradient(180deg, #FBFDFE 0%, #F4F8F9 100%);
    }

    .block-container {
        padding-top: 1.75rem;
        padding-bottom: 3rem;
    }

    /* ---------- Header ---------- */
    .app-header {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.9rem 1.2rem;
        margin-bottom: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(120deg, var(--brand-navy) 0%, var(--brand-teal) 100%);
        box-shadow: 0 4px 14px rgba(20, 55, 74, 0.18);
    }
    .app-header h1 {
        margin: 0;
        font-size: 1.55rem;
        color: #FFFFFF;
        letter-spacing: 0.2px;
    }
    .app-header p {
        margin: 0;
        color: #D7E9EC;
        font-size: 0.88rem;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        border-right: 1px solid var(--brand-border);
        background: linear-gradient(180deg, #FFFFFF 0%, #F3F7F8 100%);
    }
    .sidebar-brand {
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--brand-navy);
        margin-bottom: 0;
        letter-spacing: 0.2px;
    }
    .sidebar-tagline {
        font-size: 0.76rem;
        color: #8A97A0;
        margin-top: -4px;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 0.45rem 0.7rem;
        border-radius: 8px;
        margin-bottom: 0.25rem;
        transition: background 0.15s ease;
        border: 1px solid transparent;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: #EAF3F4;
        border-color: var(--brand-border);
    }

    /* ---------- Buttons: compact + colourful ---------- */
    div.stButton > button, div[data-testid="stDownloadButton"] > button {
        border-radius: 7px;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.32rem 0.95rem;
        min-height: 2.1rem;
        border: 1px solid var(--brand-border);
        box-shadow: 0 1px 2px rgba(20, 55, 74, 0.06);
        transition: transform 0.08s ease, box-shadow 0.15s ease;
    }
    div.stButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(20, 55, 74, 0.16);
    }
    div.stButton > button[kind="primary"], div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(120deg, var(--brand-teal) 0%, var(--brand-navy) 100%);
        border-color: var(--brand-navy);
        color: #FFFFFF;
    }
    div.stButton > button[kind="primary"]:hover, div[data-testid="stDownloadButton"] > button:hover {
        background: linear-gradient(120deg, var(--brand-teal-light) 0%, var(--brand-teal) 100%);
        border-color: var(--brand-teal);
        color: #FFFFFF;
    }
    div.stButton > button[kind="secondary"] {
        background: #FFFFFF;
        color: var(--brand-navy);
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: var(--brand-gold);
        color: var(--brand-gold);
    }

    /* File uploader browse button */
    section[data-testid="stFileUploaderDropzone"] button {
        border-radius: 7px;
        font-size: 0.82rem;
        padding: 0.3rem 0.85rem;
        min-height: 2rem;
        background: var(--brand-gold);
        border-color: var(--brand-gold);
        color: #FFFFFF;
        font-weight: 600;
    }
    section[data-testid="stFileUploaderDropzone"] button:hover {
        background: #B5852A;
        border-color: #B5852A;
    }

    /* ---------- Cards ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        border-color: var(--brand-border) !important;
        box-shadow: 0 2px 8px rgba(20, 55, 74, 0.06);
        background: #FFFFFF;
    }

    /* ---------- Expanders (case results) ---------- */
    details[data-testid="stExpander"] {
        border-radius: 8px !important;
        border-left: 3px solid var(--brand-teal-light) !important;
        margin-bottom: 0.4rem;
    }
    details[data-testid="stExpander"] summary {
        font-weight: 600;
        color: var(--brand-navy);
    }

    /* ---------- Alerts: colourful left accent ---------- */
    div[data-testid="stAlert"] {
        border-radius: 8px;
        border-left: 4px solid transparent;
    }
    div[data-testid="stAlertContentSuccess"] { color: #1E6B3E; }
    div[data-testid="stAlertContentInfo"] { color: #205C8C; }
    div[data-testid="stAlertContentWarning"] { color: #8A5A12; }
    div[data-testid="stAlertContentError"] { color: #A32E3D; }

    /* ---------- Inputs ---------- */
    div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
        border-radius: 7px !important;
    }

    /* ---------- Sidebar status badge ---------- */
    .sidebar-badge {
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        background: #E4F5EA;
        color: #1E6B3E;
        border: 1px solid #BEE6CC;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<p class="sidebar-brand">⚖️ RET Legal</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-tagline">Internal Tools Platform</p>', unsafe_allow_html=True)

    tool_choice = st.radio(
        "Select a tool",
        ["📄 Document Ingestion Tool", "📚 CanLII Research Tool"],
        label_visibility="visible",
    )

    st.divider()
    st.caption("RET Legal — Internal Platform")

if "Document Ingestion" in tool_choice:
    from tools import document_ingestion
    document_ingestion.run()
else:
    from tools import canlii_research
    canlii_research.run()
