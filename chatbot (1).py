import streamlit as st
from google import genai
# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DSA Chatbot",
    page_icon="🧠"
)

st.title("🧠 DSA Doubt Solver")
st.caption("Ask anything about Data Structures & Algorithms")

# ── Configure Gemini ─────────────────────────────────────────────────────────
API_KEY = "AIzaSyDymw04y6EiYYzCD3KaXnQ9rVtt-Sh7trc"

genai.configure(api_key=API_KEY)

# ── Load knowledge base ──────────────────────────────────────────────────────
@st.cache_data
def load_kb():
    with open("Dsa chatbot.txt", "r", encoding="utf-8") as f:
        return f.read()

kb = load_kb()

# ── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""
You are a DSA teacher.

Your job:
- Clear doubts about Data Structures and Algorithms
- Explain in very simple and easy-to-understand language
- Give examples whenever needed
- Answer only DSA-related questions
- If question is outside DSA, politely say you only answer DSA questions

Knowledge Base:
{kb}
"""

# ── Create Gemini Model ──────────────────────────────────────────────────────
@st.cache_resource
def get_model():

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

    return model

model = get_model()

# ── Chat Session ─────────────────────────────────────────────────────────────
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Display Chat History ─────────────────────────────────────────────────────
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── User Input ───────────────────────────────────────────────────────────────
if user_input := st.chat_input("Ask a DSA question..."):

    # User message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Assistant response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:
                response = st.session_state.chat.send_message(user_input)

                reply = response.text

            except Exception as e:
                reply = f"❌ Error: {str(e)}"

        st.markdown(reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })