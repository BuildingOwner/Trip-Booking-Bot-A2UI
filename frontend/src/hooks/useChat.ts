/**
 * 채팅 상태 관리 훅 (Gemini 스타일 Thinking UI)
 */

import { useState, useCallback, useEffect, useRef } from "react";
import { getApiService, type StreamEvent } from "../services/api";
import { useA2UI } from "./useA2UI";
import type { ChatMessage, A2UIMessage, UserActionMessage, AssistantMessage } from "../types/a2ui";

// Gemini 스타일 스트리밍 상태
export interface StreamingState {
  isThinking: boolean;          // 생각 중인지 여부
  currentStatus: string;        // 현재 상태 텍스트 (동적으로 변함)
  thinkingLogs: string[];       // 사고 로그 배열 (아코디언에 표시)
  answerText: string;           // 답변 텍스트 (스트리밍 누적)
}

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

const initialStreamingState: StreamingState = {
  isThinking: false,
  currentStatus: "",
  thinkingLogs: [],
  answerText: "",
};

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streaming, setStreaming] = useState<StreamingState>(initialStreamingState);
  const a2ui = useA2UI();
  const api = getApiService();
  const initializedRef = useRef(false);

  // 스트리밍 상태 리셋
  const resetStreaming = useCallback(() => {
    setStreaming(initialStreamingState);
  }, []);

  // 에러 클리어
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // 요청 취소
  const abortRequest = useCallback(() => {
    const wasAborted = api.abortCurrentRequest();
    if (wasAborted) {
      setIsLoading(false);
    }
    return wasAborted;
  }, [api]);

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
      setError(null);
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
        } else if (!response.success && response.error) {
          setError("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
        }
      } catch (err) {
        console.error("Failed to load initial UI:", err);
        setError("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialUI();
  }, [api, a2ui, processServerMessages]);

  // 스트리밍 이벤트 핸들러 (Gemini 스타일)
  const handleStreamEvent = useCallback((event: StreamEvent) => {
    switch (event.type) {
      case "status":
        // 상태 텍스트 변경 (동적 제목)
        setStreaming((prev) => ({
          ...prev,
          isThinking: true,
          currentStatus: event.text,
        }));
        break;

      case "thought":
        // 사고 로그 추가 (아코디언 내용)
        setStreaming((prev) => ({
          ...prev,
          thinkingLogs: [...prev.thinkingLogs, event.text],
        }));
        break;

      case "answer":
        // 답변 토큰 누적 (스트리밍)
        setStreaming((prev) => ({
          ...prev,
          isThinking: false,  // 답변이 오면 thinking 종료
          answerText: prev.answerText + event.text,
        }));
        break;

      case "done":
        // 최종 메시지 처리
        if (event.messages && Array.isArray(event.messages)) {
          processServerMessages(event.messages as A2UIMessage[]);
        }
        resetStreaming();
        setIsLoading(false);
        break;

      case "error":
        if (event.error !== "aborted") {
          setError("메시지 전송에 실패했습니다. 다시 시도해주세요.");
        }
        resetStreaming();
        setIsLoading(false);
        break;
    }
  }, [processServerMessages, resetStreaming]);

  // 텍스트 메시지 전송 (스트리밍)
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
      setError(null);
      resetStreaming();
      setIsLoading(true);

      // 활성 Surface의 dataModel을 함께 전송 (폼 데이터 유지용)
      const currentSurface = a2ui.activeSurface;
      const payload: { text: string; currentData?: Record<string, unknown>; surfaceId?: string } = { text };

      if (currentSurface) {
        payload.currentData = currentSurface.dataModel;
        payload.surfaceId = currentSurface.surfaceId;
      }

      // SSE 스트리밍으로 전송
      await api.sendMessageStream(payload, handleStreamEvent);
    },
    [api, handleStreamEvent, a2ui.activeSurface, resetStreaming]
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

      setError(null);
      setIsLoading(true);
      try {
        const response = await api.sendMessage(actionMessage);

        if (response.success && response.data) {
          const responseData = response.data as { messages?: A2UIMessage[] };

          // 여러 메시지 처리 (assistantMessage 포함)
          if (responseData.messages && Array.isArray(responseData.messages)) {
            processServerMessages(responseData.messages);
          }
        } else if (!response.success) {
          if (response.error !== "aborted") {
            setError("요청 처리에 실패했습니다. 다시 시도해주세요.");
          }
        }
      } catch (err) {
        console.error("Failed to send action:", err);
        setError("요청 처리에 실패했습니다. 다시 시도해주세요.");
      } finally {
        setIsLoading(false);
      }
    },
    [api, processServerMessages]
  );

  return {
    messages,
    isLoading,
    error,
    streaming,
    sendMessage,
    sendAction,
    abortRequest,
    clearError,
    a2ui,
  };
}
