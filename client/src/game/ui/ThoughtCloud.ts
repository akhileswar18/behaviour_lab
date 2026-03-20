import Phaser from "phaser";

export class ThoughtCloud {
  private readonly text: Phaser.GameObjects.Text;

  constructor(scene: Phaser.Scene, x: number, y: number) {
    this.text = scene.add.text(x, y, "", {
      color: "#93c5fd",
      fontSize: "10px",
      backgroundColor: "#1b2736",
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
