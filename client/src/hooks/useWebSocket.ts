import { useEffect, useRef, useState } from "react";

import type { SocketMessage } from "../types/world";

interface UseWebSocketOptions {
  url: string | null;
  onMessage?: (message: SocketMessage) => void;
}

export function useWebSocket({ url, onMessage }: UseWebSocketOptions) {
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const [status, setStatus] = useState<"idle" | "connecting" | "open" | "closed">("idle");

  useEffect(() => {
    let cancelled = false;

    if (!url) {
      setStatus("idle");
      return;
    }

    const connect = () => {
      if (cancelled) {
        return;
      }
      setStatus("connecting");
      const socket = new WebSocket(url);
      socketRef.current = socket;

      socket.onopen = () => {
        if (!cancelled) {
          setStatus("open");
        }
      };
      socket.onmessage = (event) => {
        const message = JSON.parse(event.data) as SocketMessage;
        onMessage?.(message);
      };
      socket.onclose = () => {
        if (cancelled) {
          return;
        }
        setStatus("closed");
        reconnectTimerRef.current = window.setTimeout(connect, 1000);
      };
      socket.onerror = () => {
        socket.close();
      };
    };

    connect();

    return () => {
      cancelled = true;
      if (reconnectTimerRef.current !== null) {
        window.clearTimeout(reconnectTimerRef.current);
      }
      socketRef.current?.close();
    };
  }, [onMessage, url]);

  const sendJson = (payload: Record<string, unknown>) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(payload));
    }
  };

  return { status, sendJson };
}
