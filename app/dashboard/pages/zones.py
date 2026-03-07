import pandas as pd
import streamlit as st

from app.dashboard.components.api_client import fetch_json

st.title("Zones")
scenario_id = st.text_input("Scenario ID")

if scenario_id:
    rows = fetch_json(f"/scenarios/{scenario_id}/zones")
    st.subheader("Zone Occupancy")
    st.dataframe(pd.DataFrame(rows), width="stretch")
else:
    st.info("Enter a scenario id to inspect zone occupancy.")
