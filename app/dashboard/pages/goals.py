import pandas as pd
import streamlit as st

from app.dashboard.components.api_client import fetch_json

st.title("Goals and Intentions")
scenario_id = st.text_input("Scenario ID")
agent_id = st.text_input("Agent ID (optional)")

if scenario_id:
    params = {"agent_id": agent_id} if agent_id else None
    goals = fetch_json(f"/scenarios/{scenario_id}/goals", params=params)
    intentions = fetch_json(f"/scenarios/{scenario_id}/intentions", params=params)
    st.subheader("Goals")
    st.dataframe(pd.DataFrame(goals), width="stretch")
    st.subheader("Intentions")
    st.dataframe(pd.DataFrame(intentions), width="stretch")
else:
    st.info("Enter a scenario id to inspect goal and intention state.")
