import React, { act } from "react";
import ReactDOM from "react-dom/client";
import { afterEach, describe, expect, it, vi } from "vitest";

import { TimelineBar } from "../src/panels/TimelineBar";

describe("TimelineBar", () => {
  let container: HTMLDivElement;
  let root: ReactDOM.Root;

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    container.remove();
  });

  it("renders replay controls and forwards speed, scrub, and camera actions", () => {
    (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
    const onLoadReplay = vi.fn();
    const onTogglePlayback = vi.fn();
    const onResumeLive = vi.fn();
    const onSetPlaybackSpeed = vi.fn();
    const onScrub = vi.fn();
    const onToggleFollowSelectedAgent = vi.fn();

    container = document.createElement("div");
    document.body.appendChild(container);
    root = ReactDOM.createRoot(container);

    act(() => {
      root.render(
        React.createElement(TimelineBar, {
          currentTick: 2,
          liveTickNumber: 5,
          mode: "replay",
          replayTicks: [1, 2, 3, 4, 5],
          isLoading: false,
          isPlaying: false,
          playbackSpeed: 2,
          followSelectedAgent: false,
          hasSelection: true,
          onLoadReplay,
          onTogglePlayback,
          onResumeLive,
          onSetPlaybackSpeed,
          onScrub,
          onToggleFollowSelectedAgent,
        }),
      );
    });

    const buttons = Array.from(container.querySelectorAll("button"));
    const range = container.querySelector('input[type="range"]') as HTMLInputElement;

    const loadReplayButton = buttons.find((button) => button.textContent?.includes("Load Replay"));
    const playButton = buttons.find((button) => button.textContent === "Play");
    const liveButton = buttons.find((button) => button.textContent === "Back To Live");
    const speedButton = buttons.find((button) => button.textContent === "5x");
    const followButton = buttons.find((button) => button.textContent === "Follow Selected");

    expect(loadReplayButton).toBeTruthy();
    expect(playButton).toBeTruthy();
    expect(liveButton).toBeTruthy();
    expect(speedButton).toBeTruthy();
    expect(followButton).toBeTruthy();
    expect(range.value).toBe("1");

    loadReplayButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    playButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    liveButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    speedButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    followButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    range.value = "3";
    range.dispatchEvent(new Event("input", { bubbles: true }));

    expect(onLoadReplay).toHaveBeenCalledOnce();
    expect(onTogglePlayback).toHaveBeenCalledOnce();
    expect(onResumeLive).toHaveBeenCalledOnce();
    expect(onSetPlaybackSpeed).toHaveBeenCalledWith(5);
    expect(onToggleFollowSelectedAgent).toHaveBeenCalledOnce();
    expect(onScrub).toHaveBeenCalledWith(3);
  });
});
