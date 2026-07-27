import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "https://api.canlii.org/v1"

# How many candidate cases to pull from CanLII per keyword search before
# filtering locally. The CanLII API has no full-text/keyword search
# endpoint at all (confirmed against the official API docs) -- it only
# supports browsing a single court's decisions by offset/date. So a
# "search" here means: fetch a batch of the court's most recent decisions,
# then filter them locally by keyword against title/citation.
MAX_SCAN = 500


def _get_databases(api_key):
    """Fetch the full list of CanLII case databases (all courts/tribunals),
    cached for the session so it's only fetched once."""
    if "canlii_databases" in st.session_state:
        return st.session_state["canlii_databases"]

    url = f"{BASE_URL}/caseBrowse/en/"
    r = requests.get(url, params={"api_key": api_key}, timeout=15)
    if r.status_code != 200:
        st.error(f"API Error loading court list: {r.status_code}")
        return {}

    databases = {db["name"]: db["databaseId"] for db in r.json().get("caseDatabases", [])}
    st.session_state["canlii_databases"] = databases
    return databases


def _matches_keyword(case, tokens):
    """True if every keyword token appears in the case's title or citation.
    This is a title/citation match, not a full-text search of the decision
    -- CanLII's public API doesn't expose decision text for searching."""
    haystack = f"{case.get('title', '')} {case.get('citation', '')}".lower()
    return all(token in haystack for token in tokens)


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

    with st.spinner("Loading list of courts/tribunals..."):
        databases = _get_databases(api_key)

    if not databases:
        st.error("Could not load the list of courts/tribunals.")
        return

    with st.container(border=True):
        db_label = st.selectbox("Select Court", sorted(databases.keys()))

        keyword = st.text_input(
            "Search keyword (matches case title / citation)",
            help=(
                "CanLII's API does not support full-text search of decisions, "
                "so this matches against the case title and citation only."
            ),
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            published_after = st.text_input("Published after (YYYY-MM-DD)", "")
        with col2:
            published_before = st.text_input("Published before (YYYY-MM-DD)", "")
        with col3:
            limit = st.number_input("Number of results to show", min_value=1, max_value=100, value=10)

        search_clicked = st.button("🔍 Search", type="primary", use_container_width=False)

    if search_clicked:
        database_id = databases[db_label]
        keyword_tokens = [t.lower() for t in keyword.split() if t.strip()]

        with st.spinner("Searching..."):
            # When scanning for a keyword, pull a larger candidate batch so
            # there's something worth filtering; otherwise just browse the
            # most recent decisions.
            scan_count = MAX_SCAN if keyword_tokens else limit
            candidates = get_cases(
                api_key, database_id, scan_count,
                published_after=published_after or None,
                published_before=published_before or None,
            )

        if candidates is None:
            st.error("No response received from the API.")
        else:
            if keyword_tokens:
                results = [c for c in candidates if _matches_keyword(c, keyword_tokens)][:limit]
            else:
                results = candidates[:limit]

            if len(results) == 0:
                st.info("No results found.")
            else:
                st.success(f"{len(results)} cases found.")
                for case in results:
                    case_id = case.get("caseId", {}).get("en", "")
                    with st.expander(case.get("title", "Untitled")):
                        st.write(f"**Citation:** {case.get('citation', '')}")
                        if case_id and st.button("View Full Details", key=f"meta_{case_id}", use_container_width=False):
                            with st.spinner("Loading details..."):
                                meta = get_case_metadata(api_key, database_id, case_id)
                            if meta:
                                st.write(f"**Date:** {meta.get('decisionDate', 'Unknown')}")
                                st.write(f"**Docket:** {meta.get('docketNumber', '')}")
                        if case_id:
                            url = f"https://www.canlii.org/en/{database_id}/doc/{case_id}.html"
                            st.markdown(f"[View on CanLII]({url})")


def get_cases(api_key, database_id, result_count, published_after=None, published_before=None):
    try:
        url = f"{BASE_URL}/caseBrowse/en/{database_id}/"
        params = {"api_key": api_key, "offset": 0, "resultCount": result_count}
        if published_after:
            params["publishedAfter"] = published_after
        if published_before:
            params["publishedBefore"] = published_before

        r = requests.get(url, params=params, timeout=20)
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
        url = f"{BASE_URL}/caseBrowse/en/{database_id}/{case_id}/"
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
