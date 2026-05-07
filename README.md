# Multi-Agent Behavior Lab

A local-first research platform for simulating persistent multi-agent systems — where synthetic agents live with goals, memories, needs, relationships, and personalities, making decisions tick by tick inside a shared, resource-constrained world.

---

## What we are building

Most agent frameworks treat agents as stateless function-callers: give them a prompt, get an action, repeat. We are building something different.

**Behaviour Lab** is a sandbox for studying how autonomous agents behave over time when they have:

- **Persistent identity** — each agent carries a persona (risk tolerance, communication style, emotional bias, cooperation profile) that shapes every decision it makes.
- **Competing needs** — hunger, safety, and social belonging create pressure that forces agents to prioritize and trade off goals dynamically.
- **Episodic memory** — agents remember past events with salience scores, and those memories influence future decisions and communications.
- **Goals and intentions** — agents pursue multi-step plans toward longer-horizon objectives, adapting when the world changes around them.
- **Social dynamics** — agents communicate with structured intent, and every message updates trust, affinity, and relational stance.
- **A shared physical world** — a tile-map environment with zones, scarce resources, pathfinding, and spatial context that agents must navigate.

The central research question is: **what behaviors emerge when you combine all of these dimensions together inside a controlled simulation?**

We want to run experiments. We want to compare runs. We want to swap decision policies — pure heuristics vs. LLM reasoning vs. a hybrid with automatic fallback — and measure the differences. We want a replay viewer so we can watch exactly what happened, tick by tick. We want full telemetry so nothing is hidden.

That is what this project is.

---

## Architecture overview

```
┌───────────────────────────────────────────────────────────────────┐
│  React + Phaser 3 Embodied World Viewer (client/)                 │
│  Live WebSocket feed · Replay mode · Agent sprites · Minimap      │
└───────────────────────┬───────────────────────────────────────────┘
                        │ WebSocket / REST
┌───────────────────────▼───────────────────────────────────────────┐
│  FastAPI (app/api/)                                               │
│  Scenarios · Simulation ticks · Agents · Goals · Relationships    │
│  Resources · Zones · Timeline · Analytics · Comparison reruns     │
└──────┬──────────────────────┬────────────────────────────────────┘
       │                      │
┌──────▼──────────┐  ┌────────▼──────────────────────────────────┐
│ Streamlit       │  │  Simulation Engine (app/simulation/)       │
│ Dashboard       │  │  Tick loop · World state · Pathfinding     │
│ (app/dashboard/)│  │  Spatial context · Scenario loader         │
└─────────────────┘  └────────┬──────────────────────────────────┘
                              │
             ┌────────────────┼────────────────────┐
             │                │                    │
    ┌────────▼──────┐ ┌───────▼───────┐  ┌────────▼──────────┐
    │ Decision      │ │ Memory        │  │ Communication     │
    │ Engine        │ │ (app/memory/) │  │ (app/communi-     │
    │ (app/agents/) │ │               │  │  cation/)         │
    │               │ │ Salience ·    │  │                   │
    │ Deterministic │ │ Retrieval ·   │  │ Message bus ·     │
    │ LLM · Hybrid  │ │ Writing       │  │ Relationship      │
    │ + fallback    │ └───────────────┘  │ updates           │
    └───────────────┘                   └────────────────────┘
                              │
             ┌────────────────▼────────────────────┐
             │  SQLite Persistence (app/persistence/)│
             │  Agents · Goals · Intentions ·        │
             │  Snapshots · Memories · Messages ·    │
             │  Relationships · DecisionLogs ·       │
             │  TickResults · Resources · Zones      │
             └───────────────────────────────────────┘
```

---

## Decision engine

Agents make decisions through one of three policy modes, selectable per simulation run:

| Mode | Behavior |
|---|---|
| `deterministic` | Pure heuristic logic — fast, reproducible, zero external dependencies |
| `llm` | LLM invocation with structured output parsing |
| `hybrid` | LLM attempt first; automatic fallback to deterministic on timeout, parse error, or constraint violation |

Every decision is logged with its source (`DETERMINISTIC`, `LLM`, `FALLBACK_DETERMINISTIC`), parser status, fallback reason, LLM latency, and prompt hash — so you can compare runs quantitatively.

---

## Comparison workflow

The comparison rerun endpoint runs the same scenario twice — a baseline and a variant — and returns structured deltas across decision sources, fallback counts, needs, goal completion rates, and behavioral differences. This is the core scientific primitive: **hold everything constant, change one thing, measure what shifts**.

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend API | Python 3.11+, FastAPI, uvicorn |
| Simulation & agents | Pure Python (no ML framework required for deterministic mode) |
| Persistence | SQLite via SQLModel + Pydantic |
| Dashboard | Streamlit |
| Embodied world viewer | React 18, Phaser 3, TypeScript, Vite |
| LLM integration | OpenAI-compatible REST (Ollama, OpenAI, any compatible endpoint) |
| Testing | pytest, httpx |

Everything runs locally. No cloud account, no API key required to run in deterministic mode.

---

## Quickstart

### 1. Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

### 2. Configure

```powershell
Copy-Item .env.example .env
```

### 3. Seed a scenario

```powershell
python -m app.persistence.init_db
python -m app.persistence.seed --scenario sample_goal_resource_lab
```

### 4. Start the API

```powershell
uvicorn app.api.main:app --reload --port 8000
```

### 5. Start the dashboard (new terminal)

```powershell
streamlit run app/dashboard/main.py --server.port 8501
```

### 6. Run a simulation

```powershell
# Get the scenario ID
curl http://127.0.0.1:8000/scenarios

# Run 10 deterministic ticks
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/run `
  -H "Content-Type: application/json" `
  -d '{"ticks": 10}'

# Run 5 hybrid ticks with a local Ollama model
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/run `
  -H "Content-Type: application/json" `
  -d '{
    "ticks": 5,
    "policy_mode": "hybrid",
    "llm_config": {
      "provider": "openai_compatible",
      "endpoint": "http://127.0.0.1:11434/v1/chat/completions",
      "model": "gpt-4o-mini",
      "timeout_seconds": 4.0
    }
  }'
```

### 7. Compare policy modes

```powershell
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/compare-rerun `
  -H "Content-Type: application/json" `
  -d '{
    "ticks": 5,
    "variant_name": "llm-vs-deterministic",
    "base_policy_mode": "deterministic",
    "variant_policy_mode": "hybrid",
    "variant_llm_config": {
      "provider": "openai_compatible",
      "endpoint": "http://127.0.0.1:11434/v1/chat/completions",
      "model": "gpt-4o-mini"
    }
  }'
```

---

## What to look at in the dashboard

| Page | What it shows |
|---|---|
| **Agents** | Live needs, active goal, active intention, zone, inventory, decision rationale |
| **Goals** | Goal status and plan history across ticks |
| **Zones** | Occupancy, local resource opportunities |
| **Resources** | Quantity and shortage events over time |
| **Communication** | Structured message flow with intent and tone |
| **Relationships** | Trust, affinity, stance, and how they shift after each interaction |
| **Timeline** | Causal chain: need pressure → goal formation → plan change → world effect |
| **Comparison** | Side-by-side deltas between baseline and variant runs |

---

## Run tests

```powershell
pytest -q
```

---

## Current phase: Phase 4 MVP

- Multi-agent tick loop with persistent goals, intentions, and needs
- Deterministic + hybrid decision engine with LLM fallback and full telemetry
- Zone-based spatial grounding with A* pathfinding
- Scarce resources with acquire/consume/shortage lifecycle
- Structured communication with relationship state updates
- Urgent world events that interrupt active plans
- Scenario comparison workflow
- FastAPI REST + WebSocket backend
- Streamlit observability dashboard
- React + Phaser 3 embodied world viewer with live WebSocket feed and replay mode

### Known limitations

- LLM reasoning is single-step per tick; no long-horizon freeform planner
- No vector memory, auth, cloud runtime, or distributed agents
- No full physics engine, complex economy, or advanced emotion model
- Scenario reset is basic and not a full restore workflow

---

## Demo runbooks

- [Phase 2 — Social loop demo](docs/phase2-demo.md)
- [Phase 3 — Goal and resource demo](docs/phase3-demo.md)
- [Phase 4 — Hybrid policy runbook and fallback troubleshooting](docs/phase4-hybrid-runbook.md)
