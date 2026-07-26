"""
canlii_page.py

CanLII Research Tool کا Streamlit صفحہ۔
یہاں سے یوزر عدالت چن کر کیسز دیکھ سکتا ہے، اور کیس کی تفصیل پڑھ سکتا ہے۔

اس فائل کو اپنی main app میں import کر کے sidebar navigation میں جوڑ دیں۔
"""

import streamlit as st
from canlii_client import CanLIIClient


def render_canlii_page():
    """CanLII صفحے کو دکھانے والا مرکزی فنکشن"""

    st.title("📚 CanLII Research Tool")
    st.write("یہاں سے کینیڈین عدالتوں کے کیسز اور قانون تلاش کریں۔")

    # ---------- API Key چیک کرنا ----------
    api_key = st.session_state.get("canlii_api_key", "")

    with st.sidebar:
        st.subheader("CanLII Settings")
        api_key_input = st.text_input(
            "CanLII API Key",
            value=api_key,
            type="password",
            help="API key CanLII کی ویب سائٹ سے حاصل کریں۔",
        )
        if api_key_input:
            st.session_state["canlii_api_key"] = api_key_input
            api_key = api_key_input

    if not api_key:
        st.warning("پہلے بائیں طرف اپنی CanLII API key درج کریں۔")
        return

    client = CanLIIClient(api_key)

    # ---------- عدالت کا انتخاب ----------
    st.subheader("1️⃣ عدالت منتخب کریں")

    if "databases" not in st.session_state:
        with st.spinner("عدالتوں کی فہرست لائی جا رہی ہے..."):
            try:
                data = client.get_case_databases()
                st.session_state["databases"] = data.get("caseDatabases", [])
            except Exception as e:
                st.error(f"خرابی: {e}")
                return

    databases = st.session_state["databases"]
    db_names = {db["name"]: db["databaseId"] for db in databases}

    if not db_names:
        st.error("کوئی عدالت نہیں ملی۔")
        return

    selected_name = st.selectbox("عدالت چنیں", list(db_names.keys()))
    selected_db_id = db_names[selected_name]

    # ---------- کیسز کی فہرست ----------
    st.subheader("2️⃣ کیسز دیکھیں")

    col1, col2 = st.columns(2)
    with col1:
        published_after = st.text_input("اس تاریخ کے بعد (YYYY-MM-DD)", "")
    with col2:
        published_before = st.text_input("اس تاریخ سے پہلے (YYYY-MM-DD)", "")

    if st.button("کیسز لائیں"):
        with st.spinner("کیسز لائے جا رہے ہیں..."):
            try:
                result = client.get_cases_in_database(
                    database_id=selected_db_id,
                    published_after=published_after or None,
                    published_before=published_before or None,
                )
                st.session_state["cases"] = result.get("cases", [])
            except Exception as e:
                st.error(f"خرابی: {e}")
                st.session_state["cases"] = []

    cases = st.session_state.get("cases", [])

    if cases:
        st.success(f"{len(cases)} کیسز ملے۔")
        for case in cases:
            with st.expander(case.get("title", "بغیر عنوان")):
                st.write(f"**Citation:** {case.get('citation', 'N/A')}")
                case_id = case.get("caseId", {}).get("en", "")

                if st.button("مکمل تفصیل دیکھیں", key=f"detail_{case_id}"):
                    with st.spinner("تفصیل لائی جا رہی ہے..."):
                        try:
                            details = client.get_case_details(selected_db_id, case_id)
                            st.json(details)
                        except Exception as e:
                            st.error(f"خرابی: {e}")


if __name__ == "__main__":
    render_canlii_page()
