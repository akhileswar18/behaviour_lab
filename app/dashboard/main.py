import streamlit as st

st.set_page_config(page_title="Behavior Lab Dashboard", layout="wide")
st.title("Behavior Lab Observatory")
st.write("Local-first observability surface for agent cognition, social dynamics, and world evolution.")
st.info("Use the observability pages first; the legacy table pages remain available for drill-down.")
st.caption("Recommended inspection order: Agent Intelligence -> Social Interaction -> World Simulation -> legacy detail pages.")
if hasattr(st, "page_link"):
    st.page_link("pages/agent_intelligence.py", label="Open Agent Intelligence")
    st.page_link("pages/social_interaction.py", label="Open Social Interaction")
    st.page_link("pages/world_simulation.py", label="Open World Simulation")
    st.page_link("pages/agents.py", label="Open Agents")
    st.page_link("pages/goals.py", label="Open Goals & Intentions")
    st.page_link("pages/zones.py", label="Open Zones")
    st.page_link("pages/resources.py", label="Open Resources")
    st.page_link("pages/communication.py", label="Open Communication Feed")
    st.page_link("pages/comparison.py", label="Open Variant Comparison")
