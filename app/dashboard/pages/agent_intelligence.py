from __future__ import annotations

import pandas as pd
import requests
import streamlit as st

from app.dashboard.components.api_client import fetch_json
from app.dashboard.components.charts import (
    render_action_count_over_time,
    render_action_mix_chart,
    render_behavioral_trends,
    render_decision_driver_chart,
    render_decision_trend_chart,
    render_goal_completion_over_time,
    render_goal_intention_history,
    render_interaction_metrics,
    render_memory_influence_trend_chart,
    render_need_gauges,
    render_needs_trend_chart,
    render_relationship_strength_chart,
    render_social_kpis,
)
from app.dashboard.components.filters import agent_intelligence_filters
from app.dashboard.components.graphs import render_ego_network


def _zones_by_scenario(identities: list[dict]) -> dict[str, list[dict]]:
    zone_map: dict[str, list[dict]] = {}
    scenario_ids = set()
    for identity in identities:
        for option in identity.get("available_scenarios", []):
            scenario_ids.add(option["scenario_id"])
    for scenario_id in sorted(scenario_ids, key=lambda value: str(value)):
        try:
            zone_rows = fetch_json(f"/scenarios/{scenario_id}/zones")
            zone_map[str(scenario_id)] = [
                {"id": row["id"], "name": row["name"]} for row in zone_rows
            ]
        except requests.RequestException:
            zone_map[str(scenario_id)] = []
    return zone_map


def _render_memory_cards(memory_summary: list[dict]) -> None:
    if not memory_summary:
        st.info("No influential memories found for this slice.")
        return
    columns = st.columns(3)
    for index, row in enumerate(memory_summary[:6]):
        column = columns[index % 3]
        with column:
            with st.container(border=True):
                st.caption(f"Tick {row['tick_number']} | {row['memory_type']}")
                st.write(row["content"][:160])
                st.caption(
                    f"Relevance {float(row['relevance_score']):.2f} | Salience {float(row['salience']):.2f}"
                )


def _render_active_card(title: str, payload: dict | None, empty_text: str) -> None:
    st.markdown(f"**{title}**")
    if not payload:
        st.info(empty_text)
        return
    with st.container(border=True):
        for key, value in payload.items():
            if key in {"id", "target_zone_id", "target_resource_id"}:
                continue
            st.write(f"**{key.replace('_', ' ').title()}**: {value}")


st.title("Agent Intelligence Dashboard")
st.caption("Agent-first reasoning cockpit derived from persisted simulation records.")

try:
    identity_rows = fetch_json("/analytics/agents")
except requests.RequestException as exc:
    st.error(f"Unable to load agent identities: {exc}")
    st.stop()

if not identity_rows:
    st.warning("No persisted agent identities available yet.")
    st.stop()

zone_lookup = _zones_by_scenario(identity_rows)
filters = agent_intelligence_filters(
    identity_options=identity_rows,
    zone_options_by_scenario=zone_lookup,
    prefix="agent_intelligence",
)

params = {
    "identity_key": filters["identity_key"],
    "scenario_id": filters["scenario_id"],
    "tick_from": filters["tick_from"],
    "tick_to": filters["tick_to"],
    "zone_id": filters["zone_id"],
    "event_type": filters["event_type"],
    "decision_source": filters.get("decision_source"),
}
params = {key: value for key, value in params.items() if value is not None}

try:
    snapshot = fetch_json("/analytics/agent-observatory", params=params)
except requests.RequestException as exc:
    st.error(f"Unable to load agent observatory data: {exc}")
    st.stop()

agent = snapshot["agent"]
scope_text = snapshot["scope_label"]
if snapshot.get("mode") == "overview":
    st.success(f"Overview Mode | {scope_text}")
else:
    st.success(f"Scenario Mode | {scope_text}")
if snapshot.get("scope_notes"):
    st.caption(snapshot["scope_notes"])

# A. Identity + Status Strip
st.markdown("## A. Identity + Status Strip")
id_cols = st.columns(6)
id_cols[0].metric("Agent", agent["name"])
id_cols[1].metric("Persona", agent["persona_label"])
id_cols[2].metric("Zone", agent.get("zone_name") or "unknown")
id_cols[3].metric("Mood", agent.get("mood", "neutral"))
id_cols[4].metric("Goal", (snapshot.get("active_goal") or {}).get("goal_type", "none"))
id_cols[5].metric(
    "Intention",
    (snapshot.get("active_intention") or {}).get("current_action_type", "none"),
)
badge_cols = st.columns(4)
badge_cols[0].caption(f"Style: {agent.get('communication_style', 'neutral')}")
badge_cols[1].caption(f"Risk tolerance: {float(agent.get('risk_tolerance', 0.0)):.2f}")
badge_cols[2].caption(f"Cooperation: {float(agent.get('cooperation_tendency', 0.0)):.2f}")
badge_cols[3].caption(f"Memory sensitivity: {float(agent.get('memory_sensitivity', 0.0)):.2f}")

# B. Internal State
st.markdown("## B. Internal State")
render_need_gauges(snapshot.get("needs", []))
render_needs_trend_chart(snapshot.get("needs_history", []))

# C. Goals & Intentions
st.markdown("## C. Goals & Intentions")
goal_col, intention_col = st.columns(2)
with goal_col:
    _render_active_card("Active Goal", snapshot.get("active_goal"), "No active goal.")
with intention_col:
    _render_active_card(
        "Active Intention",
        snapshot.get("active_intention"),
        "No active intention.",
    )
st.markdown("**Plan / Intention History**")
render_goal_intention_history(snapshot.get("plan_history", []))
with st.expander("Goal & Intention Detail", expanded=False):
    left, right = st.columns(2)
    left.dataframe(pd.DataFrame(snapshot.get("recent_goals", [])), width="stretch", hide_index=True)
    right.dataframe(
        pd.DataFrame(snapshot.get("recent_intentions", [])), width="stretch", hide_index=True
    )

# D. Decision Dynamics
st.markdown("## D. Decision Dynamics")
d_left, d_right = st.columns(2)
with d_left:
    st.markdown("**Decision Drivers**")
    render_decision_driver_chart(snapshot.get("decisions", []))
with d_right:
    st.markdown("**Action Mix**")
    render_action_mix_chart(snapshot.get("action_mix", []))
st.markdown("**Decision Trend Over Time**")
render_decision_trend_chart(snapshot.get("decisions", []))
source_counts = {}
for row in snapshot.get("decisions", []):
    source = row.get("decision_source", "deterministic")
    source_counts[source] = source_counts.get(source, 0) + 1
if source_counts:
    st.caption(
        "Decision sources: "
        + ", ".join(f"{source}={count}" for source, count in sorted(source_counts.items()))
    )
with st.expander("Decision Trace Detail", expanded=False):
    st.dataframe(pd.DataFrame(snapshot.get("decisions", [])), width="stretch", hide_index=True)

# E. Memory Influence
st.markdown("## E. Memory Influence")
st.markdown("**Top Influencing Memories**")
_render_memory_cards(snapshot.get("memory_summary", []))
st.markdown("**Influence Over Time**")
render_memory_influence_trend_chart(snapshot.get("memory_influence_trend", []))
with st.expander("Memory Influence Detail", expanded=False):
    st.dataframe(
        pd.DataFrame(snapshot.get("memory_influences", [])), width="stretch", hide_index=True
    )

# F. Social Position
st.markdown("## F. Social Position")
render_social_kpis(snapshot.get("interaction_metrics", {}))
metric_row = snapshot.get("interaction_metrics", {})
source_cols = st.columns(3)
source_cols[0].metric("LLM Decisions", int(metric_row.get("llm_decision_count", 0)))
source_cols[1].metric(
    "Deterministic Decisions",
    int(metric_row.get("deterministic_decision_count", 0)),
)
source_cols[2].metric("Fallback Count", int(metric_row.get("fallback_count", 0)))
social_left, social_right = st.columns(2)
with social_left:
    st.markdown("**Relationship Summary**")
    render_relationship_strength_chart(snapshot.get("relationships", []))
with social_right:
    st.markdown("**Ego Network**")
    render_ego_network(agent_name=agent["name"], relationships=snapshot.get("relationships", []))
with st.expander("Social Detail", expanded=False):
    render_interaction_metrics(snapshot.get("interaction_metrics", {}))
    st.dataframe(pd.DataFrame(snapshot.get("relationships", [])), width="stretch", hide_index=True)

# G. Behavioral Trends
st.markdown("## G. Behavioral Trends")
render_behavioral_trends(snapshot.get("behavioral_trends", []))
trend_left, trend_right = st.columns(2)
with trend_left:
    st.markdown("**Action Counts Over Time**")
    render_action_count_over_time(snapshot.get("behavioral_trends", []))
with trend_right:
    st.markdown("**Goal Completion Over Time**")
    render_goal_completion_over_time(snapshot.get("behavioral_trends", []))
if snapshot.get("behavioral_trends"):
    latest = snapshot["behavioral_trends"][-1]
    st.caption(
        "Trend signal: "
        f"interruptions={latest.get('interruption_count', 0)}, "
        f"distinct_actions={latest.get('distinct_action_count', 0)}, "
        f"zone_transitions={latest.get('zone_transition_count', 0)}"
    )
else:
    st.info("No behavioral trend records available.")

with st.expander("Recent Event Detail", expanded=False):
    st.dataframe(pd.DataFrame(snapshot.get("recent_events", [])), width="stretch", hide_index=True)
