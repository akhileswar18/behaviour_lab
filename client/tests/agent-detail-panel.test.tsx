import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { AgentDetailPanel } from "../src/panels/AgentDetailPanel";
import type { SelectedAgentView } from "../src/hooks/useSimulationState";

function buildDetail(): SelectedAgentView {
  return {
    agent: {
      agent_id: "cyra",
      name: "Cyra",
      zone_name: "Shelter",
      position: { tile_x: 4, tile_y: 8 },
      mood: "guarded",
      action: "avoid",
      needs: { hunger: 0.53, safety_need: 0.45, social_need: 0.12 },
      recent_decisions: [],
    },
    needs: [
      { label: "Hunger", percent: 53, color: "#F39C12" },
      { label: "Safety", percent: 45, color: "#F39C12" },
      { label: "Social", percent: 12, color: "#27AE60" },
    ],
    goalLabel: "maintain_context",
    goalPriorityLabel: "0.40",
    decisionLog: [
      { tickNumber: 11, action: "avoid", rationale: "Keep distance from nearby peers." },
      { tickNumber: 10, action: "avoid", rationale: "Room pressure still high." },
    ],
    conversationFeed: [
      { tickNumber: 11, senderName: "Cyra", message: "Keeping my distance for now." },
    ],
  };
}

describe("AgentDetailPanel", () => {
  it("renders empty-state guidance when no agent is selected", () => {
    const html = renderToStaticMarkup(<AgentDetailPanel detail={null} />);
    expect(html).toContain("Agent Detail");
    expect(html).toContain("Select an agent in the world");
  });

  it("renders needs bars, goal card, decisions, and conversation feed", () => {
    const html = renderToStaticMarkup(<AgentDetailPanel detail={buildDetail()} />);

    expect(html).toContain("Cyra");
    expect(html).toContain("Hunger");
    expect(html).toContain("width:53%");
    expect(html).toContain("maintain_context");
    expect(html).toContain("Priority 0.40");
    expect(html).toContain("T11: avoid");
    expect(html).toContain("Cyra");
    expect(html).toContain("Keeping my distance for now.");
  });
});

