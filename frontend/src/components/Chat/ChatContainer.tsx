/**
 * 채팅 컨테이너 컴포넌트
 * 왼쪽: A2UI Surface (폼), 오른쪽: 채팅 영역
 * UI가 없으면 채팅만 가운데 정렬
 */

import { useState, useEffect, useRef } from "react";
import { useChat } from "../../hooks/useChat";
import { ChatInput } from "./ChatInput";
import { A2UISurfaceView } from "./A2UISurfaceView";
import "./ChatContainer.css";

export function ChatContainer() {
  const { messages, isLoading, sendMessage, sendAction, a2ui } = useChat();
  const [isClosing, setIsClosing] = useState(false);
  const [showPanel, setShowPanel] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const hasUI = a2ui.activeSurface !== null;

  // 메시지가 추가되면 자동 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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
        {isLoading && <span className="loading-status">처리 중...</span>}
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
            <A2UISurfaceView a2ui={a2ui} onAction={sendAction} />
          </div>
        )}

        {/* 오른쪽: 채팅 영역 */}
        <div className="chat-panel">
          <div className="messages-area">
            {messages.length === 0 ? (
              <div className="empty-chat">
                <p>여행 예약을 도와드릴게요!</p>
                <p className="hint">예: "항공권 예약", "호텔 예약", "렌터카 예약"</p>
              </div>
            ) : (
              messages.map((m) => (
                <div
                  key={m.id}
                  className={m.type === "user" ? "user-message" : "agent-message"}
                >
                  {m.content}
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}
