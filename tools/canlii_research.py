import os

import requests
import streamlit as st
from dotenv import load_dotenv

from tools import ui

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

    try:
        r = requests.get(
            f"{BASE_URL}/caseBrowse/en/", params={"api_key": api_key}, timeout=15
        )
    except Exception as e:
        ui.banner("err", f"Could not reach the CanLII API: {e}")
        return {}

    if r.status_code != 200:
        ui.banner("err", _explain_status(r.status_code, "loading the court list"))
        return {}

    databases = {db["name"]: db["databaseId"] for db in r.json().get("caseDatabases", [])}
    st.session_state["canlii_databases"] = databases
    return databases


def _explain_status(code, action):
    """Turn a bare HTTP code into something a non-developer can act on."""
    if code in (401, 403):
        return (
            f"<b>CanLII rejected the API key</b> while {action} (HTTP {code}). "
            "Check that the key is correct and still active."
        )
    if code == 429:
        return (
            f"<b>Rate limit reached</b> while {action} (HTTP {code}). "
            "Wait a minute, then try again with fewer results."
        )
    return f"<b>CanLII returned HTTP {code}</b> while {action}."


def _matches_keyword(case, tokens):
    """True if every keyword token appears in the case's title or citation.
    This is a title/citation match, not a full-text search of the decision
    -- CanLII's public API doesn't expose decision text for searching."""
    haystack = f"{case.get('title', '')} {case.get('citation', '')}".lower()
    return all(token in haystack for token in tokens)


def run():
    ui.page_head(
        "Tool 02",
        "CanLII Research",
        "Browse Canadian court and tribunal decisions through the CanLII API. "
        "Pick a court, optionally narrow by keyword or date, and open any "
        "result on canlii.org.",
    )

    api_key = os.getenv("CANLII_API_KEY", "")
    if not api_key:
        api_key = st.sidebar.text_input("CanLII API key", type="password")

    if not api_key:
        ui.banner(
            "warn",
            "<b>No API key configured.</b> Add <code>CANLII_API_KEY</code> to "
            "your <code>.env</code> file, or paste a key into the sidebar box "
            "to use one for this session only.",
        )
        ui.hint(
            "Keys are issued free by CanLII at "
            "<a href='https://www.canlii.org/en/info/api.html' target='_blank'>"
            "canlii.org/en/info/api.html</a>.",
        )
        return

    with st.spinner("Loading courts and tribunals…"):
        databases = _get_databases(api_key)

    if not databases:
        return

    with st.container(border=True):
        st.markdown('<div class="card-title">Search</div>', unsafe_allow_html=True)

        db_label = st.selectbox("Court or tribunal", sorted(databases.keys()))
        keyword = st.text_input(
            "Keyword",
            placeholder="e.g. negligence",
            help=(
                "CanLII's API has no full-text search, so this matches against "
                "case titles and citations only — not the text of decisions."
            ),
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            published_after = st.text_input("Published after", placeholder="YYYY-MM-DD")
        with c2:
            published_before = st.text_input("Published before", placeholder="YYYY-MM-DD")
        with c3:
            limit = st.number_input("Results", min_value=1, max_value=100, value=10)

        search_clicked = st.button("Search", type="primary")

    if search_clicked:
        st.session_state["canlii_query"] = {
            "database_id": databases[db_label],
            "tokens": [t.lower() for t in keyword.split() if t.strip()],
            "after": published_after or None,
            "before": published_before or None,
            "limit": int(limit),
        }
        st.session_state.pop("canlii_details", None)

    query = st.session_state.get("canlii_query")
    if not query:
        ui.hint("Choose a court and run a search to see decisions.")
        return

    with st.spinner("Searching CanLII…"):
        # When scanning for a keyword, pull a larger candidate batch so
        # there's something worth filtering; otherwise just browse the
        # most recent decisions.
        scan_count = MAX_SCAN if query["tokens"] else query["limit"]
        candidates = get_cases(
            api_key,
            query["database_id"],
            scan_count,
            published_after=query["after"],
            published_before=query["before"],
        )

    if candidates is None:
        return

    if query["tokens"]:
        results = [c for c in candidates if _matches_keyword(c, query["tokens"])][
            : query["limit"]
        ]
    else:
        results = candidates[: query["limit"]]

    if not results:
        ui.banner(
            "info",
            "<b>No matching decisions.</b> Keyword matching only covers titles "
            "and citations, so try a party name or a broader term.",
        )
        return

    scanned_note = (
        f" (filtered from the {len(candidates)} most recent decisions)"
        if query["tokens"]
        else ""
    )
    ui.banner("ok", f"<b>{len(results)} decision(s) found.</b>{scanned_note}")

    details = st.session_state.setdefault("canlii_details", {})

    for case in results:
        case_id = case.get("caseId", {}).get("en", "")
        title = case.get("title", "Untitled")
        citation = case.get("citation", "")

        with st.expander(title):
            if citation:
                st.markdown(f"**Citation:** {citation}")

            if case_id:
                url = f"https://www.canlii.org/en/{query['database_id']}/doc/{case_id}.html"

                meta = details.get(case_id)
                if meta:
                    st.markdown(f"**Decision date:** {meta.get('decisionDate', 'Unknown')}")
                    st.markdown(f"**Docket:** {meta.get('docketNumber', '—') or '—'}")
                elif st.button("Load details", key=f"meta_{case_id}"):
                    with st.spinner("Loading…"):
                        fetched = get_case_metadata(api_key, query["database_id"], case_id)
                    if fetched:
                        details[case_id] = fetched
                        st.rerun()

                st.markdown(f"[Open on CanLII →]({url})")


def get_cases(api_key, database_id, result_count, published_after=None, published_before=None):
    try:
        params = {"api_key": api_key, "offset": 0, "resultCount": result_count}
        if published_after:
            params["publishedAfter"] = published_after
        if published_before:
            params["publishedBefore"] = published_before

        r = requests.get(
            f"{BASE_URL}/caseBrowse/en/{database_id}/", params=params, timeout=20
        )
        if r.status_code == 200:
            return r.json().get("cases", [])
        ui.banner("err", _explain_status(r.status_code, "searching"))
        return None
    except Exception as e:
        ui.banner("err", f"Could not reach the CanLII API: {e}")
        return None


def get_case_metadata(api_key, database_id, case_id):
    try:
        r = requests.get(
            f"{BASE_URL}/caseBrowse/en/{database_id}/{case_id}/",
            params={"api_key": api_key},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json()
        ui.banner("err", _explain_status(r.status_code, "loading case details"))
        return None
    except Exception as e:
        ui.banner("err", f"Could not reach the CanLII API: {e}")
        return None
