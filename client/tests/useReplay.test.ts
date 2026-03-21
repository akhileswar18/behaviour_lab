import React, { act, useEffect } from "react";
import ReactDOM from "react-dom/client";
import { afterEach, describe, expect, it, vi } from "vitest";

import { useReplay } from "../src/hooks/useReplay";
import type { ReplayResponse } from "../src/types/world";

function makeReplayResponse(): ReplayResponse {
  return {
    scenario_id: "scenario-1",
    tick_start: 1,
    tick_end: 3,
    snapshots: [
      {
        schema_version: "1.0",
        type: "tick_update",
        scenario_id: "scenario-1",
        tick_number: 1,
        sim_time: "2026-03-19T20:15:00Z",
        time_of_day: "dawn",
        agents: [],
        conversations: [],
        world_events: [],
      },
      {
        schema_version: "1.0",
        type: "tick_update",
        scenario_id: "scenario-1",
        tick_number: 2,
        sim_time: "2026-03-19T20:16:00Z",
        time_of_day: "day",
        agents: [],
        conversations: [],
        world_events: [],
      },
      {
        schema_version: "1.0",
        type: "tick_update",
        scenario_id: "scenario-1",
        tick_number: 3,
        sim_time: "2026-03-19T20:17:00Z",
        time_of_day: "evening",
        agents: [],
        conversations: [],
        world_events: [],
      },
    ],
  };
}

interface ReplayHarnessProps {
  baseUrl: string;
  onReady: (api: ReturnType<typeof useReplay>) => void;
}

function ReplayHarness({ baseUrl, onReady }: ReplayHarnessProps) {
  const api = useReplay(baseUrl);

  useEffect(() => {
    onReady(api);
  }, [api, onReady]);

  return null;
}

describe("useReplay", () => {
  let container: HTMLDivElement;
  let root: ReactDOM.Root;
  let currentApi: ReturnType<typeof useReplay> | null = null;

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    container.remove();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("loads replay, advances at the selected speed, and supports scrubbing", async () => {
    vi.useFakeTimers();
    (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
    const replay = makeReplayResponse();
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => replay,
    });
    vi.stubGlobal("fetch", fetchMock);

    container = document.createElement("div");
    document.body.appendChild(container);
    root = ReactDOM.createRoot(container);

    await act(async () => {
      root.render(
        React.createElement(ReplayHarness, {
          baseUrl: "http://127.0.0.1:8000",
          onReady: (api: ReturnType<typeof useReplay>) => {
            currentApi = api;
          },
        }),
      );
    });

    const api = () => currentApi as ReturnType<typeof useReplay>;

    await act(async () => {
      await api().loadReplay("scenario-1", 1, 3);
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/world/replay/1/3?scenario_id=scenario-1",
    );
    expect(api().mode).toBe("replay");
    expect(api().currentTick).toBe(1);
    expect(api().availableTicks).toEqual([1, 2, 3]);

    act(() => {
      api().setPlaybackSpeed(2);
      api().play();
    });

    expect(api().isPlaying).toBe(true);

    act(() => {
      vi.advanceTimersByTime(450);
    });
    expect(api().currentTick).toBe(2);

    act(() => {
      api().scrubToIndex(2);
    });
    expect(api().currentTick).toBe(3);
    expect(api().isPlaying).toBe(false);

    act(() => {
      api().toggleFollowSelectedAgent();
      api().resumeLive();
    });
    expect(api().followSelectedAgent).toBe(true);
    expect(api().mode).toBe("live");
  });

  it("tracks previous/current snapshots while playback advances at configured intervals", async () => {
    vi.useFakeTimers();
    (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
    const replay = makeReplayResponse();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => replay,
      }),
    );

    container = document.createElement("div");
    document.body.appendChild(container);
    root = ReactDOM.createRoot(container);

    await act(async () => {
      root.render(
        React.createElement(ReplayHarness, {
          baseUrl: "http://127.0.0.1:8000",
          onReady: (api: ReturnType<typeof useReplay>) => {
            currentApi = api;
          },
        }),
      );
    });

    const api = () => currentApi as ReturnType<typeof useReplay>;

    await act(async () => {
      await api().loadReplay("scenario-1", 1, 3);
    });

    expect(api().currentSnapshot?.tick_number).toBe(1);
    expect(api().previousSnapshot).toBeNull();

    act(() => {
      api().setPlaybackSpeed(5);
      api().play();
    });
    act(() => {
      vi.advanceTimersByTime(180);
    });
    expect(api().currentSnapshot?.tick_number).toBe(2);
    expect(api().previousSnapshot?.tick_number).toBe(1);

    act(() => {
      vi.advanceTimersByTime(180);
    });
    expect(api().currentSnapshot?.tick_number).toBe(3);
    expect(api().previousSnapshot?.tick_number).toBe(2);
    expect(api().isPlaying).toBe(false);

    act(() => {
      api().scrubToIndex(0);
    });
    expect(api().currentSnapshot?.tick_number).toBe(1);
    expect(api().previousSnapshot).toBeNull();
  });
});
