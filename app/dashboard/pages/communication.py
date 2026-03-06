import pandas as pd
import streamlit as st

from app.dashboard.components.api_client import fetch_json
from app.dashboard.components.filters import social_filters

st.title("Communication")
filters = social_filters(prefix="communication")
scenario_id = filters["scenario_id"]

if scenario_id:
    params = {
        "agent_id": filters["agent_id"],
        "tick_from": filters["tick_from"],
        "tick_to": filters["tick_to"],
    }
    params = {key: value for key, value in params.items() if value is not None}
    rows = fetch_json(f"/scenarios/{scenario_id}/messages", params=params)

    st.subheader("Structured Message Feed")
    st.dataframe(pd.DataFrame(rows), width="stretch")
else:
    st.info("Enter a scenario id to load communication flow.")
