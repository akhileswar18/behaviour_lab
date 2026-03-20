import Phaser from "phaser";

import { SpeechBubble } from "../ui/SpeechBubble";
import { ThoughtCloud } from "../ui/ThoughtCloud";
import type { AgentSnapshot, TilePosition } from "../../types/world";

export class AgentSprite {
  private readonly marker: Phaser.GameObjects.Arc;
  private readonly label: Phaser.GameObjects.Text;
  private readonly speechBubble: SpeechBubble;
  private readonly thoughtCloud: ThoughtCloud;

  constructor(
    private readonly scene: Phaser.Scene,
    agent: AgentSnapshot,
    onSelectAgent: (agentId: string) => void,
  ) {
    const initial = this.toWorld(agent.position ?? { tile_x: 2, tile_y: 2 });
    this.marker = this.scene.add.circle(initial.x, initial.y, 10, 0x7f77dd);
    this.label = this.scene.add.text(initial.x - 14, initial.y + 12, agent.name, {
      color: "#f8fafc",
      fontSize: "12px",
    });
    this.speechBubble = new SpeechBubble(this.scene, initial.x, initial.y - 30);
    this.thoughtCloud = new ThoughtCloud(this.scene, initial.x, initial.y - 48);
    this.marker.setInteractive({ useHandCursor: true }).on("pointerdown", () => {
      onSelectAgent(agent.agent_id);
    });
  }

  updateSnapshot(agent: AgentSnapshot, position: TilePosition, selected: boolean) {
    const world = this.toWorld(position);
    this.marker.setPosition(world.x, world.y);
    this.marker.setStrokeStyle(selected ? 3 : 0, 0xf8fafc);
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

  private toWorld(position: TilePosition) {
    return {
      x: 64 + position.tile_x * 24,
      y: 80 + position.tile_y * 24,
    };
  }
}
