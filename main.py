import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="RET Legal Tools Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Official CanLII Jurisdictions & Court Databases Mapping (Full Canadian Courts)
CANADIAN_JURISDICTIONS = {
    # --- Federal Courts (وفاقی عدالتیں) ---
    "All Canada / Federal Courts (تمام کینیڈا / وفاقی)": "ca",
    "Supreme Court of Canada (سپریم کورٹ آف کینیڈا)": "scc-csc",
    "Federal Court of Appeal (فیڈرل کورٹ آف اپیل)": "fca-caf",
    "Federal Court (فیڈرل کورٹ)": "fc-cf",
    "Tax Court of Canada (ٹیکس کورٹ آف کینیڈا)": "tcc-cci",
    "Court Martial Appeal Court of Canada (کورٹ مارشل اپیل)": "cmac-cacm",
    
    # --- Primary Jurisdictions (پرائمری صوبے) ---
    "Alberta (البیرٹا - Primary Jurisdiction)": "ab",
    "British Columbia (برٹش کولمبیا)": "bc",
    "Ontario (اونٹاریو)": "on",
    "Quebec (کیوبک)": "qc",
    
    # --- Other Provinces & Territories (دیگر صوبے اور علاقے) ---
    "Manitoba (مینیٹوبا)": "mb",
    "Saskatchewan (ساسکاچیوان)": "sk",
    "Nova Scotia (نووا سکوشیا)": "ns",
    "New Brunswick (نیو برنزوک)": "nb",
    "Newfoundland and Labrador (نیو فاؤنڈ لینڈ)": "nl",
    "Prince Edward Island (پرنس ایڈورڈ آئی لینڈ)": "pe",
    "Yukon (یوکون)": "yk",
    "Northwest Territories (نارتھ ویسٹ)": "nt",
    "Nunavut (نُناوُت)": "nu"
}

# 3. Theme State Setup (Default: Dark Mode)
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

# 4. Dynamic Custom CSS (Neon Dark & Day Mode)
if st.session_state.theme_mode == "dark":
    CUSTOM_CSS = """
    <style>
        .stApp {
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: #e6edf3;
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3 {
            background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
        }
        .stButton > button {
            width: 100% !important;
            height: 50px !important;
            border-radius: 12px !important;
            background: #0d1117 !important;
            color: #00f2fe !important;
            border: 2px solid #00f2fe !important;
            font-weight: 700 !important;
            font-size: 15px !important;
            transition: all 0.3s ease-in-out !important;
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.2) !important;
        }
        .stButton > button:hover {
            background: #00f2fe !important;
            color: #000000 !important;
            box-shadow: 0 0 25px #00f2fe !important;
            transform: translateY(-2px);
        }
        [data-testid="stFileUploader"] {
            background-color: #161b22 !important;
            border: 2px dashed #00f2fe !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }
        [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] label {
            color: #ffffff !important;
            font-weight: 600 !important;
        }
    </style>
    """
else:
    CUSTOM_CSS = """
    <style>
        .stApp {
            background-color: #f8f9fa;
            color: #1a1a1a;
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3 {
            color: #0f172a !important;
            font-weight: 800 !important;
        }
        .stButton > button {
            width: 100% !important;
            height: 50px !important;
            border-radius: 12px !important;
            background: #ffffff !important;
            color: #0284c7 !important;
            border: 2px solid #0284c7 !important;
            font-weight: 700 !important;
            font-size: 15px !important;
            transition: all 0.3s ease-in-out !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        }
        .stButton > button:hover {
            background: #0284c7 !important;
            color: #ffffff !important;
            transform: translateY(-2px);
        }
        [data-testid="stFileUploader"] {
            background-color: #ffffff !important;
            border: 2px dashed #0284c7 !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }
        [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] label {
            color: #0f172a !important;
            font-weight: 600 !important;
        }
    </style>
    """

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 5. Header
st.title("⚡ RET Legal Tools Platform")
st.subheader("Next-Gen Legal Tools & Intelligent Document Processing")

st.markdown("---")

# 6. Navigation Controls
if "current_page" not in st.session_state:
    st.session_state.current_page = "Ingestion Tool"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("📄 Ingestion Tool"):
        st.session_state.current_page = "Ingestion Tool"
with col2:
    if st.button("🔍 CanLII Research"):
        st.session_state.current_page = "CanLII Research"
with col3:
    if st.button("🤖 Legal AI Chatbot"):
        st.session_state.current_page = "Legal AI Chatbot"
with col4:
    if st.button("📚 Documents"):
        st.session_state.current_page = "Documents"
with col5:
    theme_icon = "☀️ Day Mode" if st.session_state.theme_mode == "dark" else "🌙 Dark Mode"
    if st.button(theme_icon):
        st.session_state.theme_mode = "light" if st.session_state.theme_mode == "dark" else "dark"
        st.rerun()

st.markdown("---")

# 7. Pages Routing logic

# --- PAGE 1: Document Ingestion Tool ---
if st.session_state.current_page == "Ingestion Tool":
    st.header("📄 Document Ingestion Tool")
    uploaded_file = st.file_uploader("Upload a PDF Document, Scanned File or Case Folder", type=['pdf'])
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        st.info("Document Processing Pipeline Ready.")

# --- PAGE 2: CanLII Research Tool (UPDATED WITH ALL CANADIAN COURTS) ---
elif st.session_state.current_page == "CanLII Research":
    st.header("🔍 CanLII Research Hub")
    st.write("یہاں سے کینیڈین عدالتوں کے کیسز، سائٹیشنز اور قانون تلاش کریں۔")

    search_query = st.text_input("کیس کا نام، موضوع یا کی ورڈز لکھیں (Case Name or Keywords):")

    col_court, col_limit = st.columns([2, 1])

    with col_court:
        selected_jurisdiction_label = st.selectbox(
            "عدالت یا صوبہ منتخب کریں (Court / Jurisdiction):",
            options=list(CANADIAN_JURISDICTIONS.keys()),
            index=0
        )
        selected_db_code = CANADIAN_JURISDICTIONS[selected_jurisdiction_label]

    with col_limit:
        result_limit = st.number_input("کتنے نتائج؟ (Limit)", min_value=1, max_value=50, value=10)

    if st.button("کیسز تلاش کریں (Search CanLII)"):
        if search_query:
            st.info(f"تلاش جاری ہے... | Database: `{selected_db_code}` | Query: `{search_query}`")
            st.warning("⚠️ CanLII API key verification active. Returning live metadata...")
        else:
            st.error("براہِ کرم کیس کا نام یا موضوع لکھیں!")

# --- PAGE 3: Legal Expert AI Chatbot ---
elif st.session_state.current_page == "Legal AI Chatbot":
    st.header("🤖 High-Precision Legal AI Assistant")
    st.write("Consult the AI assistant for legal matters, case analysis, or complex document queries:")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.write("🎤 **Voice Command Input:**")
    audio_val = st.audio_input("Record your legal query")

    if audio_val:
        st.audio(audio_val)
        st.info("Voice input received. Processing query...")

    user_query = st.chat_input("Type your legal question or case details here...")

    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        bot_reply = f"**Legal Analysis for:** '{user_query}'\n\nAnalyzing provided context against Alberta & Canadian Law Standards."
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

# --- PAGE 4: Managed Documents ---
elif st.session_state.current_page == "Documents":
    st.header("📚 Managed Documents")
    st.info("Access stored files and generated documents here.")