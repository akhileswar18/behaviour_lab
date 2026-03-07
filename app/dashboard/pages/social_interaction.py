import pandas as pd
import streamlit as st

from app.dashboard.components.api_client import fetch_json
from app.dashboard.components.charts import render_agent_metric_chart, render_cooperation_conflict_chart
from app.dashboard.components.filters import observatory_filters
from app.dashboard.components.graphs import render_relationship_graph

st.title("Social Interaction Dashboard")
filters = observatory_filters(prefix="social_interaction")
scenario_id = filters["scenario_id"]

if scenario_id:
    params = {
        "tick_from": filters["tick_from"],
        "tick_to": filters["tick_to"],
        "agent_id": filters["agent_id"],
        "zone_id": filters["zone_id"],
        "event_type": filters["event_type"],
    }
    params = {key: value for key, value in params.items() if value is not None}
    snapshot = fetch_json(f"/scenarios/{scenario_id}/analytics/social", params=params)

    top_left, top_right = st.columns([2, 1])
    with top_left:
        st.markdown("**Communication Feed**")
        st.dataframe(pd.DataFrame(snapshot["communication_feed"]), width="stretch", hide_index=True)
    with top_right:
        st.markdown("**Cooperation vs Conflict**")
        render_cooperation_conflict_chart(snapshot["cooperation_conflict_summary"])

    st.markdown("**Relationship Network**")
    render_relationship_graph(snapshot["relationship_graph"])

    lower_left, lower_right = st.columns(2)
    with lower_left:
        st.markdown("**Per-Agent Interaction Metrics**")
        render_agent_metric_chart(snapshot["interaction_metrics"])
        st.dataframe(pd.DataFrame(snapshot["interaction_metrics"]), width="stretch", hide_index=True)
    with lower_right:
        st.markdown("**Relationship Change History**")
        st.dataframe(pd.DataFrame(snapshot["relationship_history"]), width="stretch", hide_index=True)

    st.markdown("**Causal Chain Inspector**")
    st.dataframe(pd.DataFrame(snapshot["causal_chains"]), width="stretch", hide_index=True)
else:
    st.info("Enter a scenario id to inspect social dynamics.")
