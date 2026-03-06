import streamlit as st

st.set_page_config(page_title="Behavior Lab Dashboard", layout="wide")
st.title("Behavior Lab Dashboard")
st.write("Local-first observability surface for agents, communication, timeline, memory, and relationships.")
st.info("Use sidebar pages to inspect scenario data once simulation services are running.")
st.caption("Recommended inspection order: Agents -> Communication -> Relationships -> Timeline -> Memories.")
if hasattr(st, "page_link"):
    st.page_link("pages/communication.py", label="Open Communication Feed")
    st.page_link("pages/comparison.py", label="Open Variant Comparison")
