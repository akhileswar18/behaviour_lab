import Phaser from "phaser";

import { AgentSprite, tileToWorldPosition } from "../sprites/AgentSprite";
import { InteractionArc } from "../ui/InteractionArc";
import { interpolatePosition } from "../systems/Interpolation";
import { applyDayNightTint } from "../systems/DayNight";
import type { WorldSnapshot } from "../../types/world";
import type { RenderAgentState } from "../../hooks/useSimulationState";
import { buildWorldAssetManifest, Preloader } from "./Preloader";

interface WorldSceneConfig {
  baseUrl: string;
  onSelectAgent: (agentId: string) => void;
}

interface TiledLayerPayload {
  name?: string;
  type?: string;
  objects?: Array<Record<string, unknown>>;
}

interface TiledTilesetPayload {
  name?: string;
}

interface CachedMapPayload {
  width?: number;
  height?: number;
  tilewidth?: number;
  tileheight?: number;
  layers?: TiledLayerPayload[];
  tilesets?: TiledTilesetPayload[];
}

export interface TilemapRenderPlan {
  useFallback: boolean;
  mapWidth: number;
  mapHeight: number;
  tileWidth: number;
  tileHeight: number;
  visualLayers: string[];
  collisionLayer: string | null;
  objectLayer: string | null;
  tilesetName: string | null;
}

const SCENE_WIDTH = 960;
const SCENE_HEIGHT = 640;
const MINIMAP = { x: 792, y: 24, width: 140, height: 104 };
const TILEMAP_SCALE = 3;
const REQUIRED_VISUAL_LAYERS = ["floor", "walls", "furniture", "furniture_upper"] as const;
const REQUIRED_SEMANTIC_LAYERS = ["collision", "objects"] as const;

export function deriveTilemapRenderPlan(
  payload: CachedMapPayload | null | undefined,
): TilemapRenderPlan {
  const layerNames = new Set((payload?.layers ?? []).map((layer) => String(layer.name ?? "")));
  const hasRequiredVisualLayers = REQUIRED_VISUAL_LAYERS.every((layer) => layerNames.has(layer));
  const hasRequiredSemanticLayers = REQUIRED_SEMANTIC_LAYERS.every((layer) => layerNames.has(layer));
  const tilesetName = String(payload?.tilesets?.[0]?.name ?? "");
  const useFallback = !payload || !hasRequiredVisualLayers || !hasRequiredSemanticLayers || !tilesetName;

  return {
    useFallback,
    mapWidth: Number(payload?.width ?? 40),
    mapHeight: Number(payload?.height ?? 30),
    tileWidth: Number(payload?.tilewidth ?? 16),
    tileHeight: Number(payload?.tileheight ?? 16),
    visualLayers: useFallback ? [] : [...REQUIRED_VISUAL_LAYERS],
    collisionLayer: layerNames.has("collision") ? "collision" : null,
    objectLayer: layerNames.has("objects") ? "objects" : null,
    tilesetName: tilesetName || null,
  };
}

export class WorldScene extends Phaser.Scene {
  private readonly agentSprites = new Map<string, AgentSprite>();
  private readonly zoneGraphics = new Map<string, Phaser.GameObjects.Rectangle>();
  private readonly zoneLabels = new Map<string, Phaser.GameObjects.Text>();
  private readonly arcs: InteractionArc[] = [];
  private currentSnapshot: WorldSnapshot | null = null;
  private previousSnapshot: WorldSnapshot | null = null;
  private renderAgents = new Map<string, RenderAgentState>();
  private selectedAgentId: string | null = null;
  private viewMode: "live" | "replay" = "live";
  private followSelectedAgent = false;
  private isReady = false;
  private dayNightOverlay: Phaser.GameObjects.Rectangle | null = null;
  private minimapFrame: Phaser.GameObjects.Rectangle | null = null;
  private minimapGraphics: Phaser.GameObjects.Graphics | null = null;
  private cursors: Phaser.Types.Input.Keyboard.CursorKeys | null = null;
  private mapPixelWidth = 40 * 16 * TILEMAP_SCALE;
  private mapPixelHeight = 30 * 16 * TILEMAP_SCALE;
  private mapGridWidth = 40;
  private mapGridHeight = 30;
  private usingFallbackLayout = false;
  private fallbackReason = "";
  private hasAutoCenteredAgents = false;

  constructor(private readonly configData: WorldSceneConfig) {
    super("WorldScene");
  }

  create() {
    const renderPlan = deriveTilemapRenderPlan(this.getCachedMapPayload());
    this.mapGridWidth = renderPlan.mapWidth;
    this.mapGridHeight = renderPlan.mapHeight;
    this.mapPixelWidth = renderPlan.mapWidth * renderPlan.tileWidth * TILEMAP_SCALE;
    this.mapPixelHeight = renderPlan.mapHeight * renderPlan.tileHeight * TILEMAP_SCALE;
    this.usingFallbackLayout = renderPlan.useFallback;
    this.fallbackReason = renderPlan.useFallback
      ? this.describeFallbackReason(renderPlan)
      : "";

    this.cameras.main.setBounds(0, 0, this.mapPixelWidth, this.mapPixelHeight);
    this.cameras.main.setZoom(1);
    this.cameras.main.centerOn(this.mapPixelWidth / 2, this.mapPixelHeight / 2);

    this.dayNightOverlay = this.add
      .rectangle(SCENE_WIDTH / 2, SCENE_HEIGHT / 2, SCENE_WIDTH, SCENE_HEIGHT, 0x000000, 0)
      .setScrollFactor(0)
      .setDepth(15);
    this.minimapFrame = this.add
      .rectangle(MINIMAP.x + MINIMAP.width / 2, MINIMAP.y + MINIMAP.height / 2, MINIMAP.width, MINIMAP.height, 0x08111c, 0.85)
      .setStrokeStyle(1, 0x4f6b88)
      .setScrollFactor(0)
      .setDepth(18);
    this.minimapGraphics = this.add.graphics().setScrollFactor(0).setDepth(19);
    this.cursors = this.input.keyboard?.createCursorKeys() ?? null;

    this.input.on("wheel", (_pointer: Phaser.Input.Pointer, _targets: unknown, _deltaX: number, deltaY: number) => {
      const zoomDelta = deltaY > 0 ? -0.1 : 0.1;
      const nextZoom = Phaser.Math.Clamp(this.cameras.main.zoom + zoomDelta, 0.85, 2.25);
      this.cameras.main.setZoom(nextZoom);
      this.renderMinimap();
    });

    if (renderPlan.useFallback) {
      this.renderFallbackZoneLayout();
    } else {
      this.renderTilemap(renderPlan);
    }
    this.isReady = true;
    this.renderSnapshot();
  }

  update() {
    if (this.followSelectedAgent && this.viewMode === "replay") {
      return;
    }
    if (!this.cursors) {
      return;
    }

    const camera = this.cameras.main;
    const panStep = 8 / camera.zoom;

    if (this.cursors.left.isDown) {
      camera.scrollX -= panStep;
    }
    if (this.cursors.right.isDown) {
      camera.scrollX += panStep;
    }
    if (this.cursors.up.isDown) {
      camera.scrollY -= panStep;
    }
    if (this.cursors.down.isDown) {
      camera.scrollY += panStep;
    }

    this.renderMinimap();
  }

  syncSnapshot(
    previousSnapshot: WorldSnapshot | null,
    snapshot: WorldSnapshot | null,
    renderAgents: RenderAgentState[],
    selectedAgentId: string | null,
    viewMode: "live" | "replay",
    followSelectedAgent: boolean,
  ) {
    this.previousSnapshot = previousSnapshot;
    this.currentSnapshot = snapshot;
    this.renderAgents = new Map(renderAgents.map((item) => [item.agent.agent_id, item]));
    this.selectedAgentId = selectedAgentId;
    this.viewMode = viewMode;
    this.followSelectedAgent = followSelectedAgent;
    if (this.isReady) {
      this.renderSnapshot();
    }
  }

  private getCachedMapPayload(): CachedMapPayload | undefined {
    const cacheEntry = this.cache.tilemap.get("world-map") as { data?: CachedMapPayload } | undefined;
    return cacheEntry?.data;
  }

  private renderTilemap(renderPlan: TilemapRenderPlan) {
    const manifest = buildWorldAssetManifest(null);
    const map = this.make.tilemap({ key: manifest.map.key });
    const tileset = map.addTilesetImage(
      renderPlan.tilesetName ?? manifest.tileset.name,
      manifest.tileset.key,
    );
    if (!tileset) {
      this.usingFallbackLayout = true;
      this.fallbackReason = this.describeFallbackReason(renderPlan);
      this.renderFallbackZoneLayout();
      return;
    }

    for (const layerName of renderPlan.visualLayers) {
      const layer = map.createLayer(layerName, tileset, 0, 0);
      layer?.setScale(TILEMAP_SCALE);
    }

    const collisionLayer = map.getLayer("collision")?.tilemapLayer;
    collisionLayer?.setCollisionByExclusion([-1]);
    collisionLayer?.setScale(TILEMAP_SCALE);
    collisionLayer?.setVisible(false);
  }

  private renderFallbackZoneLayout() {
    const payload = this.getCachedMapPayload();
    const objectLayer = payload?.layers?.find((layer) => layer.name === "objects");
    const objects = objectLayer?.objects ?? [];

    this.add
      .rectangle(
        this.mapPixelWidth / 2,
        this.mapPixelHeight / 2,
        Math.max(this.mapPixelWidth - 64, 256),
        Math.max(this.mapPixelHeight - 64, 256),
        0x0d1622,
      )
      .setStrokeStyle(2, 0x3c556d);
    this.add
      .text(24, 18, "Embodied world map (fallback layout)", {
        color: "#edf2f7",
        fontSize: "18px",
      })
      .setScrollFactor(0);
    this.add
      .text(24, 44, `Fallback active: ${this.fallbackReason || "real map assets are unavailable."}`, {
        color: "#fbd38d",
        fontSize: "13px",
      })
      .setScrollFactor(0);

    for (const item of objects) {
      if (item.type !== "zone") {
        continue;
      }
      const properties = Array.isArray(item.properties) ? item.properties : [];
      const zoneProperty = properties.find((entry) => entry.name === "zone");
      if (!zoneProperty?.value || typeof item.x !== "number" || typeof item.y !== "number") {
        continue;
      }
      const zoneName = String(zoneProperty.value);
      const width = typeof item.width === "number" ? item.width * TILEMAP_SCALE : 48;
      const height = typeof item.height === "number" ? item.height * TILEMAP_SCALE : 48;
      const x = item.x * TILEMAP_SCALE + width / 2;
      const y = item.y * TILEMAP_SCALE + height / 2;
      const rectangle = this.add.rectangle(x, y, width, height, 0x1d2b3d, 0.55);
      rectangle.setStrokeStyle(2, 0x5b7da0);
      const label = this.add.text(x - width / 2 + 8, y - height / 2 + 8, zoneName, {
        color: "#dbeafe",
        fontSize: "14px",
      });
      this.zoneGraphics.set(zoneName, rectangle);
      this.zoneLabels.set(zoneName, label);
    }
  }

  private renderSnapshot() {
    if (!this.currentSnapshot) {
      return;
    }

    this.centerOnAgentsIfNeeded();
    applyDayNightTint(this, this.currentSnapshot.time_of_day, this.dayNightOverlay);

    for (const agent of this.currentSnapshot.agents) {
      let sprite = this.agentSprites.get(agent.agent_id);
      const renderAgent = this.renderAgents.get(agent.agent_id);
      const displayAgent = renderAgent?.agent ?? agent;
      if (!sprite) {
        sprite = new AgentSprite(
          this,
          displayAgent,
          renderAgent?.spriteKey ?? "agent_1",
          this.configData.onSelectAgent,
        );
        this.agentSprites.set(agent.agent_id, sprite);
      }
      const previous = this.previousSnapshot?.agents.find(
        (item) => item.agent_id === agent.agent_id,
      );
      const position = interpolatePosition(previous, agent, 1);
      const deltaX = (agent.position?.tile_x ?? position.tile_x) - (previous?.position?.tile_x ?? position.tile_x);
      const deltaY = (agent.position?.tile_y ?? position.tile_y) - (previous?.position?.tile_y ?? position.tile_y);
      let facing: "down" | "left" | "right" | "up" = "down";
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        facing = deltaX < 0 ? "left" : deltaX > 0 ? "right" : "down";
      } else if (Math.abs(deltaY) > 0) {
        facing = deltaY < 0 ? "up" : "down";
      }
      sprite.updateSnapshot(
        displayAgent,
        position,
        agent.agent_id === this.selectedAgentId,
        facing,
        Math.abs(deltaX) + Math.abs(deltaY) > 0,
      );
    }

    this.renderConversationArcs();
    this.applyCameraMode();
    this.renderMinimap();

    for (const [agentId, sprite] of this.agentSprites.entries()) {
      if (!this.currentSnapshot.agents.some((agent) => agent.agent_id === agentId)) {
        sprite.destroy();
        this.agentSprites.delete(agentId);
      }
    }
  }

  private applyCameraMode() {
    const camera = this.cameras.main;
    if (this.viewMode === "replay" && this.followSelectedAgent && this.selectedAgentId) {
      const selectedSprite = this.agentSprites.get(this.selectedAgentId);
      if (selectedSprite) {
        camera.startFollow(selectedSprite.followTarget(), true, 0.16, 0.16);
        return;
      }
    }
    camera.stopFollow();
  }

  private centerOnAgentsIfNeeded() {
    if (this.hasAutoCenteredAgents || !this.currentSnapshot || this.selectedAgentId) {
      return;
    }
    const positionedAgents = this.currentSnapshot.agents.filter((agent) => agent.position);
    if (positionedAgents.length === 0) {
      return;
    }
    const anchor = positionedAgents.reduce(
      (accumulator, agent) => {
        accumulator.x += agent.position?.tile_x ?? 0;
        accumulator.y += agent.position?.tile_y ?? 0;
        return accumulator;
      },
      { x: 0, y: 0 },
    );
    const centerX = (anchor.x / positionedAgents.length) * 48 + 24;
    const centerY = (anchor.y / positionedAgents.length) * 48 + 24;
    this.cameras.main.centerOn(centerX, centerY);
    this.hasAutoCenteredAgents = true;
  }

  private renderMinimap() {
    if (!this.minimapGraphics) {
      return;
    }

    const graphics = this.minimapGraphics;

    graphics.clear();
    graphics.fillStyle(0x08111c, 0.75);
    graphics.fillRect(MINIMAP.x + 1, MINIMAP.y + 1, MINIMAP.width - 2, MINIMAP.height - 2);
    graphics.lineStyle(1, 0x4f6b88, 1);
    graphics.strokeRect(MINIMAP.x, MINIMAP.y, MINIMAP.width, MINIMAP.height);

    if (!this.usingFallbackLayout) {
      graphics.fillStyle(0x8b6b4d, 0.85);
      graphics.fillRect(MINIMAP.x + 8, MINIMAP.y + 8, MINIMAP.width - 16, MINIMAP.height - 16);
    }

    for (const agent of this.currentSnapshot?.agents ?? []) {
      if (!agent.position) {
        continue;
      }
      const dotX = MINIMAP.x + (agent.position.tile_x / this.mapGridWidth) * MINIMAP.width;
      const dotY = MINIMAP.y + (agent.position.tile_y / this.mapGridHeight) * MINIMAP.height;
      graphics.fillStyle(agent.agent_id === this.selectedAgentId ? 0xf8fafc : 0x8b7cf6, 1);
      graphics.fillCircle(dotX, dotY, agent.agent_id === this.selectedAgentId ? 4 : 3);
    }

    const viewX = (this.cameras.main.worldView.x / this.mapPixelWidth) * MINIMAP.width;
    const viewY = (this.cameras.main.worldView.y / this.mapPixelHeight) * MINIMAP.height;
    const viewWidth = (this.cameras.main.worldView.width / this.mapPixelWidth) * MINIMAP.width;
    const viewHeight = (this.cameras.main.worldView.height / this.mapPixelHeight) * MINIMAP.height;

    graphics.lineStyle(1, 0xffd166, 0.9);
    graphics.strokeRect(MINIMAP.x + viewX, MINIMAP.y + viewY, viewWidth, viewHeight);
  }

  private renderConversationArcs() {
    for (const arc of this.arcs) {
      arc.destroy();
    }
    this.arcs.length = 0;

    if (!this.currentSnapshot) {
      return;
    }

    for (const conversation of this.currentSnapshot.conversations) {
      const source = this.currentSnapshot.agents.find(
        (agent) => agent.agent_id === conversation.source_agent_id,
      );
      const target = this.currentSnapshot.agents.find(
        (agent) => agent.agent_id === conversation.target_agent_id,
      );
      if (!source?.position || !target?.position) {
        continue;
      }
      const arc = new InteractionArc(this);
      const sourcePoint = tileToWorldPosition(source.position);
      const targetPoint = tileToWorldPosition(target.position);
      arc.update(
        sourcePoint.x,
        sourcePoint.y,
        targetPoint.x,
        targetPoint.y,
      );
      this.arcs.push(arc);
    }
  }

  private describeFallbackReason(renderPlan: TilemapRenderPlan): string {
    const loadFailures = this.registry.get(Preloader.LOAD_FAILURES_KEY) as string[] | undefined;
    if (loadFailures?.length) {
      return `asset load failure for ${loadFailures.join(", ")}`;
    }
    if (!renderPlan.tilesetName) {
      return "the cached tilemap is missing a tileset definition";
    }
    if (!renderPlan.collisionLayer || !renderPlan.objectLayer) {
      return "the cached tilemap is missing required semantic layers";
    }
    if (renderPlan.visualLayers.length !== REQUIRED_VISUAL_LAYERS.length) {
      return "the cached tilemap is missing one or more visual layers";
    }
    return "real map assets are unavailable";
  }
}
