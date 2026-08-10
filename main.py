import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="RET Legal Tools",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Theme State (Default: Dark Mode)
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

# 2. Dynamic Custom CSS (Switches between Dark and Light Mode)
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
    # Clean Light / Day Mode CSS
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

# 3. App Header
st.title("⚡ RET Legal Tools Platform")
st.subheader("Next-Gen Legal Tools & Intelligent Document Processing")

st.markdown("---")

# 4. Navigation Session State Setup
if "current_page" not in st.session_state:
    st.session_state.current_page = "Ingestion Tool"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 5. Equal Size Interactive Buttons Row (Settings replaced with Theme Toggle)
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
    # Dynamic Theme Button Label based on current mode
    theme_icon = "☀️ Day Mode" if st.session_state.theme_mode == "dark" else "🌙 Dark Mode"
    if st.button(theme_icon):
        if st.session_state.theme_mode == "dark":
            st.session_state.theme_mode = "light"
        else:
            st.session_state.theme_mode = "dark"
        st.rerun()

st.markdown("---")

# 6. Dynamic Content Display Based on Active Button

# --- PAGE 1: Document Ingestion Tool ---
if st.session_state.current_page == "Ingestion Tool":
    st.header("📄 Document Ingestion Tool")
    
    uploaded_file = st.file_uploader("Upload a PDF Document or Case File", type=['pdf'])
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        st.info("Document Processing Pipeline Ready.")

# --- PAGE 2: CanLII Research Hub ---
elif st.session_state.current_page == "CanLII Research":
    st.header("🔍 CanLII Research Hub")
    st.info("CanLII legal research tool is active and operational.")

# --- PAGE 3: Legal Expert AI Chatbot (Typing & Voice Command) ---
elif st.session_state.current_page == "Legal AI Chatbot":
    st.header("🤖 High-Precision Legal AI Assistant")
    st.write("Consult the AI assistant for legal matters, case analysis, or complex document queries:")

    # Display Previous Chat Messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Voice Input Option
    st.write("🎤 **Voice Command Input:**")
    audio_val = st.audio_input("Record your legal query")

    if audio_val:
        st.audio(audio_val)
        st.info("Voice input received. Processing query...")

    # Text Typing Input Option
    user_query = st.chat_input("Type your legal question or case details here...")

    if user_query:
        # User Message
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # AI Bot Response Placeholder
        bot_reply = f"**Legal Analysis for:** '{user_query}'\n\nAnalyzing the provided context and relevant legal statutes. (LLM API response will be rendered here)."
        
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

# --- PAGE 4: Managed Documents ---
elif st.session_state.current_page == "Documents":
    st.header("📚 Managed Documents")
    st.info("Access stored files and generated documents here.")