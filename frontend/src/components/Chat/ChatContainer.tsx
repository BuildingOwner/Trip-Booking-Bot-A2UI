/**
 * 채팅 컨테이너 컴포넌트
 */

import { useChat } from "../../hooks/useChat";
import { ChatInput } from "./ChatInput";
import { MessageList } from "./MessageList";
import "./ChatContainer.css";

export function ChatContainer() {
  const { messages, isConnected, sendMessage, sendAction } = useChat();

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>여행 예약 봇</h1>
        <span className={`connection-status ${isConnected ? "connected" : "disconnected"}`}>
          {isConnected ? "연결됨" : "연결 중..."}
        </span>
      </header>

      <MessageList messages={messages} onAction={sendAction} />

      <ChatInput onSend={sendMessage} disabled={!isConnected} />
    </div>
  );
}
