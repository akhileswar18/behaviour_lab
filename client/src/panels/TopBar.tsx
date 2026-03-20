interface TopBarProps {
  tickNumber: number;
  status: string;
  mode: "live" | "replay";
  playbackSpeed: number;
  selectedAgentName?: string | null;
}

export function TopBar({ tickNumber, status, mode, playbackSpeed, selectedAgentName }: TopBarProps) {
  return (
    <header
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "12px 16px",
        borderBottom: "1px solid #243041",
        background: "#0d1622",
      }}
    >
      <strong>AI Colony Embodied World</strong>
      <span>Tick: {tickNumber}</span>
      <span>Mode: {mode === "replay" ? `replay ${playbackSpeed}x` : "live"}</span>
      <span>Status: {status}</span>
      <span>Selected: {selectedAgentName ?? "none"}</span>
    </header>
  );
}
