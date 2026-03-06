# Multi-Agent Behavior Lab

Lightweight, local-first multi-agent simulation platform focused on persona, memory,
communication, and observability.

## What this MVP does

- Runs small scenarios with 2-5 persistent agents.
- Persists simulation events, decisions, messages, memories, and relationships in SQLite.
- Exposes a FastAPI control/query surface.
- Provides Streamlit pages for agents, timeline, memories, and relationships.

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

3. Initialize and seed

```powershell
python -m app.persistence.init_db
python -m app.persistence.seed --scenario sample_social_triad
```

4. Start API

```powershell
uvicorn app.api.main:app --reload --port 8000
```

5. Start dashboard (new terminal)

```powershell
streamlit run app/dashboard/main.py --server.port 8501
```

6. Run ticks

```powershell
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/run -H "Content-Type: application/json" -d '{"ticks":10}'
```

7. Inspect

- Agents page: persona, current state, recent/recalled memories, relationships.
- Timeline page: events and communication feed with filters.
- Memories page: memory timeline + recall traces.
- Relationships page: social state records.

8. Reset and rerun

```powershell
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/reset
```

## Tests

```powershell
pytest
```

## Demo steps

See `docs/demo-success-criteria.md` for go/no-go demo checklist.
See `docs/mvp-limitations.md` for explicit non-goals.
