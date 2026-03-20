import { describe, expect, it } from "vitest";

import {
  formatSpeechBubbleText,
  formatThoughtBubbleText,
} from "../src/game/ui/SpeechBubble";

describe("overlay bubble formatting", () => {
  it("cleans debug-heavy speech down to a short readable sentence", () => {
    expect(
      formatSpeechBubbleText(
        "Cyra avoids nearby peers in Storage with risk=0.28 and pressure=0.00. Extra debug tail.",
      ),
    ).toBe("Cyra avoids nearby peers in Storage...");
  });

  it("truncates long overlay text to 60 characters with an ellipsis", () => {
    expect(
      formatSpeechBubbleText(
        "This is a very long piece of dialogue that should be shortened before it reaches the in-world speech bubble renderer.",
      ),
    ).toBe("This is a very long piece of dialogue that should be shorte...");
  });

  it("formats thought text separately but with the same readability limits", () => {
    expect(
      formatThoughtBubbleText(
        "Maintain distance while I wait for the food route to clear and the room pressure to drop.",
      ),
    ).toBe("Maintain distance while I wait for the food route to clear...");
  });
});
