/**
 * 채팅 컨테이너 컴포넌트
 * 왼쪽: A2UI Surface (폼), 오른쪽: 채팅 영역
 * UI가 없으면 채팅만 가운데 정렬
 */

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useChat } from "../../hooks/useChat";
import { useA2UIActions } from "../../hooks/useA2UIActions";
import { ChatInput, type ChatInputHandle } from "./ChatInput";
import { A2UISurfaceRenderer } from "./A2UISurfaceView";
import { ThinkingBox } from "./ThinkingBox";
import type { ChatMessage } from "../../types/a2ui";
import "./ChatContainer.css";

// 메시지 아이템 컴포넌트
function MessageItem({ message }: { message: ChatMessage }) {
  if (message.type === "user") {
    return (
      <div className="user-message">
        {message.content}
      </div>
    );
  }

  // 에이전트 메시지: reasoning이 있으면 ThinkingBox(완료 상태)로 표시
  return (
    <div className="agent-message">
      {message.reasoning && (
        <ThinkingBox
          isThinking={false}
          currentStatus=""
          thinkingLogs={message.reasoning.split("\n").filter((line) => line.trim())}
        />
      )}
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
    </div>
  );
}

export function ChatContainer() {
  const { messages, isLoading, error, streaming, sendMessage, sendAction, abortRequest, clearError, a2ui } = useChat();
  const { handleAction } = useA2UIActions({ a2ui, sendAction });
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
            <A2UISurfaceRenderer
              surface={a2ui.activeSurface}
              onAction={handleAction}
              onValueChange={a2ui.updateDataValue}
            />
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
                {/* 스트리밍 중 표시 (Gemini 스타일) */}
                {isLoading && (
                  <div className="agent-message streaming">
                    {/* Thinking 중이거나 로그가 있으면 ThinkingBox 표시 */}
                    {(streaming.isThinking || streaming.thinkingLogs.length > 0) && (
                      <ThinkingBox
                        isThinking={streaming.isThinking}
                        currentStatus={streaming.currentStatus}
                        thinkingLogs={streaming.thinkingLogs}
                      />
                    )}
                    {/* 답변 스트리밍 */}
                    {streaming.answerText && (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {streaming.answerText}
                      </ReactMarkdown>
                    )}
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
