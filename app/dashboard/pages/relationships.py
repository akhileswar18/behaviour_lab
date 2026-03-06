import streamlit as st
import pandas as pd

from app.dashboard.components.api_client import fetch_json
from app.dashboard.components.filters import social_filters

st.title("Relationships")
filters = social_filters(prefix="relationships")
scenario_id = filters["scenario_id"]
if scenario_id:
    params = {"agent_id": filters["agent_id"]} if filters["agent_id"] else None
    data = fetch_json(f"/scenarios/{scenario_id}/relationships", params=params)
    st.dataframe(pd.DataFrame(data), width="stretch")
else:
    st.info("Enter a scenario id to load relationship history.")
