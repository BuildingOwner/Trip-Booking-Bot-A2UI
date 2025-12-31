/**
 * 채팅 컨테이너 컴포넌트
 */

import { useChat } from "../../hooks/useChat";
import { ChatInput } from "./ChatInput";
import { A2UISurfaceView } from "./A2UISurfaceView";
import "./ChatContainer.css";

export function ChatContainer() {
  const { messages, isConnected, sendMessage, sendAction, a2ui } = useChat();

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>여행 예약 봇</h1>
        <span className={`connection-status ${isConnected ? "connected" : "disconnected"}`}>
          {isConnected ? "연결됨" : "연결 중..."}
        </span>
      </header>

      <div className="chat-content">
        {/* 사용자 메시지 히스토리 */}
        <div className="user-messages">
          {messages
            .filter((m) => m.type === "user")
            .map((m) => (
              <div key={m.id} className="user-message">
                {m.content}
              </div>
            ))}
        </div>

        {/* A2UI Surface 렌더링 */}
        <A2UISurfaceView a2ui={a2ui} onAction={sendAction} />
      </div>

      <ChatInput onSend={sendMessage} disabled={!isConnected} />
    </div>
  );
}
