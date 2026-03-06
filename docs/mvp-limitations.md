# MVP Limitations

## In Scope

- Local-only single-machine execution
- Small scenarios (2-5 agents)
- Tick-based simulation with persisted state/events
- FastAPI + Streamlit observability loop

## Out of Scope (Current MVP)

- Websocket streaming updates
- User authentication/authorization
- Cloud deployment and managed infrastructure
- Distributed multi-process agent runtime
- Vector database memory subsystem
- Full LLM-driven behavior as default path
- 3D/game-engine world simulation

## Known Tradeoffs

- Simple deterministic decision policy used for baseline behavior
- SQLite chosen for inspectability over concurrent throughput
- Dashboard polling over push updates to preserve simplicity
