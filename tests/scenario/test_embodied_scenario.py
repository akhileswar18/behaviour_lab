from fastapi.testclient import TestClient
from sqlmodel import Session, select
from uuid import UUID

from app.persistence.engine import get_engine
from app.persistence.models import Agent, AgentStateSnapshot, Resource, Scenario, Zone


def test_embodied_live_observation_flow(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]

    with phase3_seeded_client.websocket_connect(f"/ws/simulation?scenario_id={scenario_id}") as websocket:
        ack = websocket.receive_json()
        run_response = phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 3})
        messages = [websocket.receive_json() for _ in range(3)]

    assert ack["type"] == "connection_ack"
    assert run_response.status_code == 200
    assert all(message["type"] == "tick_update" for message in messages)
    assert any(agent["position"] is not None for agent in messages[-1]["agents"])


def test_spatial_context_steers_hungry_agent_to_nearest_food_source(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    scenario_uuid = UUID(scenario_id)

    with Session(get_engine()) as session:
        ben = session.exec(
            select(Agent).where(Agent.scenario_id == scenario_uuid).where(Agent.name == "Ben")
        ).one()
        zones = {
            zone.name: zone
            for zone in session.exec(select(Zone).where(Zone.scenario_id == scenario_uuid))
        }
        commons_zone_id = str(zones["Commons"].id)
        ben_state = session.exec(
            select(AgentStateSnapshot)
            .where(AgentStateSnapshot.agent_id == ben.id)
            .order_by(AgentStateSnapshot.tick_number.desc())
        ).first()
        ben_state.hunger = 0.95
        ben_state.inventory = {}

        for resource in session.exec(select(Resource).where(Resource.scenario_id == scenario_uuid)):
            if resource.resource_type == "food":
                resource.quantity = 0
                resource.status = "depleted"
                session.add(resource)

        session.add(Resource(scenario_id=scenario_uuid, zone_id=zones["Shelter"].id, resource_type="food", quantity=1))
        session.add(Resource(scenario_id=scenario_uuid, zone_id=zones["Commons"].id, resource_type="food", quantity=1))
        session.add(ben_state)
        session.commit()

    run_response = phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 1})
    replay = phase3_seeded_client.get(f"/api/world/replay/1/1?scenario_id={scenario_id}").json()

    assert run_response.status_code == 200
    ben_snapshot = next(agent for agent in replay["snapshots"][0]["agents"] if agent["name"] == "Ben")
    assert ben_snapshot["action"] == "move"
    assert ben_snapshot["path"] is not None
    assert ben_snapshot["path"]["target_zone_id"] == commons_zone_id
    assert len(ben_snapshot["path"]["waypoints"]) > 0
    assert ben_snapshot["spatial_context"]["pathfinding_costs"]["Commons:food"] < ben_snapshot["spatial_context"]["pathfinding_costs"]["Shelter:food"]


def test_replay_payload_matches_persisted_historical_world_state(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    scenario_uuid = UUID(scenario_id)

    run_response = phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 3})
    replay = phase3_seeded_client.get(f"/api/world/replay/1/3?scenario_id={scenario_id}").json()

    assert run_response.status_code == 200
    assert [snapshot["tick_number"] for snapshot in replay["snapshots"]] == [1, 2, 3]

    with Session(get_engine()) as session:
        agents = {
            str(agent.id): agent.name
            for agent in session.exec(select(Agent).where(Agent.scenario_id == scenario_uuid))
        }
        states = {
            (str(state.agent_id), state.tick_number): state
            for state in session.exec(
                select(AgentStateSnapshot)
                .join(Agent, Agent.id == AgentStateSnapshot.agent_id)
                .where(Agent.scenario_id == scenario_uuid)
            )
        }

    for snapshot in replay["snapshots"]:
        for agent in snapshot["agents"]:
            state = states[(agent["agent_id"], snapshot["tick_number"])]
            assert agents[agent["agent_id"]] == agent["name"]
            assert agent["position"]["tile_x"] == state.tile_x
            assert agent["position"]["tile_y"] == state.tile_y
            assert agent["zone_id"] == (str(state.zone_id) if state.zone_id else None)
