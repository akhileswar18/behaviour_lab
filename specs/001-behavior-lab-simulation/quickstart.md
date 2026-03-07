# Quickstart: Phase 3 Goal-Directed Situated Behavior

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
. .venv/Scripts/activate
pip install -e .[dev]
```

## 2. Configure environment

Create `.env` from `.env.example` and set:

- `APP_ENV=local`
- `DATABASE_URL=sqlite:///./data/behavior_lab.db`
- `LOG_LEVEL=INFO`

## 3. Initialize database and seed a situated scenario

```bash
python -m app.persistence.init_db
python -m app.persistence.seed --scenario sample_goal_resource_lab
```

Expected outcome:

- one scenario with 3 agents
- 3 zones with different local opportunities
- simple resources available in selected zones
- seeded goals/needs and starting locations
- at least one urgent event scheduled for interruption testing

## 4. Run API

```bash
uv run uvicorn app.api.main:app --reload --port 8000
```

## 5. Run dashboard

```bash
uv run streamlit run app/dashboard/main.py --server.port 8501
```

## 6. Execute ticks

```bash
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/run \
  -H "Content-Type: application/json" \
  -d '{"ticks":10}'
```

## 7. Validate User Story 1

- Agents show active goals and current intentions.
- Needs change over time.
- At least one goal remains active across multiple ticks.
- Agent detail view shows needs, location, active goal, and active intention.

## 8. Validate User Story 2

- Zone occupancy changes over time for at least one agent.
- Resources are acquired or consumed and quantities change.
- Timeline shows `plan_change`, `move`, `acquire`/`consume`, and `interruption` events.
- At least one urgent event or severe need interrupts an existing intention.

## 9. Validate User Story 3

Run a variant comparison:

```bash
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/compare-rerun \
  -H "Content-Type: application/json" \
  -d '{"ticks":5,"variant_name":"hungry-ben","planning_overrides":{"Ben":{"hunger":0.95}},"world_overrides":{"Storage":{"food":0}}}'
```

Expected outcome:

- response contains `completed_goal_delta`, `move_event_delta`, and `resource_event_delta`
- comparison dashboard shows changed outcome counts across baseline and variant runs

## 10. Dashboard inspection order

1. `Agents`: inspect needs, current goal, active intention, location, and inventory.
2. `Goals`: inspect goal status and plan history.
3. `Zones`: inspect occupancy and local opportunities.
4. `Resources`: inspect quantity changes over time.
5. `Timeline`: verify need -> goal -> plan -> action -> effect causality.
6. `Comparison`: inspect deterministic differences after overrides.

## 11. Run tests

```bash
uv run pytest
```

## Troubleshooting

- If agents never move, verify zones and target resources are seeded correctly.
- If resources never change, confirm resource actions are permitted in the agent's current zone.
- If interruptions never fire, verify urgent events or severe-need thresholds exist in the scenario.
- If comparison deltas remain flat, increase the need override or reduce a key resource quantity.
