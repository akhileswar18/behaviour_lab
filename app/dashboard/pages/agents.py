import pandas as pd
import streamlit as st
from sqlmodel import Session, select
from uuid import UUID

from app.dashboard.components.api_client import fetch_json
from app.persistence.engine import get_engine
from app.persistence.models import DecisionLog, Memory, MemoryRetrievalTrace

st.title("Agents")
scenario_id = st.text_input("Scenario ID")
if scenario_id:
    agents = fetch_json(f"/scenarios/{scenario_id}/agents")
    st.subheader("Agent Overview")
    st.dataframe(pd.DataFrame(agents), width="stretch")

    if agents:
        selected = st.selectbox("Agent", options=[a["id"] for a in agents])
        messages = fetch_json(
            f"/scenarios/{scenario_id}/messages",
            params={"agent_id": selected},
        )
        relationships = fetch_json(f"/scenarios/{scenario_id}/relationships")
        st.subheader("Agent Messages")
        st.dataframe(pd.DataFrame(messages), width="stretch")

        with Session(get_engine()) as session:
            selected_uuid = UUID(selected)
            decisions = list(
                session.exec(
                    select(DecisionLog)
                    .where(DecisionLog.agent_id == selected_uuid)
                    .order_by(DecisionLog.created_at.desc())
                )
            )
            decision_df = pd.DataFrame(
                [
                    {
                        "tick": d.tick_number,
                        "action": d.selected_action,
                        "rationale": d.rationale,
                        "persona_factors": d.persona_factors,
                        "relationship_factors": d.relationship_factors,
                        "world_event_factors": d.world_event_factors,
                    }
                    for d in decisions[:10]
                ]
            )
            st.subheader("Recent Decisions")
            st.dataframe(decision_df, width="stretch")

            memories = list(
                session.exec(select(Memory).where(Memory.agent_id == selected_uuid).order_by(Memory.created_at.desc()))
            )
            memory_df = pd.DataFrame(
                [
                    {
                        "memory_id": str(m.id),
                        "type": m.memory_type,
                        "content": m.content,
                        "salience": m.salience,
                        "created_at": m.created_at,
                    }
                    for m in memories[:15]
                ]
            )
            st.subheader("Recent Memories")
            st.dataframe(memory_df, width="stretch")

            recalls = list(
                session.exec(
                    select(MemoryRetrievalTrace)
                    .where(MemoryRetrievalTrace.agent_id == selected_uuid)
                    .order_by(MemoryRetrievalTrace.created_at.desc())
                )
            )
            recall_df = pd.DataFrame(
                [
                    {
                        "tick": r.tick_number,
                        "memory_id": str(r.memory_id),
                        "decision_log_id": str(r.decision_log_id),
                        "relevance_score": r.relevance_score,
                        "created_at": r.created_at,
                    }
                    for r in recalls[:15]
                ]
            )
            st.subheader("Recalled Memories")
            st.dataframe(recall_df, width="stretch")

        rel_df = pd.DataFrame(
            [
                r
                for r in relationships
                if r["source_agent_id"] == selected or r["target_agent_id"] == selected
            ]
        )
        st.subheader("Agent Relationships")
        st.dataframe(rel_df, width="stretch")
else:
    st.info("Enter a scenario id to load agents.")
