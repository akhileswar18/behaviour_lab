import { describe, expect, it } from "vitest";

import { useSimulationState } from "../src/hooks/useSimulationState";

describe("useSimulationState", () => {
  it("exports a hook", () => {
    expect(typeof useSimulationState).toBe("function");
  });
});
