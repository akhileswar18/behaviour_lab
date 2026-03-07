from __future__ import annotations

import pandas as pd
import streamlit as st


def _frame_or_none(rows: list[dict]) -> pd.DataFrame | None:
    if not rows:
        return None
    frame = pd.DataFrame(rows)
    if frame.empty:
        return None
    return frame


def render_need_gauges(needs: list[dict]) -> None:
    columns = st.columns(max(len(needs), 1))
    for column, need in zip(columns, needs, strict=False):
        value = float(need.get("value", 0.0))
        column.metric(need.get("label", "Need"), f"{value:.0%}", need.get("severity", "stable"))
        column.progress(min(max(value, 0.0), 1.0))


def render_needs_trend_chart(history: list[dict], threshold: float = 0.7) -> None:
    frame = _frame_or_none(history)
    if frame is None:
        st.info("No need history available for this slice.")
        return
    chart_frame = frame.set_index("tick_number")[["hunger", "safety_need", "social_need"]]
    st.line_chart(chart_frame, height=240)
    st.caption(f"Threshold marker: {threshold:.0%} (elevated pressure).")


def render_interaction_metrics(metrics: dict) -> None:
    columns = st.columns(3)
    columns[0].metric("Messages Sent", int(metrics.get("messages_sent", 0)))
    columns[1].metric("Messages Received", int(metrics.get("messages_received", 0)))
    columns[2].metric("Goal Completion", f"{float(metrics.get('goal_completion_rate', 0.0)):.0%}")

    columns = st.columns(3)
    columns[0].metric("Cooperation", int(metrics.get("cooperation_events", 0)))
    columns[1].metric("Conflict", int(metrics.get("conflict_events", 0)))
    columns[2].metric("Interruptions", int(metrics.get("interruption_count", 0)))


def render_social_kpis(metrics: dict) -> None:
    left = st.columns(6)
    left[0].metric("Sent", int(metrics.get("messages_sent", 0)))
    left[1].metric("Received", int(metrics.get("messages_received", 0)))
    left[2].metric("Cooperation", int(metrics.get("cooperation_events", 0)))
    left[3].metric("Conflict", int(metrics.get("conflict_events", 0)))
    left[4].metric("Interruptions", int(metrics.get("interruption_count", 0)))
    left[5].metric("Goal Completion", f"{float(metrics.get('goal_completion_rate', 0.0)):.0%}")


def render_decision_driver_chart(decisions: list[dict]) -> None:
    if not decisions:
        st.info("No decision traces available for the selected slice.")
        return
    rows = []
    for decision in decisions[:20]:
        rows.append(
            {
                "tick": decision["tick_number"],
                "confidence": float(decision.get("confidence", 0.0)),
                "world_events": float(
                    decision.get("world_event_factors", {}).get("world_event_count", 0.0)
                ),
                "local_resources": float(
                    decision.get("world_event_factors", {}).get("local_resource_count", 0.0)
                ),
                "risk_tolerance": float(
                    decision.get("persona_factors", {}).get("risk_tolerance", 0.0)
                ),
                "cooperation_tendency": float(
                    decision.get("persona_factors", {}).get("cooperation_tendency", 0.0)
                ),
            }
        )
    frame = pd.DataFrame(rows).set_index("tick")
    st.bar_chart(frame, height=260)


def render_action_mix_chart(action_mix: list[dict]) -> None:
    frame = _frame_or_none(action_mix)
    if frame is None:
        st.info("No action mix data available.")
        return
    st.bar_chart(frame.set_index("action")[["count"]], height=220)


def render_decision_trend_chart(decisions: list[dict]) -> None:
    if not decisions:
        st.info("No decision trends available.")
        return
    frame = pd.DataFrame(decisions)
    grouped = (
        frame.groupby("tick_number")
        .agg(decision_count=("id", "count"), avg_confidence=("confidence", "mean"))
        .reset_index()
        .set_index("tick_number")
    )
    st.line_chart(grouped, height=220)


def render_memory_influence_trend_chart(rows: list[dict]) -> None:
    frame = _frame_or_none(rows)
    if frame is None:
        st.info("No memory influence trend available.")
        return
    st.line_chart(frame.set_index("tick_number")[["avg_relevance", "count"]], height=220)


def render_relationship_strength_chart(relationships: list[dict]) -> None:
    if not relationships:
        st.info("No relationship context available yet.")
        return
    frame = pd.DataFrame(
        [
            {
                "agent": row["target_agent_name"],
                "trust": row["trust"],
                "affinity": row["affinity"],
                "influence": row.get("influence", 0.0),
            }
            for row in relationships
        ]
    ).set_index("agent")
    st.bar_chart(frame, height=240)


def render_goal_intention_history(plan_history: list[dict]) -> None:
    frame = _frame_or_none(plan_history)
    if frame is None:
        st.info("No plan history for this range.")
        return
    chart_data = (
        frame.groupby(["tick_number", "event_type"])
        .size()
        .reset_index(name="count")
        .pivot(index="tick_number", columns="event_type", values="count")
        .fillna(0)
    )
    st.bar_chart(chart_data, height=200)


def render_behavioral_trends(rows: list[dict]) -> None:
    frame = _frame_or_none(rows)
    if frame is None:
        st.info("No behavioral trend data available.")
        return
    chart = frame.set_index("tick_number")[
        [
            "action_count",
            "interruption_count",
            "goal_completion_count",
            "zone_transition_count",
        ]
    ]
    st.line_chart(chart, height=240)


def render_action_count_over_time(rows: list[dict]) -> None:
    frame = _frame_or_none(rows)
    if frame is None:
        st.info("No action-count trend available.")
        return
    st.line_chart(frame.set_index("tick_number")[["action_count", "move_count"]], height=220)


def render_goal_completion_over_time(rows: list[dict]) -> None:
    frame = _frame_or_none(rows)
    if frame is None:
        st.info("No goal completion trend available.")
        return
    st.line_chart(frame.set_index("tick_number")[["goal_completion_count"]], height=220)


def render_cooperation_conflict_chart(summary: dict) -> None:
    frame = pd.DataFrame(
        [
            {"metric": "Cooperation", "count": int(summary.get("cooperation_events", 0))},
            {"metric": "Conflict", "count": int(summary.get("conflict_events", 0))},
            {"metric": "Relationship Updates", "count": int(summary.get("relationship_updates", 0))},
        ]
    ).set_index("metric")
    st.bar_chart(frame, height=220)


def render_agent_metric_chart(rows: list[dict]) -> None:
    if not rows:
        st.info("No interaction metric data available.")
        return
    frame = pd.DataFrame(rows).set_index("agent_name")[
        ["messages_sent", "messages_received", "cooperation_events", "conflict_events"]
    ]
    st.bar_chart(frame, height=280)


def render_world_metric_tiles(metrics: dict, world_state: dict) -> None:
    columns = st.columns(4)
    columns[0].metric("Avg Trust", f"{float(metrics.get('average_trust', 0.0)):.2f}")
    columns[1].metric("Goal Completion", f"{float(metrics.get('goal_completion_rate', 0.0)):.0%}")
    columns[2].metric("Movement / Tick", f"{float(metrics.get('movement_frequency', 0.0)):.2f}")
    columns[3].metric("Scarcity", f"{float(metrics.get('resource_scarcity', 0.0)):.0%}")

    columns = st.columns(4)
    columns[0].metric("Zones", int(world_state.get("zone_count", 0)))
    columns[1].metric("Agents", int(world_state.get("agent_count", 0)))
    columns[2].metric("Resource Units", int(world_state.get("resource_unit_count", 0)))
    columns[3].metric("Tick Span", int(world_state.get("active_tick_span", 0)))


def render_zone_resource_chart(resources: list[dict]) -> None:
    if not resources:
        st.info("No resource distribution data available.")
        return
    frame = pd.DataFrame(resources)
    pivot = frame.pivot_table(
        index="zone_name",
        columns="resource_type",
        values="quantity",
        aggfunc="sum",
        fill_value=0,
    )
    st.bar_chart(pivot, height=260)
