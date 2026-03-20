from pathlib import Path

from app.simulation.tilemap_loader import load_tilemap


def test_tilemap_loader_parses_required_layers_and_zones() -> None:
    tilemap = load_tilemap()

    assert tilemap.grid_width > 0
    assert tilemap.grid_height > 0
    assert {"floor", "walls", "furniture", "collision", "objects"}.issubset(tilemap.layers.keys())
    assert {"Commons", "Storage", "Shelter"}.issubset(tilemap.zones.keys())
    assert tilemap.center_for_zone("Commons") == (4, 3)
    assert tilemap.center_for_zone("Storage") == (11, 3)
    assert tilemap.center_for_zone("Shelter") == (5, 9)
    assert any(item.name == "FoodCrate" and item.zone_name == "Storage" for item in tilemap.objects)
    assert any(item.name == "Bed" and item.zone_name == "Shelter" for item in tilemap.objects)


def test_tilemap_loader_uses_repository_map_path() -> None:
    tilemap = load_tilemap()
    assert Path(tilemap.map_file_path).exists()
