# Changelog

## 2026-03-05

### Added
- Phase 2 social simulation architecture with deterministic tick-based behavior.
- Structured communication flow with message intent, tone, and causal timeline events.
- Relationship update policy with trust/affinity changes and stance tracking.
- Scenario/world-event injection and consumption in simulation loop.
- Decision logs enriched with persona, relationship, and world-event factors.
- Dashboard social observability pages and filters:
  - communication feed
  - relationship view
  - richer timeline filters
  - agent social-context details
- US3 comparison variant workflow:
  - compare-rerun API endpoint
  - baseline vs variant scenario cloning
  - persona override application
  - run-difference summary persistence
  - comparison dashboard page

### Updated
- API routes for messages, relationships, timeline, simulation, and comparison.
- Persistence models and DB initialization with added indexes/fields for social dynamics.
- Seed scenarios and personas for deterministic social behavior testing.
- Quickstart documentation for US1/US2/US3 workflows.
- Task tracking in `specs/001-behavior-lab-simulation/tasks.md` through US3.

### Validation
- Test suite passing after US3 implementation (`22 passed`).
