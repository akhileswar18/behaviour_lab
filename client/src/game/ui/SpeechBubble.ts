import Phaser from "phaser";
import { formatSpeechBubbleText, formatThoughtBubbleText } from "./overlayText";

export { formatSpeechBubbleText, formatThoughtBubbleText };

export class SpeechBubble {
  private readonly bubble: Phaser.GameObjects.Graphics;
  private readonly text: Phaser.GameObjects.Text;
  private fadeTween: Phaser.Tweens.Tween | null = null;

  constructor(scene: Phaser.Scene, x: number, y: number) {
    this.bubble = scene.add.graphics().setDepth(12);
    this.text = scene.add.text(x, y, "", {
      color: "#1f2937",
      fontFamily: "Georgia, serif",
      fontSize: "12px",
      align: "center",
      wordWrap: { width: 180 },
    }).setDepth(13);
  }

  update(x: number, y: number, content: string) {
    const displayText = formatSpeechBubbleText(content);
    if (!displayText) {
      this.bubble.setVisible(false);
      this.text.setVisible(false);
      return;
    }

    this.fadeTween?.stop();
    this.bubble.clear();
    this.bubble.setVisible(true).setAlpha(1);
    this.text.setVisible(true).setAlpha(1);
    this.text.setText(displayText);

    const textWidth = Math.min(this.text.width + 16, 196);
    const textHeight = this.text.height + 10;
    const bubbleX = x - textWidth / 2;
    const bubbleY = y - textHeight - 24;

    this.text.setPosition(bubbleX + 8, bubbleY + 5);
    this.bubble.fillStyle(0xffffff, 0.95);
    this.bubble.lineStyle(1.5, 0x1f2937, 0.35);
    this.bubble.fillRoundedRect(bubbleX, bubbleY, textWidth, textHeight, 8);
    this.bubble.strokeRoundedRect(bubbleX, bubbleY, textWidth, textHeight, 8);
    this.bubble.fillTriangle(x - 6, bubbleY + textHeight, x + 6, bubbleY + textHeight, x, bubbleY + textHeight + 8);

    this.fadeTween = this.text.scene.tweens.add({
      targets: [this.text, this.bubble],
      alpha: 0,
      delay: 4000,
      duration: 420,
      onComplete: () => {
        this.text.setVisible(false);
        this.bubble.setVisible(false);
      },
    });
  }

  destroy() {
    this.fadeTween?.stop();
    this.bubble.destroy();
    this.text.destroy();
  }
}
