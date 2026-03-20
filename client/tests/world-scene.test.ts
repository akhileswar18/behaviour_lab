import { describe, expect, it } from "vitest";

import houseMap from "../public/assets/maps/house.json";
import preloaderSource from "../src/game/scenes/Preloader.ts?raw";
import worldSceneSource from "../src/game/scenes/WorldScene.ts?raw";

describe("world-scene asset manifest", () => {
  it("loads the real public house map, tileset, and agent spritesheets", () => {
    expect(preloaderSource).toContain('this.load.tilemapTiledJSON(manifest.map.key, manifest.map.path)');
    expect(preloaderSource).toContain('path: "/assets/maps/house.json"');
    expect(preloaderSource).toContain('path: "/assets/tilesets/interiors.png"');
    expect(preloaderSource).toContain('path: "/assets/tilesets/agents/agent_1.png"');
    expect(preloaderSource).toContain('path: "/assets/tilesets/agents/agent_2.png"');
    expect(preloaderSource).toContain('path: "/assets/tilesets/agents/agent_3.png"');
  });

  it("logs loader failures so fallback mode is explainable", () => {
    expect(preloaderSource).toContain('this.load.on("loaderror"');
    expect(preloaderSource).toContain('console.warn("[embodied-world] Asset load failed:"');
  });
});

describe("world-scene render planning", () => {
  it("ships the required Tiled map structure for the real house render path", () => {
    expect(houseMap.width).toBe(40);
    expect(houseMap.height).toBe(30);
    expect(houseMap.tilewidth).toBe(16);
    expect(houseMap.tileheight).toBe(16);
    expect(houseMap.layers.map((layer) => layer.name)).toEqual(
      expect.arrayContaining([
        "floor",
        "walls",
        "furniture",
        "furniture_upper",
        "collision",
        "objects",
      ]),
    );
  });

  it("renders the real tilemap layers and preserves a fallback path", () => {
    expect(worldSceneSource).toContain('this.make.tilemap({ key: manifest.map.key })');
    expect(worldSceneSource).toContain('map.addTilesetImage(');
    expect(worldSceneSource).toContain('map.createLayer(layerName, tileset, 0, 0)');
    expect(worldSceneSource).toContain('collisionLayer?.setCollisionByExclusion([-1])');
    expect(worldSceneSource).toContain("renderFallbackZoneLayout");
    expect(worldSceneSource).toContain('Embodied world map (fallback layout)');
    expect(worldSceneSource).toContain('Fallback active:');
  });
});
