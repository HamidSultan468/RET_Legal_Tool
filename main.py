import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="RET Legal Tools",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Complete Cyberpunk / Neon Glowing Custom CSS
CUSTOM_CSS = """
<style>
    /* Background and Main Theme */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        color: #e6edf3;
        font-family: 'Inter', sans-serif;
    }

    /* Gradient Headings */
    h1, h2, h3 {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        letter-spacing: 1px;
    }

    /* Glowing Buttons Design */
    .stButton > button {
        width: 100% !important;
        height: 50px !important;
        border-radius: 12px !important;
        background: #0d1117 !important;
        color: #00f2fe !important;
        border: 2px solid #00f2fe !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.2) !important;
    }

    /* Button Hover Effect */
    .stButton > button:hover {
        background: #00f2fe !important;
        color: #000000 !important;
        box-shadow: 0 0 25px #00f2fe, 0 0 50px #00f2fe !important;
        transform: translateY(-2px);
    }
</style>
"""

# Inject CSS into Streamlit
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 3. Main Header
st.title("⚡ RET Legal Tools Platform")
st.subheader("Next-Gen Legal Tools & Document Processing")

st.markdown("---")

# 4. Equal Size Buttons Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.button("📄 Ingestion Tool")
with col2:
    st.button("🔍 CanLII Research")
with col3:
    st.button("📚 Documents")
with col4:
    st.button("⚙️ Settings")

st.markdown("---")