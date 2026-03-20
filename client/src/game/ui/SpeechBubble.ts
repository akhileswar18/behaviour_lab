import Phaser from "phaser";

export class SpeechBubble {
  private readonly text: Phaser.GameObjects.Text;

  constructor(scene: Phaser.Scene, x: number, y: number) {
    this.text = scene.add.text(x, y, "", {
      color: "#ffe082",
      fontSize: "11px",
      backgroundColor: "#203040",
    });
  }

  update(x: number, y: number, content: string) {
    this.text.setPosition(x, y);
    this.text.setText(content);
    this.text.setVisible(Boolean(content));
  }

  destroy() {
    this.text.destroy();
  }
}
