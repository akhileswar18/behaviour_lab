from __future__ import annotations

import streamlit as st


def render_zone_map(zones: list[dict]) -> None:
    if not zones:
        st.info("No zone data available.")
        return
    columns = st.columns(min(max(len(zones), 1), 3))
    for index, zone in enumerate(zones):
        column = columns[index % len(columns)]
        with column:
            with st.container(border=True):
                st.markdown(f"**{zone.get('zone_name', zone.get('name', 'zone'))}**")
                st.caption(zone.get("zone_type", "zone"))
                st.write(f"Occupants: {zone.get('occupant_count', len(zone.get('occupants', [])))}")
                occupant_names = [row.get("agent_name") for row in zone.get("occupants", [])]
                st.write(", ".join([name for name in occupant_names if name]) or "No agents")
                resources = zone.get("resource_types", [])
                st.write("Resources: " + (", ".join(resources) if resources else "none"))
