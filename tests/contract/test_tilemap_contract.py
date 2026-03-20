from pathlib import Path

from app.simulation.tilemap_loader import load_tilemap


def test_tilemap_contract_requires_shared_layers_and_zone_properties() -> None:
    tilemap = load_tilemap()
    assert {"floor", "walls", "furniture", "collision", "objects"}.issubset(tilemap.layers.keys())
    assert all(zone.zone_name for zone in tilemap.zones.values())
    assert any(obj.properties.get("resource_type") == "food" for obj in tilemap.objects)


def test_tilemap_contract_includes_client_copy_path() -> None:
    assert Path("client/public/assets/maps/house.json").exists()
