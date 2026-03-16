from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from app.dashboard.components.api_client import fetch_json
from app.dashboard.components.charts import render_world_metric_tiles, render_zone_resource_chart
from app.dashboard.components.filters import observatory_filters
from app.dashboard.components.world_map import render_zone_map


def _render_event_feed(events: list[dict], max_events: int = 20) -> None:
    if not events:
        st.info("No world events in the selected slice.")
        return

    lines: list[str] = []
    for event in sorted(
        events[:max_events],
        key=lambda row: (int(row.get("tick_number", 0)), row.get("created_at", "")),
        reverse=True,
    ):
        tick = int(event.get("tick_number", 0))
        content = str(event.get("content", event.get("event_type", "event")))
        event_type = str(event.get("event_type", "event")).replace("_", " ")
        payload = event.get("payload") or {}
        zone_name = (
            payload.get("zone_name")
            or payload.get("zone")
            or payload.get("location")
            or payload.get("resource_type")
            or ""
        )
        zone_suffix = f" <span style='color:#66737F;'>@ {escape(str(zone_name))}</span>" if zone_name else ""
        lines.append(
            "<div style='padding:6px 0;border-bottom:1px solid #E8EAED;'>"
            f"<span style='font-family:monospace;color:#5F6B76;'>T{tick:02d}</span> "
            f"<strong>{escape(content)}</strong> "
            f"<span style='color:#7A8793;'>[{escape(event_type)}]</span>"
            f"{zone_suffix}"
            "</div>"
        )

    st.markdown(
        (
            "<div style='max-height:260px;overflow-y:auto;padding:4px 10px;"
            "border:1px solid #E6E2D9;border-radius:12px;background:#FCFBF8;'>"
            + "".join(lines)
            + "</div>"
        ),
        unsafe_allow_html=True,
    )


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

    status_cols = st.columns(3)
    status_cols[0].metric("Current Tick", int(snapshot["current_tick"]))
    status_cols[1].metric("Visible Agents", int(snapshot["world_state"].get("agent_count", 0)))
    status_cols[2].metric("Visible Zones", int(snapshot["world_state"].get("zone_count", 0)))

    if hasattr(st, "page_link"):
        nav_left, nav_right = st.columns(2)
        with nav_left:
            st.page_link("pages/agent_intelligence.py", label="Open Agent Intelligence")
        with nav_right:
            st.page_link("pages/social_interaction.py", label="Open Social Interaction")

    render_world_metric_tiles(snapshot["metrics"], snapshot["world_state"])

    st.markdown("**World Transit Map**")
    render_zone_map(snapshot)

    st.markdown("**Recent Global Event Feed**")
    _render_event_feed(snapshot["global_event_feed"])

    with st.expander("Zone Occupancy Detail", expanded=False):
        st.markdown("**Zone Occupancy**")
        st.dataframe(pd.DataFrame(snapshot["zone_occupancy"]), width="stretch", hide_index=True)

    with st.expander("Resource Distribution Detail", expanded=False):
        st.markdown("**Resource Distribution**")
        render_zone_resource_chart(snapshot["resource_distribution"])
        st.dataframe(pd.DataFrame(snapshot["resource_distribution"]), width="stretch", hide_index=True)
else:
    st.info("Enter a scenario id to inspect the full world state.")
