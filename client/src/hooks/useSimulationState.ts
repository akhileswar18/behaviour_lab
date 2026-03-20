import { useCallback, useMemo, useState } from "react";

import type { AgentSnapshot, ConnectionAck, SocketMessage, WorldSnapshot } from "../types/world";

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

  const selectedAgent = useMemo<AgentSnapshot | null>(() => {
    if (!snapshot || !selectedAgentId) {
      return null;
    }
    return snapshot.agents.find((agent) => agent.agent_id === selectedAgentId) ?? null;
  }, [selectedAgentId, snapshot]);

  return {
    ack,
    snapshot,
    previousSnapshot,
    selectedAgent,
    selectedAgentId,
    setSelectedAgentId,
    handleMessage,
  };
}
