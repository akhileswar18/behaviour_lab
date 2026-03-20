import { describe, expect, it } from "vitest";

import {
  buildSelectedAgentView,
  buildOverlayContent,
  buildRenderAgentState,
  useSimulationState,
} from "../src/hooks/useSimulationState";
import type { WorldSnapshot } from "../src/types/world";

function createSnapshot(agentIds: string[]): WorldSnapshot {
  return {
    schema_version: "1.0",
    type: "tick_update",
    scenario_id: "scenario-1",
    tick_number: 1,
    sim_time: "08:00",
    time_of_day: "0.5",
    conversations: [],
    world_events: [],
    agents: agentIds.map((agentId, index) => ({
      agent_id: agentId,
      name: agentId,
      zone_name: "commons",
      position: { tile_x: index + 1, tile_y: index + 2 },
      mood: "calm",
      action: "idle",
      needs: { hunger: 10, safety_need: 20, social_need: 30 },
      recent_decisions: [],
    })),
  };
}

describe("useSimulationState", () => {
  it("exports a hook", () => {
    expect(typeof useSimulationState).toBe("function");
  });

  it("builds a stable render-agent ordering independent of snapshot order", () => {
    const first = buildRenderAgentState(createSnapshot(["cyra", "bryn", "arya"]), null);
    const second = buildRenderAgentState(createSnapshot(["arya", "cyra", "bryn"]), null);

    expect(first.renderAgents.map((item) => [item.agent.agent_id, item.spriteKey])).toEqual([
      ["arya", "agent_1"],
      ["bryn", "agent_2"],
      ["cyra", "agent_3"],
    ]);
    expect(second.renderAgents.map((item) => [item.agent.agent_id, item.spriteKey])).toEqual([
      ["arya", "agent_1"],
      ["bryn", "agent_2"],
      ["cyra", "agent_3"],
    ]);
  });

  it("maps the selected agent from render state by identity", () => {
    const renderState = buildRenderAgentState(
      createSnapshot(["cyra", "bryn", "arya"]),
      "bryn",
    );

    expect(renderState.selectedAgent?.agent_id).toBe("bryn");
    expect(renderState.selectedAgent?.name).toBe("bryn");
  });

  it("prefers concise rationale text over raw debug-heavy speech when available", () => {
    expect(
      buildOverlayContent({
        speech: {
          content: "Cyra avoids nearby peers in Storage with risk=0.28 and pressure=0.00.",
        },
        thought: {
          content: "Maintain distance while the room settles.",
        },
      }),
    ).toEqual({
      speech: "Cyra avoids nearby peers in Storage...",
      thought: "Maintain distance while the room settles.",
    });
  });

  it("builds selected-agent view with ordered needs, max 10 decisions, and recent conversation rows", () => {
    const snapshot = createSnapshot(["cyra", "bryn", "arya"]);
    snapshot.tick_number = 9;
    snapshot.agents[0].recent_decisions = Array.from({ length: 12 }, (_, index) => ({
      tick_number: index + 1,
      action: `action_${index + 1}`,
      rationale: `rationale_${index + 1}`,
    }));
    snapshot.conversations = [
      {
        source_agent_id: "cyra",
        target_agent_id: "bryn",
        intent: "chat",
        tone: "warm",
        content: "Checking in with Bryn about dinner plans.",
      },
      {
        source_agent_id: "arya",
        target_agent_id: "cyra",
        intent: "share",
        tone: "neutral",
        content: "A long world update that should be clipped before feed rendering because it is too verbose.",
      },
    ];

    const detail = buildSelectedAgentView(snapshot, "cyra");
    expect(detail?.needs.map((item) => item.label)).toEqual(["Hunger", "Safety", "Social"]);
    expect(detail?.decisionLog).toHaveLength(10);
    expect(detail?.decisionLog[0].tickNumber).toBe(12);
    expect(detail?.conversationFeed).toHaveLength(2);
    expect(detail?.conversationFeed[0].senderName).toBe("arya");
    expect(detail?.conversationFeed[0].message.endsWith("...")).toBe(true);
  });
});
