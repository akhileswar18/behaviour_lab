import { useEffect, useState } from "react";

import type { PlaybackSpeed, ReplayResponse, WorldSnapshot } from "../types/world";

const PLAYBACK_INTERVAL_MS: Record<PlaybackSpeed, number> = {
  1: 900,
  2: 450,
  5: 180,
};

export function useReplay(baseUrl: string) {
  const [loading, setLoading] = useState(false);
  const [replay, setReplay] = useState<ReplayResponse | null>(null);
  const [mode, setMode] = useState<"live" | "replay">("live");
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<PlaybackSpeed>(1);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [followSelectedAgent, setFollowSelectedAgent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadReplay = async (
    scenarioId: string,
    tickStart: number,
    tickEnd: number,
    options?: { autoPlay?: boolean },
  ) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${baseUrl}/api/world/replay/${tickStart}/${tickEnd}?scenario_id=${scenarioId}`,
      );
      if (!response.ok) {
        throw new Error(`Replay request failed with status ${response.status}`);
      }
      const payload = (await response.json()) as ReplayResponse;
      setReplay(payload);
      setMode("replay");
      setCurrentIndex(0);
      setIsPlaying(Boolean(options?.autoPlay && payload.snapshots.length > 1));
      return payload;
    } catch (caughtError) {
      const message =
        caughtError instanceof Error ? caughtError.message : "Replay request failed";
      setError(message);
      throw caughtError;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (mode !== "replay" || !isPlaying || !replay) {
      return;
    }
    if (currentIndex >= replay.snapshots.length - 1) {
      setIsPlaying(false);
      return;
    }

    const timer = window.setTimeout(() => {
      setCurrentIndex((index) => Math.min(index + 1, replay.snapshots.length - 1));
    }, PLAYBACK_INTERVAL_MS[playbackSpeed]);

    return () => {
      window.clearTimeout(timer);
    };
  }, [currentIndex, isPlaying, mode, playbackSpeed, replay]);

  const availableTicks = replay?.snapshots.map((snapshot) => snapshot.tick_number) ?? [];
  const currentSnapshot: WorldSnapshot | null =
    mode === "replay" ? replay?.snapshots[currentIndex] ?? null : null;
  const previousSnapshot: WorldSnapshot | null =
    mode === "replay" && replay && currentIndex > 0 ? replay.snapshots[currentIndex - 1] : null;

  const play = () => {
    if (!replay || replay.snapshots.length === 0) {
      return;
    }
    setMode("replay");
    if (replay.snapshots.length > 1) {
      setIsPlaying(true);
    }
  };

  const pause = () => {
    setIsPlaying(false);
  };

  const resumeLive = () => {
    setMode("live");
    setIsPlaying(false);
  };

  const scrubToIndex = (index: number) => {
    if (!replay || replay.snapshots.length === 0) {
      return;
    }
    const boundedIndex = Math.max(0, Math.min(index, replay.snapshots.length - 1));
    setMode("replay");
    setIsPlaying(false);
    setCurrentIndex(boundedIndex);
  };

  const scrubToTick = (tickNumber: number) => {
    const index = availableTicks.indexOf(tickNumber);
    if (index >= 0) {
      scrubToIndex(index);
    }
  };

  const toggleFollowSelectedAgent = () => {
    setFollowSelectedAgent((current) => !current);
  };

  return {
    availableTicks,
    currentIndex,
    currentSnapshot,
    currentTick: currentSnapshot?.tick_number ?? null,
    error,
    followSelectedAgent,
    isPlaying,
    loading,
    loadReplay,
    mode,
    pause,
    play,
    playbackSpeed,
    previousSnapshot,
    replay,
    resumeLive,
    scrubToIndex,
    scrubToTick,
    setPlaybackSpeed,
    setReplay,
    toggleFollowSelectedAgent,
  };
}
