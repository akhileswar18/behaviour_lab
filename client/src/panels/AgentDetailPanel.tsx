import type { SelectedAgentView } from "../hooks/useSimulationState";

interface AgentDetailPanelProps {
  detail: SelectedAgentView | null;
}

function percentage(value: number): string {
  return `${Math.round(value)}%`;
}

export function AgentDetailPanel({ detail }: AgentDetailPanelProps) {
  if (!detail) {
    return (
      <aside style={{ padding: 16, color: "#dbe7ff" }}>
        <strong style={{ fontSize: 20 }}>Agent Detail</strong>
        <p style={{ color: "#b6c6e3" }}>Select an agent in the world to inspect current needs and decisions.</p>
      </aside>
    );
  }
  const { agent } = detail;

  return (
    <aside
      style={{
        padding: 16,
        display: "grid",
        gap: 12,
        background: "linear-gradient(180deg, #081326 0%, #060d1a 100%)",
        color: "#ecf3ff",
        borderLeft: "1px solid #1f2d47",
      }}
    >
      <div
        style={{
          border: "1px solid #2a3a5c",
          borderRadius: 12,
          padding: 12,
          background: "rgba(18, 31, 54, 0.65)",
        }}
      >
        <strong style={{ fontSize: 20 }}>{agent.name}</strong>
        <div style={{ color: "#9fb4d8", marginTop: 4 }}>
          {agent.zone_name ?? "Unknown zone"} · {agent.mood} · {agent.action}
        </div>
      </div>
      <div>
        <strong>Needs</strong>
        <div style={{ display: "grid", gap: 8, marginTop: 8 }}>
          {detail.needs.map((need) => (
            <div key={need.label}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, color: "#c5d6f5" }}>
                <span>{need.label}</span>
                <span>{percentage(need.percent)}</span>
              </div>
              <div style={{ height: 10, borderRadius: 999, background: "#0b172c", border: "1px solid #2a3a5c" }}>
                <div
                  style={{
                    width: `${need.percent}%`,
                    height: "100%",
                    borderRadius: 999,
                    background: need.color,
                    transition: "width 0.5s ease-out",
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
      <div style={{ border: "1px solid #2a3a5c", borderRadius: 12, padding: 10, background: "rgba(15, 27, 48, 0.68)" }}>
        <strong>Goal</strong>
        <div style={{ marginTop: 6 }}>{detail.goalLabel}</div>
        <div style={{ color: "#9fb4d8", marginTop: 2 }}>Priority {detail.goalPriorityLabel}</div>
      </div>
      <div>
        <strong>Recent Decisions</strong>
        {detail.decisionLog.length === 0 ? (
          <div style={{ color: "#9fb4d8", marginTop: 6 }}>No decisions yet.</div>
        ) : (
          <div
            style={{
              marginTop: 8,
              maxHeight: 200,
              overflowY: "auto",
              display: "grid",
              gap: 8,
              paddingRight: 4,
            }}
          >
            {detail.decisionLog.map((decision) => (
              <div
                key={`${decision.tickNumber}-${decision.action}`}
                style={{
                  border: "1px solid #2a3a5c",
                  borderRadius: 10,
                  padding: "8px 10px",
                  background: "rgba(13, 24, 43, 0.85)",
                }}
              >
                <div style={{ fontWeight: 700 }}>
                  T{decision.tickNumber}: {decision.action}
                </div>
                <div style={{ color: "#aac0e4", fontSize: 12 }}>{decision.rationale}</div>
              </div>
            ))}
          </div>
        )}
      </div>
      <div>
        <strong>Conversation</strong>
        {detail.conversationFeed.length === 0 ? (
          <div style={{ color: "#9fb4d8", marginTop: 6 }}>No live messages yet.</div>
        ) : (
          <div
            style={{
              marginTop: 8,
              maxHeight: 170,
              overflowY: "auto",
              display: "grid",
              gap: 8,
              paddingRight: 4,
            }}
          >
            {detail.conversationFeed.map((entry, index) => (
              <div key={`${entry.tickNumber}-${entry.senderName}-${index}`} style={{ fontSize: 13 }}>
                <div style={{ color: "#a8bbdc" }}>
                  T{entry.tickNumber} · {entry.senderName}
                </div>
                <div>{entry.message}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
