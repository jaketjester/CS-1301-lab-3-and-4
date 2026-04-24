import streamlit as st
import requests
import pandas as pd
from google import genai

st.title("Steam Playstyle Analyzer")
st.caption("Use Steam profile data and Gemini to generate a creative analysis of a player's gaming habits.")

STEAM_API_KEY = "711F8E8AB044BF6017D9E09793DAF5B1"
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)

steam_id = st.text_input("Enter a Steam ID")
num_games = st.slider("How many top games should be analyzed?", 3, 15, 5)
analysis_style = st.selectbox(
    "Choose analysis style",
    ["Playstyle Analysis", "Game Recommendation Report", "Funny Roast", "Gaming Personality Profile"]
)

if st.button("Generate Analysis"):
    if not steam_id:
        st.warning("Please enter a Steam ID.")
    else:
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
            else:
                player = players[0]
                profile_name = player["personaname"]

                games_url = (
                    f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
                    f"?key={STEAM_API_KEY}&steamid={steam_id}&include_appinfo=true&format=json"
                )
                games_response = requests.get(games_url, timeout=10)
                games_data = games_response.json()

                if "games" not in games_data["response"]:
                    st.warning("This profile may be private, or no games were found.")
                else:
                    games = games_data["response"]["games"]
                    df = pd.DataFrame(games)
                    df["playtime_hours"] = (df["playtime_forever"] / 60).round(2)
                    top_games = df.sort_values(by="playtime_hours", ascending=False).head(num_games)
                    total_games = len(df)
                    total_hours = round(df["playtime_hours"].sum(), 2)

                    st.subheader(f"Steam Data for {profile_name}")
                    st.write(f"Total games owned: {total_games}")
                    st.write(f"Total playtime hours: {total_hours}")
                    st.dataframe(top_games[["name", "playtime_hours"]], use_container_width=True)

                    steam_data_text = f"""
Profile name: {profile_name}
Total games owned: {total_games}
Total playtime hours: {total_hours}

Top games by playtime:
{top_games[["name", "playtime_hours"]].to_string(index=False)}
"""

                    if analysis_style == "Playstyle Analysis":
                        prompt = f"""
You are a gaming analyst.
Using the Steam data below, write a detailed but readable analysis of this player's gaming habits,
favorite types of games, and overall playstyle.

Steam data:
{steam_data_text}
"""
                    elif analysis_style == "Game Recommendation Report":
                        prompt = f"""
You are a game recommendation expert.
Using the Steam data below, explain what kinds of games this player seems to enjoy and recommend 3 games they might like.
Give a short reason for each recommendation.

Steam data:
{steam_data_text}
"""
                    elif analysis_style == "Funny Roast":
                        prompt = f"""
You are a playful gaming commentator.
Using the Steam data below, write a funny and lighthearted roast of this player's gaming habits.
Keep it school-appropriate and harmless.

Steam data:
{steam_data_text}
"""
                    else:
                        prompt = f"""
You are a creative writer.
Using the Steam data below, write a 'gaming personality profile' for this player.
Describe what kind of gamer they are in a fun and engaging way.

Steam data:
{steam_data_text}
"""

                    try:
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt
                        )

                        if hasattr(response, "text") and response.text:
                            st.subheader("Gemini Output")
                            st.write(response.text)
                        else:
                            st.warning("Gemini returned no text.")

                    except Exception as e:
                        error_text = str(e)
                        st.error(f"Full error: {error_text}")

                        if "429" in error_text or "quota" in error_text.lower():
                            st.warning("Too many requests right now. Wait a few seconds and try again.")
                        elif "safety" in error_text.lower() or "blocked" in error_text.lower():
                            st.warning("The response was blocked. Try another analysis style.")
                        elif "400" in error_text:
                            st.warning("Bad request. The model name or request format may be wrong.")
                        else:
                            st.warning("Something went wrong while generating the analysis.")

        except Exception as e:
            st.error(f"Error loading Steam data: {e}")
