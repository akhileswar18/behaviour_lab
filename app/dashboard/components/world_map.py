from __future__ import annotations

import streamlit as st

from app.dashboard.components.zone_graph_renderer import render_world_graph


def render_zone_map(snapshot_or_zones: dict | list[dict]) -> None:
    if isinstance(snapshot_or_zones, dict):
        snapshot = snapshot_or_zones
    else:
        snapshot = {
            "current_tick": 0,
            "zone_occupancy": snapshot_or_zones,
            "resource_distribution": [],
            "global_event_feed": [],
        }
    if not snapshot.get("zone_occupancy"):
        st.info("No zone data available.")
        return
    render_world_graph(snapshot)
