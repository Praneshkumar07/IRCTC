import streamlit as st
import google.generativeai as genai

# ── Hardcoded config ──────────────────────────────────────────────────────────
API_KEY = "AIzaSyDymw04y6EiYYzCD3KaXnQ9rVtt-Sh7trc"
KB_FILE = "IRCTC.txt"

# ── Load knowledge base ───────────────────────────────────────────────────────
with open(KB_FILE, "r", encoding="utf-8") as f:
    KB_TEXT = f.read()

# ── Configure Gemini ──────────────────────────────────────────────────────────
genai.configure(api_key=API_KEY)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IRCTC Customer Care",
    page_icon="🚂",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background-color: #f0f4f8;
    }

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

    .irctc-header h1 {
        margin: 0;
        font-size: 1.6rem;
    }

    .irctc-header p {
        margin: 0;
        font-size: 0.85rem;
        opacity: 0.85;
    }

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

    .chat-label.right {
        text-align: right;
    }

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

    .stButton > button:hover {
        background: #003d87 !important;
    }

    .stSidebar {
        background-color: #e8eef7;
    }
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
    st.markdown("Powered by Gemini")

    st.markdown("---")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()

    st.markdown("---")
    st.markdown("### Suggested Questions")

    suggestions = [
        "IRCTC customer care number",
        "How to cancel a ticket?",
        "What is the refund policy?",
        "How to check PNR status?",
    ]

    for q in suggestions:
        if st.button(q, key=q):
            st.session_state.pending_input = q

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    st.session_state.chat = None

if "pending_input" not in st.session_state:
    st.session_state.pending_input = ""

# ── Create Chat Session ───────────────────────────────────────────────────────
def get_chat():
    if st.session_state.chat is None:

        system_prompt = f"""
You are an IRCTC Customer Care Executive.

Your job:
- Reply politely and professionally.
- Only answer from the provided knowledge base.
- If information is unavailable, reply:
  "I don't know the information."
- Do not make up answers.

Knowledge Base:
{KB_TEXT}
"""

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_prompt
        )

        st.session_state.chat = model.start_chat(history=[])

    return st.session_state.chat

# ── Display Chat ──────────────────────────────────────────────────────────────
chat_container = st.container()

with chat_container:

    if not st.session_state.messages:
        st.markdown(
            """
            <p style='text-align:center;color:#888;margin-top:2rem'>
            👋 Hello! How can I help you today?
            </p>
            """,
            unsafe_allow_html=True,
        )

    for msg in st.session_state.messages:

        if msg["role"] == "user":

            st.markdown(
                '<p class="chat-label right">You</p>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="user-bubble">{msg["content"]}</div>',
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                '<p class="chat-label">🚂 IRCTC Assistant</p>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="bot-bubble">{msg["content"]}</div>',
                unsafe_allow_html=True
            )

# ── Input Area ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])

with col1:
    default_val = st.session_state.pending_input

    user_input = st.text_input(
        "Your question",
        value=default_val,
        placeholder="Type your question here...",
        label_visibility="collapsed",
        key="user_input"
    )

with col2:
    send = st.button("Send")

# ── Clear Pending Input ───────────────────────────────────────────────────────
if st.session_state.pending_input:
    st.session_state.pending_input = ""

# ── Handle Message ────────────────────────────────────────────────────────────
if send and user_input.strip():

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.spinner("Fetching answer..."):

        try:
            chat = get_chat()

            response = chat.send_message(user_input)

            answer = response.text

        except Exception as e:
            answer = f"❌ Error: {str(e)}"

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()