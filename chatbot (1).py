import streamlit as st
from google import genai

# ── Config ─────────────────────────────────────────────────────────────────────
API_KEY = "AIzaSyBuuXQEvB181nxQdH1YXwt4gOmSDPN8pbc"  # Set your Gemini API key here
KB_FILE = "IRCTC.txt"

try:
    with open(KB_FILE, "r") as f:
        KB_TEXT = f.read()
except FileNotFoundError:
    KB_TEXT = ""

SYSTEM_PROMPT = f"""You are an IRCTC Customer Care executive. Your job is to provide answers 
to the questions asked by the customer. You should reply politely. If the question is out of 
scope, just say I don't know the info. Only refer to the knowledge base and provide the info.

{KB_TEXT}"""

SUGGESTIONS = [
    "IRCTC customer care number",
    "How to cancel a ticket?",
    "What is the refund policy?",
    "How to check PNR status?",
    "Tatkal booking rules",
    "Train schedule enquiry",
]

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IRCTC Customer Care",
    page_icon="🚂",
    layout="centered",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #f0f4f8; }

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
.chat-label { font-size: 0.7rem; opacity: 0.55; margin-bottom: 2px; }
.chat-label.right { text-align: right; }

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
.stSidebar { background-color: #e8eef7; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="irctc-header">
    <span style="font-size:2.4rem">🚂</span>
    <div>
        <h1>IRCTC Customer Care</h1>
        <p>Ask me anything about bookings, refunds, trains &amp; more</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "messages"      not in st.session_state:
    st.session_state.messages      = []
if "pending_input" not in st.session_state:
    st.session_state.pending_input = ""
if "client"        not in st.session_state:
    st.session_state.client        = genai.Client(api_key=API_KEY)
if "chat"          not in st.session_state:
    st.session_state.chat          = st.session_state.client.chats.create(
        model="gemini-2.5-flash",
        config={"system_instruction": SYSTEM_PROMPT},
    )

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🚂 IRCTC Assistant")
    st.markdown("Powered by **Gemini 2.5 Flash**")
    st.markdown("---")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        # Recreate client and chat on clear
        st.session_state.client = genai.Client(api_key=API_KEY)
        st.session_state.chat   = st.session_state.client.chats.create(
            model="gemini-2.5-flash",
            config={"system_instruction": SYSTEM_PROMPT},
        )
        st.rerun()

    st.markdown("---")
    st.markdown("**Suggested questions**")
    for q in SUGGESTIONS:
        if st.button(q, key=f"sugg_{q}"):
            st.session_state.pending_input = q

# ── Chat display ───────────────────────────────────────────────────────────────
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
            st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="chat-label">🚂 IRCTC Assistant</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="bot-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        "Your question",
        value=st.session_state.pending_input,
        placeholder="Type your question here…",
        label_visibility="collapsed",
        key="user_input",
    )
with col2:
    send = st.button("Send")

if st.session_state.pending_input:
    st.session_state.pending_input = ""

# ── Handle send ────────────────────────────────────────────────────────────────
if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Fetching answer…"):
        try:
            resp   = st.session_state.chat.send_message(user_input)
            answer = resp.text
        except Exception as e:
            answer = f"❌ Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
