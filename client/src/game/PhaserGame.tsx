import Phaser from "phaser";
import { useEffect, useRef } from "react";

import { Preloader } from "./scenes/Preloader";
import { WorldScene } from "./scenes/WorldScene";
import type { WorldSnapshot } from "../types/world";

interface PhaserGameProps {
  baseUrl: string;
  scenarioId: string | null;
  snapshot: WorldSnapshot | null;
  previousSnapshot: WorldSnapshot | null;
  selectedAgentId: string | null;
  mode: "live" | "replay";
  followSelectedAgent: boolean;
  onSelectAgent: (agentId: string) => void;
}

export function PhaserGame({
  baseUrl,
  scenarioId,
  snapshot,
  previousSnapshot,
  selectedAgentId,
  mode,
  followSelectedAgent,
  onSelectAgent,
}: PhaserGameProps) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const gameRef = useRef<Phaser.Game | null>(null);
  const worldSceneRef = useRef<WorldScene | null>(null);

  useEffect(() => {
    if (!hostRef.current || gameRef.current) {
      return;
    }

    const worldScene = new WorldScene({ baseUrl, onSelectAgent });
    worldSceneRef.current = worldScene;
    gameRef.current = new Phaser.Game({
      type: Phaser.AUTO,
      parent: hostRef.current,
      width: 960,
      height: 640,
      backgroundColor: "#152235",
      pixelArt: true,
      scene: [new Preloader(baseUrl, scenarioId), worldScene],
    });

    return () => {
      gameRef.current?.destroy(true);
      gameRef.current = null;
      worldSceneRef.current = null;
    };
  }, [baseUrl, onSelectAgent, scenarioId]);

  useEffect(() => {
    worldSceneRef.current?.syncSnapshot(
      previousSnapshot,
      snapshot,
      selectedAgentId,
      mode,
      followSelectedAgent,
    );
  }, [followSelectedAgent, mode, previousSnapshot, selectedAgentId, snapshot]);

  return <div ref={hostRef} style={{ width: "100%", height: "100%" }} />;
}
