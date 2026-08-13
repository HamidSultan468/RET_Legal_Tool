"""
RET Legal Tools Platform -- app entry point.

Run with:  streamlit run main.py
"""

import streamlit as st

st.set_page_config(
    page_title="RET Legal Tools",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from tools import ui, document_ingestion, canlii_research  # noqa: E402

ui.inject_css()

PAGES = {
    "Document Ingestion": document_ingestion.run,
    "CanLII Research": canlii_research.run,
}

with st.sidebar:
    st.markdown(
        '<div class="brand">'
        '<div class="brand-mark">⚖</div>'
        '<div class="brand-text">'
        '<div class="name">RET Legal</div>'
        '<div class="role">Tools Platform</div>'
        "</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">Tools</div>', unsafe_allow_html=True)
    choice = st.radio(
        "Select a tool",
        list(PAGES.keys()),
        label_visibility="collapsed",
    )

    st.markdown('<div class="side-label">About this tool</div>', unsafe_allow_html=True)
    notes = {
        "Document Ingestion": (
            "Pulls text out of PDFs and scans. Digital pages are read directly; "
            "scanned pages fall back to OCR, and every OCR line carries a "
            "confidence score so weak reads get flagged for review."
        ),
        "CanLII Research": (
            "Browses Canadian court decisions through the CanLII API. "
            "Keyword matching runs against case titles and citations — "
            "CanLII's API does not expose decision full text."
        ),
    }
    st.markdown(f'<div class="side-note">{notes[choice]}</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="side-foot">RET Legal — internal use only.<br>'
        "Verify all extracted text against the source document.</div>",
        unsafe_allow_html=True,
    )

PAGES[choice]()
