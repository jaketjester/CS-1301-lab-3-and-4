import streamlit as st
import requests
import pandas as pd
from datetime import datetime

api_key = "711F8E8AB044BF6017D9E09793DAF5B1"
st.title("Steam Profile Analyzer")
st.write("This app analyzes a Steam user's profile and game playtime.")
st.write("Enter a Steam ID to view profile information and game statistics.")
steam_id = st.text_input("Enter Steam ID")
num_games = st.slider("How many top games do you want to see?", 5, 20, 10)

if steam_id:
    #Profile Info
    profile_url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}"
    profile_response = requests.get(profile_url)
    if profile_response.status_code != 200:
        st.error("API request failed.")
    try:
        profile_data = profile_response.json()
        players = profile_data["response"]["players"]
        if len(players) == 0:
            st.error("No player found. Check the Steam ID.")
        else:
            player = players[0]
            st.subheader(player["personaname"])
            st.image(player["avatarfull"], width=150)
            st.write("Profile URL:", player["profileurl"])
            if "lastlogoff" in player:
                last_logoff = datetime.fromtimestamp(player["lastlogoff"])
                st.write("Last logoff:", last_logoff)
            if "personastate" in player:
                if player["personastate"] == 0:
                    st.write("Status: Offline")
                else:
                    st.write("Status: Online")
            #Owned Games
            games_url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id}&include_appinfo=true&format=json"
            games_response = requests.get(games_url)
            try:
                games_data = games_response.json()
                if "games" not in games_data["response"]:
                    st.warning("This profile may be private, or no games were found.")
                else:
                    games = games_data["response"]["games"]
                    df = pd.DataFrame(games)
                    df["playtime_hours"] = df["playtime_forever"] / 60
                    top_games = df.sort_values(by="playtime_hours", ascending=False).head(num_games)
                    st.write("Total Games:", len(df))
                    st.write("Total Playtime (hours):", round(df["playtime_hours"].sum(), 2))
                    st.subheader("Top Games by Playtime")
                    st.bar_chart(top_games.set_index("name")["playtime_hours"])
                    st.subheader("Game Data Table")
                    st.dataframe(top_games[["name", "playtime_hours"]])
            except:
                st.error("Could not load game data.")
    except:
        st.error("Could not load profile data.")
