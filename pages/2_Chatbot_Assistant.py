import streamlit as st
from google import genai

st.title("🎮 Steam Gaming Assistant")
st.caption("Ask me anything about Steam games, recommendations, or your gaming habits!")

API_KEY = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask about games, recommendations, stats...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    system_prompt = """
You are a knowledgeable and enthusiastic Steam gaming assistant.
Keep your responses friendly and engaging like you're talking to a fellow gamer.
"""

    # ✅ CHANGED: only send recent messages, not the whole chat forever
    recent_messages = st.session_state.messages[-8:]

    full_conversation = system_prompt
    for message in recent_messages:
        role = "User" if message["role"] == "user" else "Assistant"
        full_conversation += f"{role}: {message['content']}\n"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # ✅ CHANGED: try newer model
            contents=full_conversation
        )

        bot_reply = response.text

    except Exception as e:
        # ✅ IMPORTANT: this shows the exact real error
        st.error(f"Full error: {e}")

        if "429" in str(e) or "quota" in str(e).lower():
            bot_reply = "⚠️ Rate limit or quota issue. Wait a bit and try again."
        elif "400" in str(e):
            bot_reply = "⚠️ Bad request issue. The model name or request format may be wrong."
        else:
            bot_reply = "⚠️ Something went wrong."

    with st.chat_message("assistant"):
        st.write(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
