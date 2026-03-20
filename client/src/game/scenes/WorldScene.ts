import Phaser from "phaser";

import { AgentSprite } from "../sprites/AgentSprite";
import { InteractionArc } from "../ui/InteractionArc";
import { interpolatePosition } from "../systems/Interpolation";
import { applyDayNightTint } from "../systems/DayNight";
import type { WorldSnapshot } from "../../types/world";

interface WorldSceneConfig {
  baseUrl: string;
  onSelectAgent: (agentId: string) => void;
}

interface CachedMapPayload {
  map?: {
    width?: number;
    height?: number;
    layers?: Array<{ name?: string; objects?: Array<Record<string, unknown>> }>;
  };
}

const SCENE_WIDTH = 960;
const SCENE_HEIGHT = 640;
const WORLD_BOUNDS = { width: 1280, height: 960 };
const MINIMAP = { x: 792, y: 24, width: 140, height: 104 };

export class WorldScene extends Phaser.Scene {
  private readonly agentSprites = new Map<string, AgentSprite>();
  private readonly zoneGraphics = new Map<string, Phaser.GameObjects.Rectangle>();
  private readonly zoneLabels = new Map<string, Phaser.GameObjects.Text>();
  private readonly arcs: InteractionArc[] = [];
  private currentSnapshot: WorldSnapshot | null = null;
  private previousSnapshot: WorldSnapshot | null = null;
  private selectedAgentId: string | null = null;
  private viewMode: "live" | "replay" = "live";
  private followSelectedAgent = false;
  private isReady = false;
  private dayNightOverlay: Phaser.GameObjects.Rectangle | null = null;
  private minimapFrame: Phaser.GameObjects.Rectangle | null = null;
  private minimapGraphics: Phaser.GameObjects.Graphics | null = null;
  private cursors: Phaser.Types.Input.Keyboard.CursorKeys | null = null;

  constructor(private readonly configData: WorldSceneConfig) {
    super("WorldScene");
  }

  create() {
    this.cameras.main.setBounds(0, 0, WORLD_BOUNDS.width, WORLD_BOUNDS.height);
    this.cameras.main.setZoom(1);
    this.add.rectangle(480, 320, 900, 580, 0x0d1622).setStrokeStyle(2, 0x3c556d);
    this.add.text(24, 18, "Embodied world map", { color: "#edf2f7", fontSize: "18px" });

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

    this.renderZoneLayout();
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
    selectedAgentId: string | null,
    viewMode: "live" | "replay",
    followSelectedAgent: boolean,
  ) {
    this.previousSnapshot = previousSnapshot;
    this.currentSnapshot = snapshot;
    this.selectedAgentId = selectedAgentId;
    this.viewMode = viewMode;
    this.followSelectedAgent = followSelectedAgent;
    if (this.isReady) {
      this.renderSnapshot();
    }
  }

  private renderZoneLayout() {
    const payload = this.cache.json.get("world-map") as CachedMapPayload | undefined;
    const objectLayer = payload?.map?.layers?.find((layer) => layer.name === "objects");
    const objects = objectLayer?.objects ?? [];

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
      const width = typeof item.width === "number" ? item.width * 1.5 : 48;
      const height = typeof item.height === "number" ? item.height * 1.5 : 48;
      const x = 32 + item.x * 1.5 + width / 2;
      const y = 32 + item.y * 1.5 + height / 2;
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

    applyDayNightTint(this, this.currentSnapshot.time_of_day, this.dayNightOverlay);

    for (const agent of this.currentSnapshot.agents) {
      let sprite = this.agentSprites.get(agent.agent_id);
      if (!sprite) {
        sprite = new AgentSprite(this, agent, this.configData.onSelectAgent);
        this.agentSprites.set(agent.agent_id, sprite);
      }
      const previous = this.previousSnapshot?.agents.find(
        (item) => item.agent_id === agent.agent_id,
      );
      const position = interpolatePosition(previous, agent, 1);
      sprite.updateSnapshot(agent, position, agent.agent_id === this.selectedAgentId);
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

  private renderMinimap() {
    if (!this.minimapGraphics) {
      return;
    }

    const payload = this.cache.json.get("world-map") as CachedMapPayload | undefined;
    const gridWidth = payload?.map?.width ?? 32;
    const gridHeight = payload?.map?.height ?? 24;
    const graphics = this.minimapGraphics;

    graphics.clear();
    graphics.lineStyle(1, 0x4f6b88, 1);
    graphics.strokeRect(MINIMAP.x, MINIMAP.y, MINIMAP.width, MINIMAP.height);

    for (const agent of this.currentSnapshot?.agents ?? []) {
      if (!agent.position) {
        continue;
      }
      const dotX = MINIMAP.x + (agent.position.tile_x / gridWidth) * MINIMAP.width;
      const dotY = MINIMAP.y + (agent.position.tile_y / gridHeight) * MINIMAP.height;
      graphics.fillStyle(agent.agent_id === this.selectedAgentId ? 0xf8fafc : 0x8b7cf6, 1);
      graphics.fillCircle(dotX, dotY, agent.agent_id === this.selectedAgentId ? 4 : 3);
    }

    const viewX = ((this.cameras.main.worldView.x - 64) / (gridWidth * 24)) * MINIMAP.width;
    const viewY = ((this.cameras.main.worldView.y - 80) / (gridHeight * 24)) * MINIMAP.height;
    const viewWidth = (this.cameras.main.worldView.width / (gridWidth * 24)) * MINIMAP.width;
    const viewHeight = (this.cameras.main.worldView.height / (gridHeight * 24)) * MINIMAP.height;

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
      arc.update(
        64 + source.position.tile_x * 24,
        80 + source.position.tile_y * 24,
        64 + target.position.tile_x * 24,
        80 + target.position.tile_y * 24,
      );
      this.arcs.push(arc);
    }
  }
}
