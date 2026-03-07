from __future__ import annotations

import pandas as pd
import streamlit as st


def render_relationship_graph(relationships: list[dict]) -> None:
    if not relationships:
        st.info("No social graph data available.")
        return
    frame = pd.DataFrame(
        [
            {
                "edge": f"{row['source_agent_name']} -> {row['target_agent_name']}",
                "trust": row["trust"],
                "affinity": row["affinity"],
                "stance": row["stance"],
                "influence": row["influence"],
            }
            for row in relationships
        ]
    ).set_index("edge")
    st.bar_chart(frame[["trust", "affinity", "influence"]], height=260)
    st.dataframe(frame.reset_index(), width="stretch", hide_index=True)


def render_ego_network(agent_name: str, relationships: list[dict]) -> None:
    if not relationships:
        st.info("No relationship edges to render for this agent.")
        return
    rows = []
    for row in relationships:
        rows.append(
            {
                "connection": f"{agent_name} -> {row['target_agent_name']}",
                "trust": row["trust"],
                "affinity": row["affinity"],
                "influence": row.get("influence", 0.0),
                "stance": row.get("stance", "neutral"),
            }
        )
    frame = pd.DataFrame(rows).set_index("connection")
    st.bar_chart(frame[["trust", "affinity", "influence"]], height=220)
    st.dataframe(frame.reset_index(), width="stretch", hide_index=True)
