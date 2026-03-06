import pandas as pd
import streamlit as st

from app.dashboard.components.api_client import fetch_json
from app.dashboard.components.filters import social_filters

st.title("Timeline")
filters = social_filters(prefix="timeline")
scenario_id = filters["scenario_id"]

if scenario_id:
    params = {
        "tick_from": filters["tick_from"],
        "tick_to": filters["tick_to"],
        "agent_id": filters["agent_id"],
        "event_type": filters["event_type"],
    }
    params = {k: v for k, v in params.items() if v is not None}

    events = fetch_json(f"/scenarios/{scenario_id}/timeline", params=params)
    st.subheader("Event Timeline")
    st.dataframe(pd.DataFrame(events), width="stretch")

    msg_params = {
        "agent_id": filters["agent_id"],
        "tick_from": filters["tick_from"],
        "tick_to": filters["tick_to"],
    }
    msg_params = {k: v for k, v in msg_params.items() if v is not None}
    messages = fetch_json(f"/scenarios/{scenario_id}/messages", params=msg_params if msg_params else None)
    st.subheader("Communication Feed")
    st.dataframe(pd.DataFrame(messages), width="stretch")
else:
    st.info("Enter a scenario id to load timeline and communication feed.")
