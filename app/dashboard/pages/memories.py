import pandas as pd
import streamlit as st
from sqlmodel import Session, select

from app.persistence.engine import get_engine
from app.persistence.models import Memory, MemoryRetrievalTrace

st.title("Memories")
agent_id = st.text_input("Agent ID (optional)")

with Session(get_engine()) as session:
    stmt = select(Memory).order_by(Memory.created_at.desc())
    rows = list(session.exec(stmt))
    if agent_id:
        rows = [r for r in rows if str(r.agent_id) == agent_id]

    memory_df = pd.DataFrame(
        [
            {
                "id": str(r.id),
                "agent_id": str(r.agent_id),
                "memory_type": r.memory_type,
                "content": r.content,
                "salience": r.salience,
                "created_at": r.created_at,
            }
            for r in rows
        ]
    )
    st.subheader("Memory Timeline")
    st.dataframe(memory_df, width="stretch")

    traces = list(session.exec(select(MemoryRetrievalTrace).order_by(MemoryRetrievalTrace.created_at.desc())))
    trace_df = pd.DataFrame(
        [
            {
                "agent_id": str(t.agent_id),
                "tick": t.tick_number,
                "decision_log_id": str(t.decision_log_id),
                "memory_id": str(t.memory_id),
                "relevance_score": t.relevance_score,
                "created_at": t.created_at,
            }
            for t in traces
        ]
    )
    st.subheader("Recall Traces")
    st.dataframe(trace_df, width="stretch")
