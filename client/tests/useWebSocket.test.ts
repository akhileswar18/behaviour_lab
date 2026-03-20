import { describe, expect, it } from "vitest";

import { useWebSocket } from "../src/hooks/useWebSocket";

describe("useWebSocket", () => {
  it("exports a hook", () => {
    expect(typeof useWebSocket).toBe("function");
  });
});
