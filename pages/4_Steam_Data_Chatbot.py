import streamlit as st
import requests
import pandas as pd
from google import genai

st.title("Steam Data Chatbot")
st.caption("Ask questions about a Steam profile using real Steam API data.")

STEAM_API_KEY = "711F8E8AB044BF6017D9E09793DAF5B1"
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)

steam_id = st.text_input("Enter a Steam ID")
num_games = st.slider("How many top games should the chatbot use?", 3, 15, 5)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "steam_context" not in st.session_state:
    st.session_state.steam_context = ""

if "profile_name" not in st.session_state:
    st.session_state.profile_name = ""

if st.button("Load Steam Data"):
    try:
        profile_url = (
            f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
            f"?key={STEAM_API_KEY}&steamids={steam_id}"
        )
        profile_response = requests.get(profile_url, timeout=10)
        profile_data = profile_response.json()
        players = profile_data["response"]["players"]

        if len(players) == 0:
            st.error("No Steam profile found for that Steam ID.")
            st.session_state.steam_context = ""
        else:
            player = players[0]
            st.session_state.profile_name = player["personaname"]

            games_url = (
                f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
                f"?key={STEAM_API_KEY}&steamid={steam_id}&include_appinfo=true&format=json"
            )
            games_response = requests.get(games_url, timeout=10)
            games_data = games_response.json()

            if "games" not in games_data["response"]:
                st.warning("This profile may be private, or no games were found.")
                st.session_state.steam_context = ""
            else:
                games = games_data["response"]["games"]
                df = pd.DataFrame(games)
                df["playtime_hours"] = (df["playtime_forever"] / 60).round(2)
                top_games = df.sort_values(by="playtime_hours", ascending=False).head(num_games)
                total_games = len(df)
                total_hours = round(df["playtime_hours"].sum(), 2)

                st.subheader(f"Loaded Steam data for {st.session_state.profile_name}")
                st.dataframe(top_games[["name", "playtime_hours"]], use_container_width=True)

                st.session_state.steam_context = f"""
Profile name: {st.session_state.profile_name}
Total games owned: {total_games}
Total playtime hours: {total_hours}

Top games by playtime:
{top_games[["name", "playtime_hours"]].to_string(index=False)}
"""
                st.session_state.messages = []

    except Exception as e:
        st.error(f"Error loading Steam data: {e}")
        st.session_state.steam_context = ""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask about this Steam profile...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.steam_context == "":
        bot_reply = "Please load Steam data first so I can answer using the profile."
    else:
        system_prompt = f"""
You are a Steam gaming assistant.
Use the Steam profile data below to answer the user's questions.
Base your answers on the provided Steam data when possible.
If the user asks for recommendations, use the player's top games and playtime habits.
Be friendly, clear, and conversational.

Steam data:
{st.session_state.steam_context}
"""

        recent_messages = st.session_state.messages[-8:]

        full_conversation = system_prompt + "\n"
        for message in recent_messages:
            role = "User" if message["role"] == "user" else "Assistant"
            full_conversation += f"{role}: {message['content']}\n"

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_conversation
            )

            if hasattr(response, "text") and response.text:
                bot_reply = response.text
            else:
                bot_reply = "Gemini returned no text."

        except Exception as e:
            error_text = str(e)
            st.error(f"Full error: {error_text}")

            if "429" in error_text or "quota" in error_text.lower():
                bot_reply = "Too many requests right now. Wait a few seconds and try again."
            elif "safety" in error_text.lower() or "blocked" in error_text.lower():
                bot_reply = "I cannot respond to that one. Try asking something else."
            elif "400" in error_text:
                bot_reply = "Bad request. The model name or request format may be wrong."
            else:
                bot_reply = "Something went wrong while generating a response."

    with st.chat_message("assistant"):
        st.write(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
