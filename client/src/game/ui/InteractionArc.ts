import Phaser from "phaser";

export class InteractionArc {
  private readonly graphics: Phaser.GameObjects.Graphics;
  private readonly dashTween: Phaser.Tweens.Tween;
  private dashOffset = 0;
  private fromX = 0;
  private fromY = 0;
  private toX = 0;
  private toY = 0;

  constructor(scene: Phaser.Scene) {
    this.graphics = scene.add.graphics().setDepth(9);
    this.dashTween = scene.tweens.add({
      targets: this,
      dashOffset: 12,
      duration: 800,
      repeat: -1,
      ease: "Linear",
      onRepeat: () => {
        this.dashOffset = 0;
      },
      onUpdate: () => {
        this.drawDashedLine();
      },
    });
  }

  update(fromX: number, fromY: number, toX: number, toY: number) {
    this.fromX = fromX;
    this.fromY = fromY;
    this.toX = toX;
    this.toY = toY;
    this.drawDashedLine();
  }

  private drawDashedLine() {
    this.graphics.clear();
    this.graphics.lineStyle(2, 0xfbbf24, 0.75);

    const distance = Phaser.Math.Distance.Between(this.fromX, this.fromY, this.toX, this.toY);
    if (distance <= 1) {
      return;
    }
    const dashLength = 10;
    const gapLength = 7;
    const segment = dashLength + gapLength;
    const angle = Phaser.Math.Angle.Between(this.fromX, this.fromY, this.toX, this.toY);

    for (let cursor = -this.dashOffset; cursor < distance; cursor += segment) {
      const start = Math.max(cursor, 0);
      const end = Math.min(cursor + dashLength, distance);
      if (end <= 0 || start >= distance) {
        continue;
      }
      const startX = this.fromX + Math.cos(angle) * start;
      const startY = this.fromY + Math.sin(angle) * start;
      const endX = this.fromX + Math.cos(angle) * end;
      const endY = this.fromY + Math.sin(angle) * end;
      this.graphics.strokeLineShape(new Phaser.Geom.Line(startX, startY, endX, endY));
    }
  }

  destroy() {
    this.dashTween.stop();
    this.graphics.destroy();
  }
}
