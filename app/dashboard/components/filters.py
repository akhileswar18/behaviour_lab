from __future__ import annotations

from typing import Any

import streamlit as st


def social_filters(prefix: str = "social") -> dict[str, Any]:
    scenario_id = st.text_input("Scenario ID", key=f"{prefix}_scenario_id")
    agent_id = st.text_input("Agent ID (optional)", key=f"{prefix}_agent_id")
    tick_from = st.number_input("Tick from", min_value=0, value=0, step=1, key=f"{prefix}_tick_from")
    tick_to = st.number_input("Tick to", min_value=0, value=0, step=1, key=f"{prefix}_tick_to")
    event_type = st.selectbox(
        "Event Type",
        options=["", "world_event", "decision", "message", "relationship_update", "memory_write"],
        key=f"{prefix}_event_type",
    )
    return {
        "scenario_id": scenario_id.strip(),
        "agent_id": agent_id.strip() or None,
        "tick_from": int(tick_from) if tick_from > 0 else None,
        "tick_to": int(tick_to) if tick_to > 0 else None,
        "event_type": event_type or None,
    }
