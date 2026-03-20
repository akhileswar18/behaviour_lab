import type { PlaybackSpeed } from "../types/world";

interface TimelineBarProps {
  currentTick: number;
  liveTickNumber: number;
  mode: "live" | "replay";
  replayTicks: number[];
  isLoading: boolean;
  isPlaying: boolean;
  playbackSpeed: PlaybackSpeed;
  followSelectedAgent: boolean;
  hasSelection: boolean;
  onLoadReplay: () => void;
  onTogglePlayback: () => void;
  onResumeLive: () => void;
  onSetPlaybackSpeed: (speed: PlaybackSpeed) => void;
  onScrub: (index: number) => void;
  onToggleFollowSelectedAgent: () => void;
}

const SPEED_OPTIONS: PlaybackSpeed[] = [1, 2, 5];

export function TimelineBar({
  currentTick,
  liveTickNumber,
  mode,
  replayTicks,
  isLoading,
  isPlaying,
  playbackSpeed,
  followSelectedAgent,
  hasSelection,
  onLoadReplay,
  onTogglePlayback,
  onResumeLive,
  onSetPlaybackSpeed,
  onScrub,
  onToggleFollowSelectedAgent,
}: TimelineBarProps) {
  const sliderValue = Math.max(
    0,
    replayTicks.findIndex((tick) => tick === currentTick),
  );

  return (
    <footer
      style={{
        padding: "12px 16px",
        borderTop: "1px solid #243041",
        background: "#101b29",
        display: "grid",
        gap: 10,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: 12,
          flexWrap: "wrap",
        }}
      >
        <div>
          <strong>{mode === "replay" ? "Replay timeline" : "Live timeline"}</strong>
          <div style={{ color: "#9fb3c8", fontSize: 13 }}>
            Current tick: {currentTick} | Live tick: {liveTickNumber}
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button type="button" onClick={onLoadReplay} disabled={isLoading || liveTickNumber < 1}>
            {isLoading ? "Loading..." : "Load Replay"}
          </button>
          <button type="button" onClick={onTogglePlayback} disabled={replayTicks.length === 0}>
            {isPlaying ? "Pause" : "Play"}
          </button>
          <button type="button" onClick={onResumeLive} disabled={mode === "live"}>
            Back To Live
          </button>
          <button
            type="button"
            onClick={onToggleFollowSelectedAgent}
            disabled={!hasSelection || replayTicks.length === 0}
          >
            {followSelectedAgent ? "Free Camera" : "Follow Selected"}
          </button>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(0, 1fr) auto",
          gap: 12,
          alignItems: "center",
        }}
      >
        <div style={{ display: "grid", gap: 6 }}>
          <input
            aria-label="Replay tick scrubber"
            type="range"
            min={0}
            max={Math.max(replayTicks.length - 1, 0)}
            value={sliderValue}
            disabled={replayTicks.length === 0}
            onInput={(event) => onScrub(Number(event.currentTarget.value))}
          />
          <div style={{ color: "#9fb3c8", fontSize: 13 }}>
            {replayTicks.length === 0
              ? "Run ticks to unlock replay and scrubbing."
              : `Scrubbed tick: ${currentTick}`}
          </div>
        </div>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {SPEED_OPTIONS.map((speed) => (
            <button
              key={speed}
              type="button"
              onClick={() => onSetPlaybackSpeed(speed)}
              style={{
                fontWeight: playbackSpeed === speed ? 700 : 400,
              }}
            >
              {speed}x
            </button>
          ))}
        </div>
      </div>
    </footer>
  );
}
