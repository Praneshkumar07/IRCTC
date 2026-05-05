import streamlit as st
from google import genai

# ── Hardcoded config (from original code) ────────────────────────────────────
API_KEY = "AIzaSyDymw04y6EiYYzCD3KaXnQ9rVtt-Sh7trc"
KB_FILE = "IRCTC.txt"

with open(KB_FILE, "r") as f:
    KB_TEXT = f.read()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IRCTC Customer Care",
    page_icon="🚂",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f0f4f8; }

    /* Header banner */
    .irctc-header {
        background: linear-gradient(135deg, #003580 0%, #0057b8 100%);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .irctc-header h1 { margin: 0; font-size: 1.6rem; }
    .irctc-header p  { margin: 0; font-size: 0.85rem; opacity: 0.85; }

    /* Chat bubbles */
    .user-bubble {
        background: #0057b8;
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 18px 18px 4px 18px;
        max-width: 78%;
        margin-left: auto;
        margin-bottom: 0.5rem;
        word-wrap: break-word;
    }
    .bot-bubble {
        background: white;
        color: #1a1a2e;
        padding: 0.75rem 1rem;
        border-radius: 18px 18px 18px 4px;
        max-width: 78%;
        margin-right: auto;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        word-wrap: break-word;
    }
    .chat-label {
        font-size: 0.7rem;
        opacity: 0.55;
        margin-bottom: 2px;
    }
    .chat-label.right { text-align: right; }

    /* Input area */
    .stTextInput > div > div > input {
        border-radius: 24px !important;
        border: 2px solid #c8d8f0 !important;
        padding: 0.6rem 1.1rem !important;
    }
    .stButton > button {
        border-radius: 24px !important;
        background: #0057b8 !important;
        color: white !important;
        border: none !important;
        padding: 0.55rem 1.4rem !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover { background: #003d87 !important; }

    /* Sidebar */
    .stSidebar { background-color: #e8eef7; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="irctc-header">
    <span style="font-size:2.4rem">🚂</span>
    <div>
        <h1>IRCTC Customer Care</h1>
        <p>Ask me anything about bookings, refunds, trains & more</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🚂 IRCTC Assistant")
    st.markdown("Powered by Gemini 2.5 Flash")
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat     = None
        st.rerun()

    st.markdown("---")
    st.markdown("**Suggested questions**")
    suggestions = [
        "IRCTC customer care number",
        "How to cancel a ticket?",
        "What is the refund policy?",
        "How to check PNR status?",
    ]
    for q in suggestions:
        if st.button(q, key=f"sugg_{q}"):
            st.session_state.pending_input = q

# ── Session state init ────────────────────────────────────────────────────────
if "messages"      not in st.session_state: st.session_state.messages      = []
if "chat"          not in st.session_state: st.session_state.chat          = None
if "pending_input" not in st.session_state: st.session_state.pending_input = ""

# ── Build / cache chat session ────────────────────────────────────────────────
def get_chat():
    """Create (or return cached) Gemini chat session."""
    if st.session_state.chat is None:
        prompt = f"""
you are IRCTC Customer care executive your job is to provide answers to the questions asked by the customer,you should reply them politely,if the question is out of kb just say I don't know the info,only refer kb and provide the info.
{KB_TEXT}
"""
        client = genai.Client(api_key=API_KEY)
        st.session_state.chat = client.chats.create(
            model="gemini-2.5-flash",
            config={"system_instruction": prompt},
        )
    return st.session_state.chat

# ── Chat display ──────────────────────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.markdown(
            "<p style='text-align:center;color:#888;margin-top:2rem'>"
            "👋 Hello! How can I help you today?</p>",
            unsafe_allow_html=True,
        )
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown('<p class="chat-label right">You</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="user-bubble">{msg["content"]}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<p class="chat-label">🚂 IRCTC Assistant</p>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="bot-bubble">{msg["content"]}</div>',
                        unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])
with col1:
    default_val = st.session_state.pending_input
    user_input  = st.text_input("Your question", value=default_val,
                                placeholder="Type your question here…",
                                label_visibility="collapsed", key="user_input")
with col2:
    send = st.button("Send")

# Clear pending after it's been placed in the input
if st.session_state.pending_input:
    st.session_state.pending_input = ""

# ── Handle send ───────────────────────────────────────────────────────────────
if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Fetching answer…"):
        try:
            chat   = get_chat()
            resp   = chat.send_message(user_input)
            answer = resp.text
        except Exception as e:
            answer = f"❌ Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()