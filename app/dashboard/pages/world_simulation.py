import pandas as pd
import streamlit as st

from app.dashboard.components.api_client import fetch_json
from app.dashboard.components.charts import render_world_metric_tiles, render_zone_resource_chart
from app.dashboard.components.filters import observatory_filters
from app.dashboard.components.world_map import render_zone_map

st.title("World Simulation Dashboard")
filters = observatory_filters(prefix="world_simulation")
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
    snapshot = fetch_json(f"/scenarios/{scenario_id}/analytics/world", params=params)

    st.subheader(f"Current Tick: {snapshot['current_tick']}")
    render_world_metric_tiles(snapshot["metrics"], snapshot["world_state"])

    top_left, top_right = st.columns(2)
    with top_left:
        st.markdown("**Global Event Feed**")
        st.dataframe(pd.DataFrame(snapshot["global_event_feed"]), width="stretch", hide_index=True)
    with top_right:
        st.markdown("**Zone Map**")
        render_zone_map(snapshot["zone_occupancy"])

    bottom_left, bottom_right = st.columns(2)
    with bottom_left:
        st.markdown("**Zone Occupancy**")
        st.dataframe(pd.DataFrame(snapshot["zone_occupancy"]), width="stretch", hide_index=True)
    with bottom_right:
        st.markdown("**Resource Distribution**")
        render_zone_resource_chart(snapshot["resource_distribution"])
        st.dataframe(pd.DataFrame(snapshot["resource_distribution"]), width="stretch", hide_index=True)
else:
    st.info("Enter a scenario id to inspect the full world state.")
