import Phaser from "phaser";

export interface SpritesheetManifest {
  key: string;
  path: string;
  frameWidth: number;
  frameHeight: number;
}

export interface WorldAssetManifest {
  map: {
    key: string;
    path: string;
  };
  tileset: {
    key: string;
    name: string;
    path: string;
  };
  spritesheets: SpritesheetManifest[];
}

export function buildWorldAssetManifest(_scenarioId: string | null): WorldAssetManifest {
  return {
    map: {
      key: "world-map",
      path: "/assets/maps/house.json",
    },
    tileset: {
      key: "interiors-tiles",
      name: "interiors",
      path: "/assets/tilesets/interiors.png",
    },
    spritesheets: [
      {
        key: "agent_1",
        path: "/assets/tilesets/agents/agent_1.png",
        frameWidth: 16,
        frameHeight: 16,
      },
      {
        key: "agent_2",
        path: "/assets/tilesets/agents/agent_2.png",
        frameWidth: 16,
        frameHeight: 16,
      },
      {
        key: "agent_3",
        path: "/assets/tilesets/agents/agent_3.png",
        frameWidth: 16,
        frameHeight: 16,
      },
    ],
  };
}

export class Preloader extends Phaser.Scene {
  static readonly LOAD_FAILURES_KEY = "embodied-world-load-failures";

  constructor(
    private readonly baseUrl: string,
    private readonly scenarioId: string | null,
  ) {
    super("Preloader");
  }

  preload() {
    const manifest = buildWorldAssetManifest(this.scenarioId);
    const loadFailures: string[] = [];

    this.load.on("loaderror", (file: { key?: string; src?: string }) => {
      const failedKey = String(file.key ?? file.src ?? "unknown-asset");
      if (!loadFailures.includes(failedKey)) {
        loadFailures.push(failedKey);
      }
      console.warn("[embodied-world] Asset load failed:", failedKey);
      this.registry.set(Preloader.LOAD_FAILURES_KEY, [...loadFailures]);
    });

    this.load.tilemapTiledJSON(manifest.map.key, manifest.map.path);
    this.load.image(manifest.tileset.key, manifest.tileset.path);
    for (const spritesheet of manifest.spritesheets) {
      this.load.spritesheet(spritesheet.key, spritesheet.path, {
        frameWidth: spritesheet.frameWidth,
        frameHeight: spritesheet.frameHeight,
      });
    }
  }

  create() {
    if (!this.registry.has(Preloader.LOAD_FAILURES_KEY)) {
      this.registry.set(Preloader.LOAD_FAILURES_KEY, []);
    }
    this.scene.start("WorldScene");
  }
}
