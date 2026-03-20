# Quickstart: Phase 5 2D Embodied Simulation World

## Prerequisites

- Existing backend dependencies installed
- Existing database initialization and scenario seeding flow working
- Node.js 20+ available locally for the browser client

## 1. Initialize backend state

```powershell
python -m app.persistence.init_db
python -m app.persistence.seed --scenario sample_goal_resource_lab
```

## 2. Start the FastAPI backend

```powershell
uvicorn app.api.main:app --reload --port 8000
```

Expected backend services for this phase:

- REST API on `http://127.0.0.1:8000`
- WebSocket endpoint on `ws://127.0.0.1:8000/ws/simulation`
- world REST endpoints under `http://127.0.0.1:8000/api/world/...`

## 3. Start the Streamlit dashboard (unchanged)

```powershell
streamlit run app/dashboard/main.py --server.port 8501
```

This step is optional for embodied-world validation but remains available for trace
inspection.

## 4. Install and start the Phaser plus React client

```powershell
cd client
npm install
npm run dev
```

Expected local client URL:

- `http://127.0.0.1:5173`

## 5. Verify shared map loading

1. Confirm `maps/house.json` exists.
2. Confirm the frontend can load `client/public/assets/maps/house.json`.
3. Confirm the backend `GET /api/world/map` endpoint returns the same map metadata.

## 6. Run a live scenario

1. Get a scenario id:

```powershell
curl http://127.0.0.1:8000/scenarios
```

2. Run ticks:

```powershell
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/run -H "Content-Type: application/json" -d "{\"ticks\":10}"
```

3. Open the browser client and verify:
   - the tilemap renders
   - agents appear in rooms
   - movements update after ticks
   - clicking an agent opens detail in the side panel

## 7. Validate spatial grounding

1. Place food in the kitchen and at least one hungry agent elsewhere.
2. Run 10 ticks.
3. Verify:
   - backend traces show spatial context in the decision path
   - the agent visibly paths to the kitchen
   - room transition and movement path are reflected in the client

## 8. Validate replay mode

1. Request a replay range from the backend:

```powershell
curl http://127.0.0.1:8000/api/world/replay/1/10
```

2. In the client, load replay mode and scrub across the returned range.
3. Verify historical world state renders correctly without changing live backend state.

## 9. Guardrail checks

- The backend keeps running if the browser tab is closed.
- Two browser tabs can connect at once without changing simulation outcomes.
- Zone-only scenarios continue to run when no tilemap is configured.
- The Streamlit dashboard remains functional and unchanged.
