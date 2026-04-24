import streamlit as st

# Title of App
st.title("Web Development Lab03")

# Assignment Data 
# TODO: Fill out your team number, section, and team members

st.header("CS 1301")
st.subheader("Web Development - Section A")
st.subheader("Jake Jester, Daniel Mahabadi")


# Introduction
# TODO: Write a quick description for all of your pages in this lab below, in the form:
#       1. **Page Name**: Description
#       2. **Page Name**: Description
#       3. **Page Name**: Description
#       4. **Page Name**: Description

st.write("""
Welcome to our Streamlit Web Development Lab03 app! You can navigate between the pages using the sidebar to the left. The following pages are:

1. **Steam Analyzer**: Allows users to enter a Steam ID to view profile information, including username, avatar, online status, and last logoff time, while also analyzing owned games through interactive charts and playtime statistics.
2. **Chatbot Assistant**: Provides a Steam-themed chatbot that can answer questions and interact with users while maintaining conversation context.
3. **Steam Playstyle Analyzer**: Uses Steam API data and Google Gemini to generate creative analyses, recommendations, and player profiles based on a user’s game library and playtime.
4. **Steam Data Chatbot**: Lets users chat with an AI assistant that answers questions using real Steam profile and game data from the Steam API.""")
