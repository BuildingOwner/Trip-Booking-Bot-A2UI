/**
 * 채팅 상태 관리 훅
 */

import { useState, useCallback, useEffect } from "react";
import { useWebSocket } from "./useWebSocket";
import type { ChatMessage, A2UIMessage, UserActionMessage } from "../types/a2ui";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const { isConnected, send, onMessage } = useWebSocket();

  // 메시지 수신 처리
  useEffect(() => {
    const unsubscribe = onMessage((message: unknown) => {
      const a2uiMessage = message as A2UIMessage;

      // A2UI 메시지를 채팅 메시지로 변환
      const chatMessage: ChatMessage = {
        id: crypto.randomUUID(),
        type: "ui",
        a2ui: a2uiMessage,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, chatMessage]);
    });

    return unsubscribe;
  }, [onMessage]);

  // 텍스트 메시지 전송
  const sendMessage = useCallback(
    (text: string) => {
      // 사용자 메시지 추가
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        type: "user",
        content: text,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // 서버로 전송
      send({ text });
    },
    [send]
  );

  // userAction 전송
  const sendAction = useCallback(
    (surfaceId: string, componentId: string, action: string, data?: Record<string, unknown>) => {
      const actionMessage: UserActionMessage = {
        userAction: {
          surfaceId,
          componentId,
          action,
          data,
        },
      };
      send(actionMessage);
    },
    [send]
  );

  return {
    messages,
    isConnected,
    sendMessage,
    sendAction,
  };
}
