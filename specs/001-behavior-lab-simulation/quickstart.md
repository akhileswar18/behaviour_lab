# Quickstart: Multi-Agent Behavior Lab

## Prerequisites

- Python 3.11+
- `uv` installed (preferred). `pip` fallback supported.

## 1. Install dependencies

### Preferred (`uv`)

```bash
uv sync
```

### Fallback (`pip`)

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

## 2. Configure environment

Create `.env` from `.env.example` and set:

- `APP_ENV=local`
- `DATABASE_URL=sqlite:///./data/behavior_lab.db`
- `LOG_LEVEL=INFO`

## 3. Initialize database and seed sample scenario

```bash
python -m app.persistence.seed --scenario sample_social_tension
```

Expected outcome:
- One scenario created
- 3 seeded agents with distinct personas
- Initial relationship records
- Scheduled world events for social tension/opportunity
- Seeded structured message with intent/tone

## 4. Run API

```bash
uv run uvicorn app.api.main:app --reload --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## 5. Run dashboard

In a second terminal:

```bash
uv run streamlit run app/dashboard/main.py --server.port 8501
```

Open `http://127.0.0.1:8501`.

## 6. Execute simulation ticks

Run 10 ticks:

```bash
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/run \
  -H "Content-Type: application/json" \
  -d '{"ticks":10}'
```

## 7. Validate Phase Goals

- Agent roster visible with persona and current state.
- Communication feed shows structured messages (intent, tone, sender/receiver).
- Timeline displays `world_event`, `decision`, `message`, and `relationship_update` events by tick.
- Memory and decision history visible per agent with rationale factors.
- Relationship updates visible after interactions with trust/affinity and stance changes.

## 8. Social inspection flow (US1 + US2)

1. Open dashboard pages in this order:
   - `Agents` for persona and decision factors
   - `Communication` for message flow
   - `Relationships` for trust/affinity changes
   - `Timeline` for event causality chain
2. In Timeline filters, set:
   - `event_type=world_event` then `event_type=relationship_update`
   - `tick_from=1`, `tick_to=5`
3. Confirm visible causal path:
   - world event -> decision -> message -> relationship update -> memory trace

## 9. Run tests

```bash
uv run pytest
```

## 10. Run US3 variant comparison

Run API comparison endpoint:

```bash
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/compare-rerun \
  -H "Content-Type: application/json" \
  -d '{"ticks":3,"variant_name":"risk-heavy-ava","persona_overrides":{"Ava":{"risk_tolerance":0.95,"cooperation_tendency":0.2}}}'
```

Expected outcome:
- Response includes `base_scenario_id`, `variant_scenario_id`, and `comparison.differences`.
- `comparison.differences` includes `decision_count_delta`, `message_count_delta`, and `relationship_avg_trust_delta`.

UI path:
- Open dashboard `Comparison` page.
- Provide base scenario ID, overrides JSON, and ticks.
- Run comparison and inspect delta table.

## Troubleshooting

- If SQLite file lock occurs, stop duplicate API/dashboard processes.
- If dashboard appears stale, refresh filters and ensure API tick run completed.
- If no events appear, verify scenario seed succeeded and run endpoint returned tick results.
