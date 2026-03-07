import pandas as pd
import streamlit as st

from app.dashboard.components.api_client import fetch_json

st.title("Resources")
scenario_id = st.text_input("Scenario ID")
zone_id = st.text_input("Zone ID (optional)")

if scenario_id:
    params = {"zone_id": zone_id} if zone_id else None
    rows = fetch_json(f"/scenarios/{scenario_id}/resources", params=params)
    st.subheader("Resource Availability")
    st.dataframe(pd.DataFrame(rows), width="stretch")
else:
    st.info("Enter a scenario id to inspect resources.")
