# Phase 3 Demo Guide

## Goal

Show that agents are no longer only socially reactive. They now carry needs, goals, intentions,
location, and resource-aware behavior that can be inspected after every tick.

## Demo sequence

1. Seed the scenario:
   - `python -m app.persistence.init_db`
   - `python -m app.persistence.seed --scenario sample_goal_resource_lab`
2. Start API:
   - `uvicorn app.api.main:app --reload --port 8000`
3. Start dashboard:
   - `streamlit run app/dashboard/main.py --server.port 8501`
4. Run 8-10 ticks.
5. Inspect pages in this order:
   - `Agents`
   - `Goals`
   - `Zones`
   - `Resources`
   - `Timeline`
   - `Comparison`

## What a successful demo looks like

- at least one agent changes zone
- at least one food/resource event is persisted
- at least one plan change is visible in timeline
- at least one need threshold or interruption appears
- comparison rerun shows non-zero deltas for at least one planning/world override

## Troubleshooting

- No movement:
  - check that zones are seeded and the scenario uses `sample_goal_resource_lab`
- No resource events:
  - verify resource quantities exist before running ticks
- No interruptions:
  - run at least 4-6 ticks so the urgent shelter event is consumed
- Flat comparison output:
  - use a stronger override such as `{"Ben":{"hunger":0.95}}` and `{"Storage":{"food":0}}`
- Dashboard looks empty:
  - confirm the API is running on `http://127.0.0.1:8000`

## Scope limits

This phase does not include LLM planning, vector memory, websockets, auth, cloud execution,
pygame embodiment, or a full movement/physics engine.
