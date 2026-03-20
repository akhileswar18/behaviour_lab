from uuid import uuid4

from app.persistence.models import Agent, AgentStateSnapshot, Resource, Zone
from app.simulation.spatial_context import build_spatial_perception
from app.simulation.tilemap_loader import load_tilemap


def test_spatial_context_exposes_nearby_agents_and_resources() -> None:
    scenario_id = uuid4()
    commons = Zone(id=uuid4(), scenario_id=scenario_id, name="Commons", zone_type="commons")
    storage = Zone(id=uuid4(), scenario_id=scenario_id, name="Storage", zone_type="storage")
    agents = {
        uuid4(): Agent(id=uuid4(), scenario_id=scenario_id, persona_profile_id=uuid4(), name="Ava"),
        uuid4(): Agent(id=uuid4(), scenario_id=scenario_id, persona_profile_id=uuid4(), name="Ben"),
    }
    agent_ids = list(agents.keys())
    states = {
        agent_ids[0]: AgentStateSnapshot(agent_id=agent_ids[0], tick_number=1, zone_id=commons.id, tile_x=2, tile_y=2),
        agent_ids[1]: AgentStateSnapshot(agent_id=agent_ids[1], tick_number=1, zone_id=storage.id, tile_x=9, tile_y=2),
    }
    resources = [
        Resource(
            id=uuid4(),
            scenario_id=scenario_id,
            zone_id=storage.id,
            resource_type="food",
            quantity=2,
        )
    ]

    perception = build_spatial_perception(
        agent=agents[agent_ids[0]],
        state=states[agent_ids[0]],
        zone=commons,
        tilemap=load_tilemap(),
        latest_state_by_agent=states,
        agents_by_id=agents,
        zones_by_id={commons.id: commons, storage.id: storage},
        resources=resources,
        radius=10,
    )

    assert perception.current_room == "Commons"
    assert any(item.agent_name == "Ben" for item in perception.nearby_agents)
    assert all(item.object_type != "zone" for item in load_tilemap().objects if item.name in {"FoodCrate", "Bed"})
    assert any(item.name == "FoodCrate" for item in perception.nearby_objects)
    assert any(item["resource_type"] == "food" for item in perception.visible_resources) is False
    assert "Storage:food" in perception.pathfinding_costs


def test_spatial_context_uses_zone_center_when_tile_coordinates_are_missing() -> None:
    scenario_id = uuid4()
    commons = Zone(id=uuid4(), scenario_id=scenario_id, name="Commons", zone_type="commons")
    ava_id = uuid4()
    agents = {
        ava_id: Agent(id=ava_id, scenario_id=scenario_id, persona_profile_id=uuid4(), name="Ava"),
    }
    states = {
        ava_id: AgentStateSnapshot(agent_id=ava_id, tick_number=1, zone_id=commons.id),
    }

    perception = build_spatial_perception(
        agent=agents[ava_id],
        state=states[ava_id],
        zone=commons,
        tilemap=load_tilemap(),
        latest_state_by_agent=states,
        agents_by_id=agents,
        zones_by_id={commons.id: commons},
        resources=[],
        radius=4,
    )

    assert perception.current_tile is not None
    assert (perception.current_tile.tile_x, perception.current_tile.tile_y) == (4, 3)
    assert perception.current_room == "Commons"
