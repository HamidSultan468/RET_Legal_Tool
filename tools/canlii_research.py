import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()

DATABASES = {
    "Alberta - Court of King's Bench": "abkb",
    "Alberta - Court of Appeal": "abca",
    "Alberta - Court of Justice": "abcj",
    "BC - Supreme Court": "bcsc",
    "BC - Court of Appeal": "bcca",
    "Ontario - Superior Court": "onsc",
    "Ontario - Court of Appeal": "onca",
    "Supreme Court of Canada": "csc-scc",
}

def run():
    st.markdown(
        '<div class="app-header"><h1>📚 CanLII Research Tool</h1>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.write("Search Canadian court case law from CanLII.")

    api_key = os.getenv("CANLII_API_KEY", "")
    if not api_key:
        api_key = st.sidebar.text_input("CanLII API Key", type="password")
    if not api_key:
        st.warning("No API key found. Please provide one in the sidebar.")
        return

    st.sidebar.markdown('<span class="sidebar-badge">✓ API Key loaded</span>', unsafe_allow_html=True)

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            db_label = st.selectbox("Select Court", list(DATABASES.keys()))
        with col2:
            limit = st.number_input("Number of Results", min_value=1, max_value=20, value=10)

        search_clicked = st.button("🔍 Search", type="primary")

    if search_clicked:
        database_id = DATABASES[db_label]
        with st.spinner("Searching..."):
            results = get_cases(api_key, database_id, limit)

        if results is None:
            st.error("No response received from the API.")
        elif len(results) == 0:
            st.info("No results found.")
        else:
            st.success(f"{len(results)} cases found.")
            for case in results:
                case_id = case.get("caseId", {}).get("en", "")
                with st.expander(case.get("title", "Untitled")):
                    st.write(f"**Citation:** {case.get('citation', '')}")
                    if case_id and st.button("View Full Details", key=f"meta_{case_id}"):
                        with st.spinner("Loading details..."):
                            meta = get_case_metadata(api_key, database_id, case_id)
                        if meta:
                            st.write(f"**Date:** {meta.get('decisionDate', 'Unknown')}")
                            st.write(f"**Docket:** {meta.get('docketNumber', '')}")
                    if case_id:
                        url = f"https://www.canlii.org/en/{database_id}/doc/{case_id}.html"
                        st.markdown(f"[View on CanLII]({url})")

def get_cases(api_key, database_id, limit):
    try:
        url = f"https://api.canlii.org/v1/caseBrowse/en/{database_id}/"
        params = {"api_key": api_key, "offset": 0, "resultCount": limit}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json().get("cases", [])
        else:
            st.error(f"API Error: {r.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def get_case_metadata(api_key, database_id, case_id):
    try:
        url = f"https://api.canlii.org/v1/caseBrowse/en/{database_id}/{case_id}/"
        params = {"api_key": api_key}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"API Error: {r.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None
