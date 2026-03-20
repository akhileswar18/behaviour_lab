import Phaser from "phaser";

export class Preloader extends Phaser.Scene {
  constructor(
    private readonly baseUrl: string,
    private readonly scenarioId: string | null,
  ) {
    super("Preloader");
  }

  preload() {
    const query = this.scenarioId ? `?scenario_id=${this.scenarioId}` : "";
    this.load.json("world-map", `${this.baseUrl}/api/world/map${query}`);
  }

  create() {
    this.scene.start("WorldScene");
  }
}
