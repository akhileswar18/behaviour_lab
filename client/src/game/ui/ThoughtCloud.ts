import Phaser from "phaser";
import { formatThoughtBubbleText } from "./overlayText";

export class ThoughtCloud {
  private readonly cloud: Phaser.GameObjects.Graphics;
  private readonly text: Phaser.GameObjects.Text;
  private fadeTween: Phaser.Tweens.Tween | null = null;

  constructor(scene: Phaser.Scene, x: number, y: number) {
    this.cloud = scene.add.graphics().setDepth(12);
    this.text = scene.add.text(x, y, "", {
      color: "#e2ecff",
      fontFamily: "Georgia, serif",
      fontSize: "11px",
      align: "center",
      wordWrap: { width: 164 },
    }).setDepth(13);
  }

  update(x: number, y: number, content: string) {
    const displayText = formatThoughtBubbleText(content);
    if (!displayText) {
      this.cloud.setVisible(false);
      this.text.setVisible(false);
      return;
    }

    this.fadeTween?.stop();
    this.cloud.clear();
    this.cloud.setVisible(true).setAlpha(1);
    this.text.setVisible(true).setAlpha(1);
    this.text.setText(displayText);

    const width = Math.min(this.text.width + 18, 180);
    const height = this.text.height + 12;
    const cloudX = x - width / 2;
    const cloudY = y - height - 36;

    this.text.setPosition(cloudX + 9, cloudY + 6);
    this.cloud.fillStyle(0x93c5fd, 0.2);
    this.cloud.lineStyle(1.5, 0xbfdbfe, 0.9);
    this.cloud.fillRoundedRect(cloudX, cloudY, width, height, 12);
    this.cloud.strokeRoundedRect(cloudX, cloudY, width, height, 12);
    this.cloud.fillCircle(x - 11, cloudY + height + 8, 4);
    this.cloud.fillCircle(x - 4, cloudY + height + 15, 3);
    this.cloud.fillCircle(x + 2, cloudY + height + 21, 2);

    this.fadeTween = this.text.scene.tweens.add({
      targets: [this.text, this.cloud],
      alpha: 0,
      delay: 4000,
      duration: 420,
      onComplete: () => {
        this.text.setVisible(false);
        this.cloud.setVisible(false);
      },
    });
  }

  destroy() {
    this.fadeTween?.stop();
    this.cloud.destroy();
    this.text.destroy();
  }
}
