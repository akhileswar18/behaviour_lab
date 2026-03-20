import type { AgentSnapshot } from "../types/world";

interface AgentDetailPanelProps {
  agent: AgentSnapshot | null;
}

function percentage(value: number | undefined): string {
  return `${Math.round((value ?? 0) * 100)}%`;
}

export function AgentDetailPanel({ agent }: AgentDetailPanelProps) {
  if (!agent) {
    return (
      <aside style={{ padding: 16 }}>
        <strong>Agent Detail</strong>
        <p>Select an agent in the world to inspect current needs and decisions.</p>
      </aside>
    );
  }

  return (
    <aside style={{ padding: 16, display: "grid", gap: 12 }}>
      <div>
        <strong>{agent.name}</strong>
        <div>
          {agent.zone_name ?? "Unknown zone"} · {agent.mood}
        </div>
      </div>
      <div>
        <strong>Needs</strong>
        <div>Hunger: {percentage(agent.needs.hunger)}</div>
        <div>Safety: {percentage(agent.needs.safety_need)}</div>
        <div>Social: {percentage(agent.needs.social_need)}</div>
      </div>
      <div>
        <strong>Goal</strong>
        <div>{agent.goal ? `${agent.goal.goal_type} (${agent.goal.priority.toFixed(2)})` : "None"}</div>
      </div>
      <div>
        <strong>Recent Decisions</strong>
        {agent.recent_decisions.length === 0 ? (
          <div>No decisions yet.</div>
        ) : (
          agent.recent_decisions.map((decision) => (
            <div key={`${decision.tick_number}-${decision.action}`}>
              T{decision.tick_number}: {decision.action}
            </div>
          ))
        )}
      </div>
      <div>
        <strong>Conversation</strong>
        <div>{agent.speech?.content ?? "No live speech bubble."}</div>
      </div>
    </aside>
  );
}
