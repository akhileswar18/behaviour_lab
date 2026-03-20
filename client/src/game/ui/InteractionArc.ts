import Phaser from "phaser";

export class InteractionArc {
  private readonly graphics: Phaser.GameObjects.Graphics;

  constructor(scene: Phaser.Scene) {
    this.graphics = scene.add.graphics();
  }

  update(fromX: number, fromY: number, toX: number, toY: number) {
    this.graphics.clear();
    this.graphics.lineStyle(2, 0xfbbf24, 0.7);
    this.graphics.strokeLineShape(new Phaser.Geom.Line(fromX, fromY, toX, toY));
  }

  destroy() {
    this.graphics.destroy();
  }
}
