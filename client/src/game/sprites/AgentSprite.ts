import Phaser from "phaser";

import { SpeechBubble } from "../ui/SpeechBubble";
import { ThoughtCloud } from "../ui/ThoughtCloud";
import type { AgentSnapshot, TilePosition } from "../../types/world";

export const AGENT_SPRITE_SCALE = 3;
export const AGENT_FRAME_SIZE = 16;
export const WORLD_TILE_SIZE = AGENT_FRAME_SIZE * AGENT_SPRITE_SCALE;
export const AGENT_SPRITE_KEYS = ["agent_1", "agent_2", "agent_3"] as const;

export type AgentSpriteKey = (typeof AGENT_SPRITE_KEYS)[number];
export type AgentFacing = "down" | "left" | "right" | "up";

export function tileToWorldPosition(position: TilePosition) {
  return {
    x: position.tile_x * WORLD_TILE_SIZE + WORLD_TILE_SIZE / 2,
    y: position.tile_y * WORLD_TILE_SIZE + WORLD_TILE_SIZE / 2,
  };
}

export class AgentSprite {
  private readonly marker: Phaser.GameObjects.Sprite | Phaser.GameObjects.Arc;
  private readonly label: Phaser.GameObjects.Text;
  private readonly speechBubble: SpeechBubble;
  private readonly thoughtCloud: ThoughtCloud;
  private readonly spriteKey: AgentSpriteKey;
  private facing: AgentFacing = "down";

  constructor(
    private readonly scene: Phaser.Scene,
    agent: AgentSnapshot,
    spriteKey: AgentSpriteKey,
    onSelectAgent: (agentId: string) => void,
  ) {
    this.spriteKey = spriteKey;
    const initial = tileToWorldPosition(agent.position ?? { tile_x: 2, tile_y: 2 });
    this.ensureAnimations();
    this.marker = this.createMarker(initial.x, initial.y);
    this.label = this.scene.add.text(initial.x - 14, initial.y + 12, agent.name, {
      color: "#f8fafc",
      fontSize: "12px",
    }).setDepth(11);
    this.speechBubble = new SpeechBubble(this.scene, initial.x, initial.y - 30);
    this.thoughtCloud = new ThoughtCloud(this.scene, initial.x, initial.y - 48);
    this.marker.setInteractive({ useHandCursor: true }).on("pointerdown", () => {
      onSelectAgent(agent.agent_id);
    });
  }

  updateSnapshot(
    agent: AgentSnapshot,
    position: TilePosition,
    selected: boolean,
    facing: AgentFacing = "down",
    moving = false,
  ) {
    const world = tileToWorldPosition(position);
    this.facing = facing;
    this.marker.setPosition(world.x, world.y);
    if ("setStrokeStyle" in this.marker) {
      this.marker.setStrokeStyle(selected ? 3 : 0, 0xf8fafc);
    }
    if ("play" in this.marker) {
      this.marker.play(this.animationKey(moving ? `walk-${facing}` : "idle"), true);
    }
    this.label.setPosition(world.x - 14, world.y + 12);
    this.label.setText(agent.name);
    this.speechBubble.update(world.x, world.y - 30, agent.speech?.content ?? "");
    this.thoughtCloud.update(world.x, world.y - 50, agent.thought?.content ?? "");
  }

  followTarget() {
    return this.marker;
  }

  destroy() {
    this.marker.destroy();
    this.label.destroy();
    this.speechBubble.destroy();
    this.thoughtCloud.destroy();
  }

  private createMarker(x: number, y: number) {
    if (!this.scene.textures.exists(this.spriteKey)) {
      return this.scene.add.circle(x, y, 12, 0x7f77dd).setDepth(10);
    }
    return this.scene.add
      .sprite(x, y, this.spriteKey, 0)
      .setScale(AGENT_SPRITE_SCALE)
      .setOrigin(0.5, 0.5)
      .setDepth(10);
  }

  private ensureAnimations() {
    if (!this.scene.textures.exists(this.spriteKey)) {
      return;
    }
    const animationSpecs: Array<{ suffix: "walk-down" | "walk-left" | "walk-right" | "walk-up"; row: number }> = [
      { suffix: "walk-down", row: 0 },
      { suffix: "walk-left", row: 1 },
      { suffix: "walk-right", row: 2 },
      { suffix: "walk-up", row: 3 },
    ];
    for (const spec of animationSpecs) {
      const key = this.animationKey(spec.suffix);
      if (this.scene.anims.exists(key)) {
        continue;
      }
      this.scene.anims.create({
        key,
        frames: this.scene.anims.generateFrameNumbers(this.spriteKey, {
          start: spec.row * 4,
          end: spec.row * 4 + 3,
        }),
        frameRate: 8,
        repeat: -1,
      });
    }
    const idleKey = this.animationKey("idle");
    if (!this.scene.anims.exists(idleKey)) {
      this.scene.anims.create({
        key: idleKey,
        frames: [{ key: this.spriteKey, frame: 0 }],
        frameRate: 1,
        repeat: -1,
      });
    }
  }

  private animationKey(suffix: "walk-down" | "walk-left" | "walk-right" | "walk-up" | "idle") {
    return `${this.spriteKey}-${suffix}`;
  }
}
