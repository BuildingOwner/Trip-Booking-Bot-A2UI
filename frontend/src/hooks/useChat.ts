/**
 * 채팅 상태 관리 훅 (REST API 버전)
 */

import { useState, useCallback, useEffect, useRef } from "react";
import { getApiService } from "../services/api";
import { useA2UI } from "./useA2UI";
import type { ChatMessage, A2UIMessage, UserActionMessage, AssistantMessage } from "../types/a2ui";

// UUID 생성 함수 (crypto.randomUUID 폴백)
function generateUUID(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

// assistantMessage 타입 가드
function isAssistantMessage(msg: A2UIMessage): msg is AssistantMessage {
  return "assistantMessage" in msg;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const a2ui = useA2UI();
  const api = getApiService();
  const initializedRef = useRef(false);

  // 서버 응답 처리 (assistantMessage 추출 + A2UI 처리)
  const processServerMessages = useCallback((serverMessages: A2UIMessage[]) => {
    // assistantMessage 추출하여 채팅에 추가
    const assistantMessages = serverMessages.filter(isAssistantMessage);
    assistantMessages.forEach((msg) => {
      const chatMessage: ChatMessage = {
        id: generateUUID(),
        type: "agent",
        content: msg.assistantMessage,
        reasoning: msg.reasoning,  // GPT-5 thinking summary
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, chatMessage]);
    });

    // A2UI 메시지 처리 (assistantMessage 제외)
    const a2uiMessages = serverMessages.filter((msg) => !isAssistantMessage(msg));
    if (a2uiMessages.length > 0) {
      a2ui.processMessages(a2uiMessages);
    }
  }, [a2ui]);

  // 초기 UI 로드
  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;

    const loadInitialUI = async () => {
      setIsLoading(true);
      try {
        const response = await api.getInitialUI();
        if (response.success && response.data) {
          const data = response.data as { messages?: A2UIMessage[] };
          // 여러 메시지 처리
          if (data.messages && Array.isArray(data.messages)) {
            processServerMessages(data.messages);
          } else {
            // 단일 메시지 (하위 호환)
            a2ui.processMessage(response.data as A2UIMessage);
          }
        }
      } catch (error) {
        console.error("Failed to load initial UI:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialUI();
  }, [api, a2ui, processServerMessages]);

  // 텍스트 메시지 전송
  const sendMessage = useCallback(
    async (text: string) => {
      // 사용자 메시지 추가
      const userMessage: ChatMessage = {
        id: generateUUID(),
        type: "user",
        content: text,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      setIsLoading(true);
      try {
        const response = await api.sendMessage({ text });

        if (response.success && response.data) {
          const data = response.data as { messages?: A2UIMessage[] };

          // 여러 메시지 처리 (assistantMessage 포함)
          if (data.messages && Array.isArray(data.messages)) {
            processServerMessages(data.messages);
          }
        }
      } catch (error) {
        console.error("Failed to send message:", error);
      } finally {
        setIsLoading(false);
      }
    },
    [api, processServerMessages]
  );

  // userAction 전송
  const sendAction = useCallback(
    async (surfaceId: string, componentId: string, action: string, data?: Record<string, unknown>) => {
      const actionMessage: UserActionMessage = {
        userAction: {
          surfaceId,
          componentId,
          action,
          data,
        },
      };

      setIsLoading(true);
      try {
        const response = await api.sendMessage(actionMessage);

        if (response.success && response.data) {
          const responseData = response.data as { messages?: A2UIMessage[] };

          // 여러 메시지 처리 (assistantMessage 포함)
          if (responseData.messages && Array.isArray(responseData.messages)) {
            processServerMessages(responseData.messages);
          }
        }
      } catch (error) {
        console.error("Failed to send action:", error);
      } finally {
        setIsLoading(false);
      }
    },
    [api, processServerMessages]
  );

  return {
    messages,
    isLoading,
    sendMessage,
    sendAction,
    a2ui,
  };
}
