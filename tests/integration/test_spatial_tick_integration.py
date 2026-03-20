from sqlmodel import Session, select

from app.persistence.engine import get_engine
from app.persistence.init_db import init_db
from app.persistence.models import AgentStateSnapshot, TileMapConfig
from app.persistence.models import Scenario
from app.persistence.seed import seed_sample_goal_resource_lab
from app.schemas.decision_engine import (
    DecisionSource,
    ParserStatus,
    PolicyMode,
    StructuredDecision,
    StructuredDecisionResult,
)
from app.simulation.tick_engine import run_tick


def test_embodied_run_persists_tile_coordinates(phase3_seeded_client) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    run_response = phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 1})

    assert run_response.status_code == 200
    with Session(get_engine()) as session:
        configs = list(session.exec(select(TileMapConfig)))
        states = list(session.exec(select(AgentStateSnapshot).where(AgentStateSnapshot.tick_number == 1)))

    assert configs
    assert states
    assert all(state.tile_x is not None and state.tile_y is not None for state in states)


def test_embodied_world_rest_endpoints_return_map_and_replay(phase3_seeded_client) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 2})

    world_map = phase3_seeded_client.get(f"/api/world/map?scenario_id={scenario_id}")
    replay = phase3_seeded_client.get(f"/api/world/replay/1/2?scenario_id={scenario_id}")

    assert world_map.status_code == 200
    assert replay.status_code == 200
    assert replay.json()["tick_start"] == 1
    assert len(replay.json()["snapshots"]) == 2


def test_replay_range_returns_ordered_stored_ticks_only(phase3_seeded_client) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 3})

    replay = phase3_seeded_client.get(f"/api/world/replay/2/5?scenario_id={scenario_id}")
    missing = phase3_seeded_client.get(f"/api/world/replay/8/10?scenario_id={scenario_id}")

    assert replay.status_code == 200
    assert replay.json()["tick_start"] == 2
    assert replay.json()["tick_end"] == 3
    assert [snapshot["tick_number"] for snapshot in replay.json()["snapshots"]] == [2, 3]
    assert missing.status_code == 404


class CapturingDecisionEngine:
    def __init__(self) -> None:
        self.contexts = []

    def resolve(self, context, mode, llm_config=None, constraints=None) -> StructuredDecisionResult:
        self.contexts.append(context)
        return StructuredDecisionResult(
            decision=StructuredDecision(
                action="observe",
                intent="observe",
                emotional_tone="neutral",
                rationale="capture spatial context",
                confidence=0.5,
            ),
            decision_source=DecisionSource.DETERMINISTIC,
            parser_status=ParserStatus.NOT_ATTEMPTED,
        )


def test_spatial_context_flows_into_decision_engine() -> None:
    init_db()
    seed_sample_goal_resource_lab()

    with Session(get_engine()) as session:
        scenario_id = session.exec(select(Scenario.id)).first()
        engine = CapturingDecisionEngine()
        run_tick(session, scenario_id, 1, policy_mode=PolicyMode.DETERMINISTIC, decision_engine=engine)

    assert engine.contexts
    ben_context = next(context for context in engine.contexts if context.agent_name == "Ben")
    assert ben_context.spatial_context is not None
    assert ben_context.spatial_context.current_room == "Storage"
    assert any(item.name == "FoodCrate" for item in ben_context.spatial_context.nearby_objects)
    assert ben_context.spatial_context.pathfinding_costs.get("Storage:food") == 0
