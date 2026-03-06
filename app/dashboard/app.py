from __future__ import annotations

import sys
import types
from pathlib import Path

import streamlit as st

# This file exists only as a compatibility entrypoint for:
#   streamlit run app/dashboard/app.py
# It bootstraps package paths explicitly to avoid recursive import collisions.
THIS_FILE = Path(__file__).resolve()
DASHBOARD_DIR = THIS_FILE.parent
APP_DIR = DASHBOARD_DIR.parent
REPO_ROOT = APP_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# Ensure imports like `app.dashboard...` and `app.persistence...` resolve to package dirs.
app_pkg = types.ModuleType("app")
app_pkg.__path__ = [str(APP_DIR)]
sys.modules["app"] = app_pkg

dashboard_pkg = types.ModuleType("app.dashboard")
dashboard_pkg.__path__ = [str(DASHBOARD_DIR)]
sys.modules["app.dashboard"] = dashboard_pkg

st.set_page_config(page_title="Behavior Lab Dashboard", layout="wide")
st.title("Behavior Lab Dashboard")
st.write(
    "Local-first observability surface for agents, communication, timeline, memory, and relationships."
)
st.info("Use sidebar pages to inspect scenario data once simulation services are running.")
st.caption(
    "Recommended inspection order: Agents -> Communication -> Relationships -> Timeline -> Memories."
)
