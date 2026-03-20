import Phaser from "phaser";

const tints: Record<string, { background: number; overlay: number; alpha: number }> = {
  dawn: { background: 0x334b64, overlay: 0xf4b183, alpha: 0.08 },
  day: { background: 0x152235, overlay: 0x9ad1ff, alpha: 0.03 },
  evening: { background: 0x3b2745, overlay: 0xffb36a, alpha: 0.12 },
  night: { background: 0x161827, overlay: 0x203a6b, alpha: 0.18 },
};

export function applyDayNightTint(
  scene: Phaser.Scene,
  timeOfDay: string,
  overlay: Phaser.GameObjects.Rectangle | null,
) {
  const camera = scene.cameras.main;
  const tint = tints[timeOfDay] ?? tints.day;

  camera.setBackgroundColor(tint.background);
  if (overlay) {
    overlay.setFillStyle(tint.overlay, tint.alpha);
    overlay.setVisible(true);
  }
}
