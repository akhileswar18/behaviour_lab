from __future__ import annotations

from typing import Any

import streamlit as st


EVENT_TYPES = [
    "",
    "world_event",
    "decision",
    "message",
    "relationship_update",
    "memory_write",
    "plan_change",
    "interruption",
    "move",
    "acquire",
    "consume",
    "resource_shortage",
    "need_threshold",
]

DECISION_SOURCES = [
    "",
    "deterministic",
    "llm",
    "fallback_deterministic",
]


def agent_intelligence_filters(
    *,
    identity_options: list[dict[str, Any]],
    zone_options_by_scenario: dict[str, list[dict[str, Any]]],
    prefix: str = "agent_intelligence",
) -> dict[str, Any]:
    if not identity_options:
        return {
            "identity_key": None,
            "scenario_id": None,
            "zone_id": None,
            "tick_from": None,
            "tick_to": None,
            "event_type": None,
            "decision_source": None,
        }

    identity_labels = [f"{row['name']} ({row['persona_label']})" for row in identity_options]
    identity_by_label = {label: row for label, row in zip(identity_labels, identity_options, strict=False)}
    default_label = identity_labels[0]
    selected_label = st.selectbox("Agent", options=identity_labels, index=0, key=f"{prefix}_identity")
    selected_identity = identity_by_label.get(selected_label, identity_by_label[default_label])

    scenario_options = selected_identity.get("available_scenarios", [])
    scenario_label_rows = [{"label": "All scenarios", "scenario_id": None}]
    scenario_label_rows.extend(
        {
            "label": row.get("scenario_name", str(row.get("scenario_id"))),
            "scenario_id": row.get("scenario_id"),
        }
        for row in scenario_options
    )
    scenario_labels = [row["label"] for row in scenario_label_rows]
    selected_scenario_label = st.selectbox(
        "Scenario (optional)",
        options=scenario_labels,
        index=0,
        key=f"{prefix}_scenario",
    )
    selected_scenario = next(
        (row for row in scenario_label_rows if row["label"] == selected_scenario_label),
        scenario_label_rows[0],
    )
    fallback_scenario_id = selected_identity.get("latest_scenario_id")
    scoped_scenario_id = selected_scenario["scenario_id"] or fallback_scenario_id
    zone_options = zone_options_by_scenario.get(str(scoped_scenario_id), [])

    with st.expander("Advanced Filters", expanded=False):
        tick_left, tick_right = st.columns(2)
        tick_from = tick_left.number_input(
            "Tick from",
            min_value=0,
            value=0,
            step=1,
            key=f"{prefix}_tick_from",
        )
        tick_to = tick_right.number_input(
            "Tick to",
            min_value=0,
            value=0,
            step=1,
            key=f"{prefix}_tick_to",
        )
        zone_labels = ["All zones"] + [row["name"] for row in zone_options]
        selected_zone_label = st.selectbox("Zone", options=zone_labels, key=f"{prefix}_zone")
        zone_row = next((row for row in zone_options if row["name"] == selected_zone_label), None)
        event_type = st.selectbox("Event Type", options=EVENT_TYPES, key=f"{prefix}_event_type")
        decision_source = st.selectbox(
            "Decision Source",
            options=DECISION_SOURCES,
            key=f"{prefix}_decision_source",
        )

    return {
        "identity_key": selected_identity["identity_key"],
        "scenario_id": selected_scenario["scenario_id"],
        "zone_id": zone_row["id"] if zone_row else None,
        "tick_from": int(tick_from) if tick_from > 0 else None,
        "tick_to": int(tick_to) if tick_to > 0 else None,
        "event_type": event_type or None,
        "decision_source": decision_source or None,
    }


def observatory_filters(prefix: str = "observatory") -> dict[str, Any]:
    scenario_id = st.text_input("Scenario ID", key=f"{prefix}_scenario_id")
    agent_id = st.text_input("Agent ID (optional)", key=f"{prefix}_agent_id")
    zone_id = st.text_input("Zone ID (optional)", key=f"{prefix}_zone_id")
    left, right = st.columns(2)
    tick_from = left.number_input("Tick from", min_value=0, value=0, step=1, key=f"{prefix}_tick_from")
    tick_to = right.number_input("Tick to", min_value=0, value=0, step=1, key=f"{prefix}_tick_to")
    event_type = st.selectbox("Event Type", options=EVENT_TYPES, key=f"{prefix}_event_type")
    return {
        "scenario_id": scenario_id.strip(),
        "agent_id": agent_id.strip() or None,
        "zone_id": zone_id.strip() or None,
        "tick_from": int(tick_from) if tick_from > 0 else None,
        "tick_to": int(tick_to) if tick_to > 0 else None,
        "event_type": event_type or None,
    }


def social_filters(prefix: str = "social") -> dict[str, Any]:
    return observatory_filters(prefix=prefix)
