/**
 * WebSocket 연결 관리 훅
 */

import { useEffect, useState, useCallback, useRef } from "react";
import { getWebSocketService, WebSocketService } from "../services/websocket";

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const wsRef = useRef<WebSocketService | null>(null);

  useEffect(() => {
    const ws = getWebSocketService();
    wsRef.current = ws;

    ws.connect()
      .then(() => setIsConnected(true))
      .catch((err) => setError(err));

    return () => {
      ws.disconnect();
    };
  }, []);

  const send = useCallback((message: unknown) => {
    wsRef.current?.send(message);
  }, []);

  const onMessage = useCallback((handler: (message: unknown) => void) => {
    return wsRef.current?.onMessage(handler) || (() => {});
  }, []);

  return {
    isConnected,
    error,
    send,
    onMessage,
  };
}
