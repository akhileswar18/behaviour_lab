import { useCallback, useMemo, useState } from "react";

import type { AgentSnapshot, ConnectionAck, SocketMessage, WorldSnapshot } from "../types/world";
import { formatSpeechBubbleText, formatThoughtBubbleText } from "../game/ui/overlayText";

const RENDER_AGENT_SPRITE_KEYS = ["agent_1", "agent_2", "agent_3"] as const;
const MAX_DECISION_ROWS = 10;
const MAX_CONVERSATION_ROWS = 10;

export type RenderAgentSpriteKey = (typeof RENDER_AGENT_SPRITE_KEYS)[number];

export interface RenderAgentState {
  agent: AgentSnapshot;
  spriteKey: RenderAgentSpriteKey;
}

export interface NeedBarView {
  label: "Hunger" | "Safety" | "Social";
  percent: number;
  color: string;
}

export interface DecisionLogView {
  tickNumber: number;
  action: string;
  rationale: string;
}

export interface ConversationFeedView {
  tickNumber: number;
  senderName: string;
  message: string;
}

export interface SelectedAgentView {
  agent: AgentSnapshot;
  needs: NeedBarView[];
  goalLabel: string;
  goalPriorityLabel: string;
  decisionLog: DecisionLogView[];
  conversationFeed: ConversationFeedView[];
}

function asPercent(value: number): number {
  const normalized = value <= 1 ? value * 100 : value;
  return Math.max(0, Math.min(100, normalized));
}

function needColor(percent: number): string {
  if (percent <= 30) {
    return "#27AE60";
  }
  if (percent <= 60) {
    return "#F39C12";
  }
  return "#E74C3C";
}

function buildNeeds(agent: AgentSnapshot): NeedBarView[] {
  const hunger = asPercent(agent.needs.hunger);
  const safety = asPercent(agent.needs.safety_need);
  const social = asPercent(agent.needs.social_need);
  return [
    { label: "Hunger", percent: hunger, color: needColor(hunger) },
    { label: "Safety", percent: safety, color: needColor(safety) },
    { label: "Social", percent: social, color: needColor(social) },
  ];
}

function normalizeAgentOverlay(agent: AgentSnapshot): AgentSnapshot {
  return {
    ...agent,
    speech: agent.speech ? { ...agent.speech, content: formatSpeechBubbleText(agent.speech.content ?? "") } : null,
    thought: agent.thought ? { ...agent.thought, content: formatThoughtBubbleText(agent.thought.content ?? "") } : null,
    recent_decisions: [...agent.recent_decisions]
      .sort((left, right) => right.tick_number - left.tick_number)
      .slice(0, MAX_DECISION_ROWS),
  };
}

export function buildOverlayContent(payload: {
  speech?: { content?: string | null } | null;
  thought?: { content?: string | null } | null;
}) {
  return {
    speech: formatSpeechBubbleText(payload.speech?.content ?? ""),
    thought: formatThoughtBubbleText(payload.thought?.content ?? ""),
  };
}

export function buildSelectedAgentView(
  snapshot: WorldSnapshot | null,
  selectedAgentId: string | null,
): SelectedAgentView | null {
  if (!snapshot || !selectedAgentId) {
    return null;
  }
  const agent = snapshot.agents.find((item) => item.agent_id === selectedAgentId);
  if (!agent) {
    return null;
  }
  const normalizedAgent = normalizeAgentOverlay(agent);
  const namesById = new Map(snapshot.agents.map((item) => [item.agent_id, item.name]));
  const conversationFeed = snapshot.conversations
    .filter(
      (conversation) =>
        conversation.source_agent_id === selectedAgentId ||
        conversation.target_agent_id === selectedAgentId,
    )
    .slice(-MAX_CONVERSATION_ROWS)
    .reverse()
    .map((conversation) => ({
      tickNumber: snapshot.tick_number,
      senderName: namesById.get(conversation.source_agent_id) ?? conversation.source_agent_id,
      message: formatSpeechBubbleText(conversation.content ?? ""),
    }));

  return {
    agent: normalizedAgent,
    needs: buildNeeds(normalizedAgent),
    goalLabel: normalizedAgent.goal?.goal_type ?? "No active goal",
    goalPriorityLabel: normalizedAgent.goal ? normalizedAgent.goal.priority.toFixed(2) : "N/A",
    decisionLog: normalizedAgent.recent_decisions.map((decision) => ({
      tickNumber: decision.tick_number,
      action: decision.action,
      rationale: formatThoughtBubbleText(decision.rationale ?? ""),
    })),
    conversationFeed,
  };
}

export function buildRenderAgentState(
  snapshot: WorldSnapshot | null,
  selectedAgentId: string | null,
): { renderAgents: RenderAgentState[]; selectedAgent: AgentSnapshot | null; selectedAgentView: SelectedAgentView | null } {
  if (!snapshot) {
    return { renderAgents: [], selectedAgent: null, selectedAgentView: null };
  }

  const orderedAgents = [...snapshot.agents].sort((left, right) =>
    left.agent_id.localeCompare(right.agent_id),
  );
  const renderAgents = orderedAgents.map((agent, index) => ({
    agent: normalizeAgentOverlay(agent),
    spriteKey: RENDER_AGENT_SPRITE_KEYS[index % RENDER_AGENT_SPRITE_KEYS.length],
  }));
  const selectedAgent =
    renderAgents.find((item) => item.agent.agent_id === selectedAgentId)?.agent ?? null;
  const selectedAgentView = buildSelectedAgentView(snapshot, selectedAgentId);

  return { renderAgents, selectedAgent, selectedAgentView };
}

export function useSimulationState() {
  const [ack, setAck] = useState<ConnectionAck | null>(null);
  const [snapshot, setSnapshot] = useState<WorldSnapshot | null>(null);
  const [previousSnapshot, setPreviousSnapshot] = useState<WorldSnapshot | null>(null);
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

  const handleMessage = useCallback((message: SocketMessage) => {
    if (message.type === "connection_ack") {
      setAck(message);
      return;
    }
    setSnapshot((current) => {
      setPreviousSnapshot(current);
      return message;
    });
  }, []);

  const renderState = useMemo(
    () => buildRenderAgentState(snapshot, selectedAgentId),
    [selectedAgentId, snapshot],
  );

  return {
    ack,
    snapshot,
    previousSnapshot,
    renderAgents: renderState.renderAgents,
    selectedAgent: renderState.selectedAgent,
    selectedAgentView: renderState.selectedAgentView,
    selectedAgentId,
    setSelectedAgentId,
    handleMessage,
  };
}
