from pathlib import Path
from uuid import uuid4

from app.api.schemas.world import ConnectionAckRead, WorldSnapshotRead


def test_websocket_models_expose_required_message_fields() -> None:
    ack = ConnectionAckRead(scenario_id=str(uuid4()), current_tick=3, server_time="2026-03-19T00:00:00Z")
    snapshot = WorldSnapshotRead(
        scenario_id=str(uuid4()),
        tick_number=1,
        sim_time="2026-03-19T00:00:00Z",
        time_of_day="day",
    )

    assert ack.type == "connection_ack"
    assert snapshot.type == "tick_update"
    assert snapshot.schema_version == "1.0"


def test_client_world_types_define_world_snapshot_contract() -> None:
    content = Path("client/src/types/world.ts").read_text(encoding="utf-8")
    assert "interface WorldSnapshot" in content
    assert "schema_version" in content
    assert "type: \"tick_update\"" in content
    assert "interface SpatialPerception" in content
    assert "spatial_context" in content
