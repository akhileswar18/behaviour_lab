# First Demo Success Criteria

## Demo Goal

Demonstrate a local, inspectable multi-agent simulation where persona, memory,
communication, and relationships influence state over time.

## Go/No-Go Checklist

- [ ] API starts locally and `/health` returns `ok`
- [ ] Dashboard starts locally and loads all core pages
- [ ] Seeded scenario contains 3 agents with distinct personas
- [ ] Running 10 ticks persists decisions and events
- [ ] Communication records appear in message feed
- [ ] Memory timeline and recall traces are visible
- [ ] Relationship records update across ticks
- [ ] Scenario reset clears generated run artifacts and supports rerun
- [ ] Smoke tests pass (`pytest tests/smoke`)

## Demo Script

1. Initialize DB and seed scenario
2. Run API and dashboard
3. Execute simulation ticks
4. Inspect timeline, memories, and relationships
5. Reset scenario and rerun
