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

    /* ---------- Sidebar: tree-menu navigation ---------- */
    .sidebar-group-label {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.72rem;
        font-weight: 700;
        color: #8A97A0;
        text-transform: uppercase;
        letter-spacing: 0.7px;
        margin: 0.2rem 0 0.55rem 0.1rem;
    }
    .sidebar-group-label .chevron {
        font-size: 0.62rem;
        color: var(--brand-purple);
        transition: transform 0.15s ease;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] {
        position: relative;
        display: flex;
        flex-direction: column;
        gap: 0.3rem;
        padding-left: 0.9rem;
        margin-left: 0.25rem;
    }
    /* vertical tree connector line */
    section[data-testid="stSidebar"] div[role="radiogroup"]::before {
        content: "";
        position: absolute;
        left: 0.28rem;
        top: 0.4rem;
        bottom: 0.4rem;
        width: 2px;
        border-radius: 2px;
        background: linear-gradient(180deg, var(--brand-teal-light) 0%, var(--brand-purple) 100%);
        opacity: 0.35;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        position: relative;
        padding: 0.55rem 0.75rem;
        border-radius: 9px;
        margin-bottom: 0;
        transition: background 0.15s ease, border-color 0.15s ease, transform 0.12s ease;
        border: 1px solid transparent;
    }
    /* small horizontal branch connecting the tree line to each item */
    section[data-testid="stSidebar"] div[role="radiogroup"] label::before {
        content: "";
        position: absolute;
        left: -0.62rem;
        top: 50%;
        width: 0.45rem;
        height: 2px;
        background: var(--brand-border);
    }
    /* hide the native radio dot for a cleaner menu-item look */
    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
        display: none;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: #EEF1FC;
        border-color: var(--brand-border);
        transform: translateX(2px);
    }
    /* active/selected tool: purple-to-teal highlight */
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(120deg, rgba(108, 93, 211, 0.16) 0%, rgba(46, 150, 163, 0.18) 100%);
        border-color: var(--brand-purple-light);
        box-shadow: inset 3px 0 0 0 var(--brand-purple);
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
        color: var(--brand-navy);
        font-weight: 700;
    }

    /* ---------- Buttons: pill-shaped CTAs ---------- */
    div.stButton > button, div[data-testid="stDownloadButton"] > button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.45rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.45rem 1.3rem;
        min-height: 2.3rem;
        border: 1px solid var(--brand-border);
        box-shadow: 0 2px 6px rgba(20, 55, 74, 0.08);
        transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.2s ease;
    }
    div.stButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(20, 55, 74, 0.22);
    }
    div.stButton > button:active, div[data-testid="stDownloadButton"] > button:active {
        transform: translateY(0);
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
    div.stButton > button[kind="primary"]::after {
        content: "→";
        font-weight: 700;
        transition: transform 0.15s ease;
    }
    div.stButton > button[kind="primary"]:hover::after {
        transform: translateX(3px);
    }
    div.stButton > button[kind="secondary"] {
        background: #FFFFFF;
        color: var(--brand-navy);
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: var(--brand-gold);
        color: var(--brand-gold);
    }
    div.stButton > button[kind="secondary"]::after {
        content: "→";
        font-weight: 700;
        opacity: 0.7;
        transition: transform 0.15s ease;
    }
    div.stButton > button[kind="secondary"]:hover::after {
        transform: translateX(3px);
    }
    div[data-testid="stDownloadButton"] > button::before {
        content: "↓";
        font-weight: 700;
    }

    /* File uploader browse button */
    section[data-testid="stFileUploaderDropzone"] button {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        border-radius: 50px;
        font-size: 0.82rem;
        padding: 0.35rem 1.1rem;
        min-height: 2.1rem;
        background: linear-gradient(120deg, var(--brand-gold) 0%, #B5852A 100%);
        border-color: var(--brand-gold);
        color: #FFFFFF;
        font-weight: 600;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    section[data-testid="stFileUploaderDropzone"] button::after {
        content: "↑";
        font-weight: 700;
    }
    section[data-testid="stFileUploaderDropzone"] button:hover {
        background: linear-gradient(120deg, #D6A83A 0%, var(--brand-gold) 100%);
        border-color: #B5852A;
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(201, 150, 44, 0.3);
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
