# Multi-Agent Behavior Lab

Lightweight, local-first multi-agent simulation platform focused on persona, memory,
communication, goals, needs, resources, observability, and embodied spatial grounding.

## Phase 4 MVP

Phase 4 is the current active build. The system now supports:

- small deterministic scenarios with 2-5 persistent agents
- persisted goals and active intentions across ticks
- need-driven behavior with hunger, safety, and social pressure
- structured communication, relationship updates, and memory traces
- zone-based world grounding with location-dependent opportunities
- scarce resources with acquire/consume/shortage events
- urgent world events that can interrupt an active plan
- comparison reruns with persona, planning, and world overrides
- optional hybrid decision engine (`deterministic`, `llm`, `hybrid`)
- strict structured LLM output parsing and deterministic fallback
- persisted decision-source, parser-status, and fallback telemetry
- FastAPI and Streamlit surfaces backed by persisted SQLite state
- Constitution v1.1.0 defines an additive Phaser 3 + React embodied world viewer over
  FastAPI WebSocket for the next phase; the current Phase 4 codebase remains
  dashboard-first in shipped functionality

## Local run sequence

1. Install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

2. Configure environment

```powershell
Copy-Item .env.example .env
```

3. Initialize and seed a scenario

```powershell
python -m app.persistence.init_db
python -m app.persistence.seed --scenario sample_goal_resource_lab
```

4. Start API

```powershell
uvicorn app.api.main:app --reload --port 8000
```

5. Start dashboard (new terminal)

```powershell
streamlit run app/dashboard/main.py --server.port 8501
```

6. Get the scenario id

```powershell
curl http://127.0.0.1:8000/scenarios
```

7. Run deterministic ticks

```powershell
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/run -H "Content-Type: application/json" -d '{"ticks":10}'
```

8. Run hybrid mode with explicit LLM config and fallback safety

```powershell
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/run -H "Content-Type: application/json" -d "{\"ticks\":5,\"policy_mode\":\"hybrid\",\"llm_config\":{\"provider\":\"openai_compatible\",\"endpoint\":\"http://127.0.0.1:11434/v1/chat/completions\",\"model\":\"gpt-4o-mini\",\"timeout_seconds\":4.0}}"
```

## What to inspect in UI

- `Agents`: needs, active goal, active intention, zone, inventory, decision rationale.
- `Goals`: goal status and plan history.
- `Zones`: occupancy and local opportunities.
- `Resources`: quantity and status over time.
- `Communication`: structured message flow.
- `Relationships`: trust, affinity, stance, and update timing.
- `Timeline`: need -> goal -> plan_change -> move/resource/social effects.
- `Comparison`: rerun a scenario with policy-mode overrides and inspect deltas.

## Phase 4 comparison example

```powershell
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/compare-rerun -H "Content-Type: application/json" -d "{\"ticks\":5,\"variant_name\":\"llm-vs-det\",\"base_policy_mode\":\"deterministic\",\"variant_policy_mode\":\"hybrid\",\"variant_llm_config\":{\"provider\":\"openai_compatible\",\"endpoint\":\"http://127.0.0.1:11434/v1/chat/completions\",\"model\":\"gpt-4o-mini\"}}"
```

## Validation checklist

- `/health` returns `200`.
- `POST /scenarios/{id}/run` in all policy modes completes with `tick_results`.
- `POST /scenarios/{id}/run` returns `policy_mode`, `fallback_count`, and decision source counts.
- dashboard pages load and read persisted state only.
- `POST /scenarios/{id}/compare-rerun` returns policy-aware deltas including fallback/llm deltas.
- `pytest -q` passes locally.

## Tests

```powershell
pytest -q
```

## Known limitations

- LLM reasoning is single-step per tick only; no long-horizon freeform planner
- no vector memory, websockets, auth, cloud runtime, or distributed agents
- the Phaser 3 embodied world viewer defined in constitution v1.1.0 is not yet shipped in
  Phase 4
- no full physics, complex economy, or complex emotion engine
- reset behavior is basic and should not be treated as a full scenario restore workflow

## Demo docs

See [phase2-demo.md](C:/Users/akhil/behaviour_lab/docs/phase2-demo.md) for the previous social-loop demo.
See [phase3-demo.md](C:/Users/akhil/behaviour_lab/docs/phase3-demo.md) for the current goal/resource demo flow.
See [phase4-hybrid-runbook.md](C:/Users/akhil/behaviour_lab/docs/phase4-hybrid-runbook.md) for hybrid policy mode operation and fallback troubleshooting.
