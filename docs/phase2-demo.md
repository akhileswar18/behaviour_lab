# Phase 2 Demo Guide

## Goal

Demonstrate a complete local social-simulation loop:

- world event influences agent decisions
- decisions create messages
- messages update relationships
- effects remain visible in memories, timeline, and comparison runs

## Demo Run Order

1. Seed the scenario:

```powershell
python -m app.persistence.init_db
python -m app.persistence.seed --scenario sample_social_tension
```

2. Start services:

```powershell
uvicorn app.api.main:app --reload --port 8000
streamlit run app/dashboard/main.py --server.port 8501
```

3. Fetch the scenario id:

```powershell
curl http://127.0.0.1:8000/scenarios
```

4. Run the scenario:

```powershell
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/run -H "Content-Type: application/json" -d '{"ticks":10}'
```

5. Inspect in dashboard:

- `Agents`
- `Communication`
- `Relationships`
- `Timeline`
- `Memories`

6. Run a comparison variant:

```powershell
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/compare-rerun -H "Content-Type: application/json" -d "{\"ticks\":3,\"variant_name\":\"risk-heavy-ava\",\"persona_overrides\":{\"Ava\":{\"risk_tolerance\":0.95,\"cooperation_tendency\":0.2}}}"
```

## What To Verify

- At least one `world_event` appears in the timeline.
- Agents choose different social actions under the same scenario.
- Structured messages contain `intent` and `emotional_tone`.
- Relationship rows show trust or affinity changes after messages.
- Agent detail view shows decision rationale factors and recall traces.
- Comparison output returns `decision_count_delta`, `message_count_delta`, and `relationship_avg_trust_delta`.

## Troubleshooting

- If `/health` fails:
  - confirm API is running on `127.0.0.1:8000`
  - check the active virtual environment

- If dashboard loads but shows no data:
  - confirm the scenario was seeded successfully
  - fetch `/scenarios` and use the correct scenario id
  - run ticks before checking timeline-dependent pages

- If relationships do not change:
  - verify `message` and `relationship_update` events exist in the timeline
  - confirm ticks were executed after seeding

- If comparison output looks identical:
  - increase the persona override difference
  - use `risk_tolerance` and `cooperation_tendency` together for clearer divergence
  - run at least `3` ticks

- If Streamlit page imports fail:
  - start with `streamlit run app/dashboard/main.py --server.port 8501`
  - if using the compatibility entrypoint, fully stop and restart Streamlit

## Smoke Validation

Run:

```powershell
pytest tests/smoke/test_phase2_social_flow.py -q
```

Expected result:

- the smoke test passes
- messages, world events, decisions, and relationship updates are all present
