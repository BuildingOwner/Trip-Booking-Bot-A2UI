/**
 * 채팅 컨테이너 컴포넌트
 * 왼쪽: A2UI Surface (폼), 오른쪽: 채팅 영역
 * UI가 없으면 채팅만 가운데 정렬
 */

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useChat } from "../../hooks/useChat";
import { ChatInput, type ChatInputHandle } from "./ChatInput";
import { A2UISurfaceView } from "./A2UISurfaceView";
import type { ChatMessage } from "../../types/a2ui";
import "./ChatContainer.css";

// Thinking 컴포넌트 (접을 수 있는 reasoning 표시)
function ThinkingBlock({ reasoning }: { reasoning: string }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="thinking-block">
      <button
        className="thinking-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="thinking-icon">✦</span>
        <span className="thinking-label">Thinking</span>
        <span className={`thinking-arrow ${isExpanded ? "expanded" : ""}`}>
          ▼
        </span>
      </button>
      {isExpanded && (
        <div className="thinking-content">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{reasoning}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}

// 메시지 아이템 컴포넌트
function MessageItem({ message }: { message: ChatMessage }) {
  if (message.type === "user") {
    return (
      <div className="user-message">
        {message.content}
      </div>
    );
  }

  return (
    <div className="agent-message">
      {message.reasoning && (
        <ThinkingBlock reasoning={message.reasoning} />
      )}
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
    </div>
  );
}

export function ChatContainer() {
  const { messages, isLoading, error, sendMessage, sendAction, abortRequest, clearError, a2ui } = useChat();
  const [isClosing, setIsClosing] = useState(false);
  const [showPanel, setShowPanel] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatInputRef = useRef<ChatInputHandle>(null);
  const prevIsLoadingRef = useRef(isLoading);

  const hasUI = a2ui.activeSurface !== null;

  // 메시지가 추가되면 자동 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // AI 응답 완료 시 (isLoading: true → false) 입력창에 포커스
  useEffect(() => {
    if (prevIsLoadingRef.current && !isLoading) {
      chatInputRef.current?.focus();
    }
    prevIsLoadingRef.current = isLoading;
  }, [isLoading]);

  // UI 패널 표시/숨김 애니메이션 처리
  useEffect(() => {
    if (hasUI && !isClosing) {
      setShowPanel(true);
    }
  }, [hasUI, isClosing]);

  const handleClose = () => {
    setIsClosing(true);
    setTimeout(() => {
      a2ui.closeActiveSurface();
      setIsClosing(false);
      setShowPanel(false);
    }, 500); // 애니메이션 시간과 동일
  };

  // 액션 핸들러 (클라이언트 처리 + 서버 전송)
  const handleAction = (
    surfaceId: string,
    componentId: string,
    action: string,
    data?: Record<string, unknown>
  ) => {
    // swap-route: 출발지/도착지 교환 (클라이언트에서 직접 처리)
    if (action === "swap-route") {
      const departure = a2ui.getBoundValue(surfaceId, "/flight/departure");
      const arrival = a2ui.getBoundValue(surfaceId, "/flight/arrival");
      a2ui.updateDataValue(surfaceId, "/flight/departure", arrival || "");
      a2ui.updateDataValue(surfaceId, "/flight/arrival", departure || "");
      return;
    }

    // 기타 액션은 서버로 전송
    sendAction(surfaceId, componentId, action, data);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>여행 예약 봇</h1>
      </header>

      <div className={`main-content ${showPanel ? "with-panel" : "chat-only"}`}>
        {/* 왼쪽: A2UI Surface (UI가 있을 때만 표시) */}
        {showPanel && hasUI && (
          <div className={`ui-panel ${isClosing ? "closing" : ""}`}>
            <button
              className="ui-panel-close"
              onClick={handleClose}
              title="닫기"
            >
              ✕
            </button>
            <A2UISurfaceView a2ui={a2ui} onAction={handleAction} />
          </div>
        )}

        {/* 오른쪽: 채팅 영역 */}
        <div className="chat-panel">
          <div className="messages-area">
            {messages.length === 0 && !isLoading ? (
              <div className="empty-chat">
                <p>여행 예약을 도와드릴게요!</p>
                <p className="hint">예: "항공권 예약", "호텔 예약", "렌터카 예약"</p>
              </div>
            ) : (
              <>
                {messages.map((m) => (
                  <MessageItem key={m.id} message={m} />
                ))}
                {/* 에러 메시지 */}
                {error && (
                  <div className="error-message">
                    <span className="error-icon">!</span>
                    <span className="error-text">{error}</span>
                    <button className="error-dismiss" onClick={clearError} title="닫기">
                      ✕
                    </button>
                  </div>
                )}
                {/* Thinking 애니메이션 */}
                {isLoading && (
                  <div className="agent-message thinking">
                    <div className="thinking-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>
          <ChatInput ref={chatInputRef} onSend={sendMessage} onStop={abortRequest} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
