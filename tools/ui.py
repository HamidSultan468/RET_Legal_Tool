"""
Shared UI layer for the RET Legal Tools platform.

Everything visual lives here so the two tools (document_ingestion,
canlii_research) stay pure logic and can't drift into inconsistent styling.
"""

import streamlit as st

# Design tokens. Deep navy on white -- the conventional palette for legal
# software, chosen over the previous neon-on-black because these screens get
# read for long stretches and printed/screenshotted into client-facing notes.
INK = "#0F172A"
MUTED = "#5A6B7F"
BRAND = "#1B4B66"
BRAND_DARK = "#123449"
BRAND_LIGHT = "#E8EFF4"
SURFACE = "#F6F8FA"
BORDER = "#E3E8EE"
SUCCESS = "#0E7C66"
WARNING = "#A15C07"
DANGER = "#B4232A"


CSS = f"""
<style>
    /* ---------- Base ---------- */
    .stApp {{
        background: #FFFFFF;
        color: {INK};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter,
                     Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    [data-testid="stHeader"] {{
        background: transparent;
    }}
    .block-container, [data-testid="stMainBlockContainer"] {{
        padding-top: 2.2rem;
        padding-bottom: 4rem;
        max-width: 1180px;
    }}

    /* ---------- Typography ---------- */
    h1, h2, h3, h4 {{
        color: {INK} !important;
        font-weight: 650 !important;
        letter-spacing: -0.015em;
        -webkit-text-fill-color: {INK};
    }}
    h1 {{ font-size: 1.85rem !important; }}
    h2 {{ font-size: 1.35rem !important; }}
    h3 {{ font-size: 1.08rem !important; }}
    p, li, label, .stMarkdown {{ color: {INK}; }}

    /* ---------- Page header ---------- */
    .page-head {{
        border-bottom: 1px solid {BORDER};
        padding-bottom: 1.1rem;
        margin-bottom: 1.6rem;
    }}
    .page-head .eyebrow {{
        color: {BRAND};
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }}
    .page-head h1 {{ margin: 0 0 0.3rem 0 !important; }}
    .page-head .sub {{
        color: {MUTED};
        font-size: 0.95rem;
        margin: 0;
        max-width: 70ch;
        line-height: 1.55;
    }}

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {{
        background: {BRAND_DARK};
        border-right: 1px solid {BRAND_DARK};
    }}
    [data-testid="stSidebar"] * {{ color: #DCE6EE !important; }}
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF;
    }}
    .brand {{
        display: flex;
        align-items: center;
        gap: 0.65rem;
        padding: 0.2rem 0 1.1rem 0;
        margin-bottom: 0.9rem;
        border-bottom: 1px solid rgba(255,255,255,0.13);
    }}
    .brand-mark {{
        width: 38px; height: 38px;
        flex: 0 0 38px;
        border-radius: 9px;
        background: #FFFFFF;
        color: {BRAND_DARK} !important;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.15rem; font-weight: 800;
    }}
    .brand-text .name {{
        font-size: 0.98rem; font-weight: 700; color: #FFFFFF !important;
        line-height: 1.2;
    }}
    .brand-text .role {{
        font-size: 0.72rem; color: rgba(220,230,238,0.75) !important;
        letter-spacing: 0.03em;
    }}
    .side-label {{
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.09em;
        text-transform: uppercase;
        color: rgba(220,230,238,0.6) !important;
        margin: 0.4rem 0 0.3rem 0;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label {{
        padding: 0.28rem 0;
        font-size: 0.93rem;
    }}
    .side-note {{
        font-size: 0.78rem;
        line-height: 1.5;
        color: rgba(220,230,238,0.72) !important;
        background: rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 0.7rem 0.8rem;
        margin-top: 0.5rem;
    }}
    .side-foot {{
        margin-top: 1.4rem; padding-top: 0.9rem;
        border-top: 1px solid rgba(255,255,255,0.13);
        font-size: 0.72rem;
        color: rgba(220,230,238,0.55) !important;
    }}

    /* ---------- Cards ---------- */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF;
        border-radius: 12px;
    }}
    .card-title {{
        font-size: 0.78rem; font-weight: 700; letter-spacing: 0.07em;
        text-transform: uppercase; color: {MUTED};
        margin-bottom: 0.15rem;
    }}

    /* ---------- Buttons ---------- */
    .stButton > button, .stDownloadButton > button {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 0.55rem 1.25rem !important;
        border: 1px solid {BORDER} !important;
        background: #FFFFFF !important;
        color: {INK} !important;
        box-shadow: none !important;
        transition: background 0.15s ease, border-color 0.15s ease;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        background: {SURFACE} !important;
        border-color: #C9D3DD !important;
        color: {INK} !important;
    }}
    .stButton > button[kind="primary"],
    .stDownloadButton > button[kind="primary"] {{
        background: {BRAND} !important;
        border-color: {BRAND} !important;
        color: #FFFFFF !important;
    }}
    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button[kind="primary"]:hover {{
        background: {BRAND_DARK} !important;
        border-color: {BRAND_DARK} !important;
        color: #FFFFFF !important;
    }}

    /* ---------- Inputs ---------- */
    [data-testid="stFileUploader"] section {{
        background: {SURFACE} !important;
        border: 1.5px dashed #C2D0DC !important;
        border-radius: 10px !important;
        padding: 1.1rem !important;
    }}
    [data-testid="stFileUploader"] section:hover {{
        border-color: {BRAND} !important;
        background: {BRAND_LIGHT} !important;
    }}

    /* The previous build styled the page dark but left this element alone,
       so extracted text rendered near-white on near-white and looked blank.
       Both colours are pinned explicitly here so that can't recur. */
    .stTextArea textarea, [data-testid="stTextArea"] textarea {{
        background: {SURFACE} !important;
        color: {INK} !important;
        -webkit-text-fill-color: {INK} !important;
        opacity: 1 !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
        font-family: "SF Mono", "Cascadia Mono", Consolas, monospace !important;
        font-size: 0.83rem !important;
        line-height: 1.6 !important;
    }}
    .stTextInput input, .stNumberInput input, [data-baseweb="select"] > div {{
        border-radius: 8px !important;
        border-color: {BORDER} !important;
        color: {INK} !important;
    }}

    /* ---------- Status banners ---------- */
    .banner {{
        display: flex; align-items: flex-start; gap: 0.6rem;
        padding: 0.8rem 1rem;
        border-radius: 9px;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 0.75rem;
        border: 1px solid;
    }}
    .banner b {{ font-weight: 650; }}
    .banner-ok   {{ background:#ECFAF5; border-color:#B9E6D8; color:{SUCCESS}; }}
    .banner-info {{ background:{BRAND_LIGHT}; border-color:#C6D9E6; color:{BRAND}; }}
    .banner-warn {{ background:#FDF6EC; border-color:#F0DCBC; color:{WARNING}; }}
    .banner-err  {{ background:#FDEFEF; border-color:#F2CDCD; color:{DANGER}; }}

    /* ---------- Stat tiles ---------- */
    .stat {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 0.85rem 1rem;
        background: #FFFFFF;
        height: 100%;
    }}
    .stat .k {{
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.07em;
        text-transform: uppercase; color: {MUTED}; margin-bottom: 0.3rem;
    }}
    .stat .v {{
        font-size: 1.5rem; font-weight: 700; color: {INK}; line-height: 1.1;
    }}
    .stat .v.warn {{ color: {WARNING}; }}
    .stat .v.ok {{ color: {SUCCESS}; }}

    /* ---------- Tables ---------- */
    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        overflow: hidden;
    }}

    /* ---------- Misc ---------- */
    .pill {{
        display: inline-block;
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 650;
        background: {BRAND_LIGHT};
        color: {BRAND};
        border: 1px solid #C6D9E6;
    }}
    .hint {{
        color: {MUTED};
        font-size: 0.82rem;
        line-height: 1.55;
    }}
    [data-testid="stExpander"] {{
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
    }}
    footer, #MainMenu {{ visibility: hidden; }}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def page_head(eyebrow: str, title: str, subtitle: str):
    st.markdown(
        f'<div class="page-head">'
        f'<div class="eyebrow">{eyebrow}</div>'
        f"<h1>{title}</h1>"
        f'<p class="sub">{subtitle}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )


def banner(kind: str, text: str):
    """kind: ok | info | warn | err"""
    icons = {"ok": "✓", "info": "i", "warn": "!", "err": "×"}
    st.markdown(
        f'<div class="banner banner-{kind}">'
        f"<span><b>{icons.get(kind, '')}</b></span><span>{text}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


def stat(label: str, value, tone: str = ""):
    st.markdown(
        f'<div class="stat"><div class="k">{label}</div>'
        f'<div class="v {tone}">{value}</div></div>',
        unsafe_allow_html=True,
    )


def hint(text: str):
    st.markdown(f'<p class="hint">{text}</p>', unsafe_allow_html=True)
