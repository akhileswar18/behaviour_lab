import { useEffect, useMemo, useState } from "react";

import { PhaserGame } from "./game/PhaserGame";
import { useReplay } from "./hooks/useReplay";
import { useSimulationState } from "./hooks/useSimulationState";
import { useWebSocket } from "./hooks/useWebSocket";
import { AgentDetailPanel } from "./panels/AgentDetailPanel";
import { TimelineBar } from "./panels/TimelineBar";
import { TopBar } from "./panels/TopBar";
import type { PlaybackSpeed, ReplayResponse } from "./types/world";

export function App() {
  const simulation = useSimulationState();
  const {
    ack,
    handleMessage,
    previousSnapshot,
    selectedAgentId,
    setSelectedAgentId,
    snapshot,
  } = simulation;
  const baseUrl = useMemo(() => "http://127.0.0.1:8000", []);
  const replay = useReplay(baseUrl);
  const [scenarioId, setScenarioId] = useState<string | null>(null);
  const socketUrl = useMemo(
    () => (scenarioId ? `ws://127.0.0.1:8000/ws/simulation?scenario_id=${scenarioId}` : null),
    [scenarioId],
  );
  const { status, sendJson } = useWebSocket({ url: socketUrl, onMessage: handleMessage });

  const liveTickNumber = snapshot?.tick_number ?? ack?.current_tick ?? 0;
  const visibleSnapshot = replay.mode === "replay" ? replay.currentSnapshot : snapshot;
  const visiblePreviousSnapshot =
    replay.mode === "replay" ? replay.previousSnapshot : previousSnapshot;
  const visibleTickNumber = visibleSnapshot?.tick_number ?? liveTickNumber;
  const visibleSelectedAgent = useMemo(
    () =>
      visibleSnapshot?.agents.find((agent) => agent.agent_id === selectedAgentId) ?? null,
    [selectedAgentId, visibleSnapshot],
  );

  useEffect(() => {
    let active = true;

    const bootstrapScenario = async () => {
      const response = await fetch(`${baseUrl}/scenarios`);
      const scenarios = (await response.json()) as Array<{ id: string }>;
      if (!active || scenarios.length === 0) {
        return;
      }
      setScenarioId((current) => current ?? scenarios[0].id);
    };

    void bootstrapScenario();
    return () => {
      active = false;
    };
  }, [baseUrl]);

  useEffect(() => {
    let active = true;
    if (!scenarioId || snapshot || (ack?.current_tick ?? 0) <= 0) {
      return;
    }

    const bootstrapSnapshot = async () => {
      const latestTick = ack?.current_tick ?? 0;
      const response = await fetch(
        `${baseUrl}/api/world/replay/${latestTick}/${latestTick}?scenario_id=${scenarioId}`,
      );
      if (!response.ok) {
        return;
      }
      const payload = (await response.json()) as ReplayResponse;
      if (!active) {
        return;
      }
      const initialSnapshot = payload.snapshots[0];
      if (initialSnapshot) {
        handleMessage(initialSnapshot);
      }
    };

    void bootstrapSnapshot();
    return () => {
      active = false;
    };
  }, [ack?.current_tick, baseUrl, handleMessage, scenarioId, snapshot]);

  const loadReplayRange = async (autoPlay = false) => {
    if (!scenarioId || liveTickNumber < 1) {
      return;
    }
    await replay.loadReplay(scenarioId, 1, liveTickNumber, { autoPlay });
    sendJson({
      schema_version: "1.0",
      type: "replay_request",
      tick_start: 1,
      tick_end: liveTickNumber,
      speed: replay.playbackSpeed,
    });
  };

  const handleTogglePlayback = async () => {
    if (replay.mode !== "replay" && !replay.replay) {
      await loadReplayRange(true);
      sendJson({ schema_version: "1.0", type: "sim_control", command: "play", speed: replay.playbackSpeed });
      return;
    }
    if (replay.mode !== "replay") {
      replay.play();
      sendJson({ schema_version: "1.0", type: "sim_control", command: "play", speed: replay.playbackSpeed });
      return;
    }
    if (replay.isPlaying) {
      replay.pause();
      sendJson({ schema_version: "1.0", type: "sim_control", command: "pause", speed: replay.playbackSpeed });
      return;
    }
    replay.play();
    sendJson({ schema_version: "1.0", type: "sim_control", command: "play", speed: replay.playbackSpeed });
  };

  const handlePlaybackSpeed = (speed: PlaybackSpeed) => {
    replay.setPlaybackSpeed(speed);
    sendJson({ schema_version: "1.0", type: "sim_control", command: "set_speed", speed });
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#08111c",
        color: "#edf2f7",
        display: "grid",
        gridTemplateRows: "auto 1fr auto",
      }}
    >
      <TopBar
        tickNumber={visibleTickNumber}
        status={status}
        mode={replay.mode}
        playbackSpeed={replay.playbackSpeed}
        selectedAgentName={visibleSelectedAgent?.name ?? null}
      />
      <main style={{ display: "grid", gridTemplateColumns: "minmax(0, 2fr) minmax(280px, 360px)" }}>
        <PhaserGame
          baseUrl={baseUrl}
          scenarioId={scenarioId}
          snapshot={visibleSnapshot}
          previousSnapshot={visiblePreviousSnapshot}
          selectedAgentId={selectedAgentId}
          mode={replay.mode}
          followSelectedAgent={replay.followSelectedAgent}
          onSelectAgent={(agentId) => {
            setSelectedAgentId(agentId);
            sendJson({ schema_version: "1.0", type: "agent_selected", agent_id: agentId });
          }}
        />
        <AgentDetailPanel agent={visibleSelectedAgent} />
      </main>
      <TimelineBar
        currentTick={visibleTickNumber}
        liveTickNumber={liveTickNumber}
        mode={replay.mode}
        replayTicks={replay.availableTicks}
        isLoading={replay.loading}
        isPlaying={replay.isPlaying}
        playbackSpeed={replay.playbackSpeed}
        followSelectedAgent={replay.followSelectedAgent}
        hasSelection={Boolean(selectedAgentId)}
        onLoadReplay={() => {
          void loadReplayRange(false);
        }}
        onTogglePlayback={() => {
          void handleTogglePlayback();
        }}
        onResumeLive={replay.resumeLive}
        onSetPlaybackSpeed={handlePlaybackSpeed}
        onScrub={replay.scrubToIndex}
        onToggleFollowSelectedAgent={replay.toggleFollowSelectedAgent}
      />
    </div>
  );
}
