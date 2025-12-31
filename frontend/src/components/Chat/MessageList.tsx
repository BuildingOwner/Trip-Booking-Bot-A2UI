/**
 * 메시지 목록 컴포넌트
 */

import { useEffect, useRef } from "react";
import type { ChatMessage } from "../../types/a2ui";
import "./MessageList.css";

interface MessageListProps {
  messages: ChatMessage[];
  onAction: (surfaceId: string, componentId: string, action: string, data?: Record<string, unknown>) => void;
}

export function MessageList({ messages, onAction }: MessageListProps) {
  const listRef = useRef<HTMLDivElement>(null);

  // 새 메시지 시 스크롤
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="message-list" ref={listRef}>
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} onAction={onAction} />
      ))}
    </div>
  );
}

interface MessageItemProps {
  message: ChatMessage;
  onAction: (surfaceId: string, componentId: string, action: string, data?: Record<string, unknown>) => void;
}

function MessageItem({ message, onAction }: MessageItemProps) {
  if (message.type === "user") {
    return (
      <div className="message message-user">
        <div className="message-content">{message.content}</div>
      </div>
    );
  }

  if (message.type === "ui" && message.a2ui) {
    return (
      <div className="message message-agent">
        <A2UIPreview message={message.a2ui} onAction={onAction} />
      </div>
    );
  }

  return null;
}

interface A2UIPreviewProps {
  message: unknown;
  onAction: (surfaceId: string, componentId: string, action: string, data?: Record<string, unknown>) => void;
}

function A2UIPreview({ message, onAction }: A2UIPreviewProps) {
  const msg = message as Record<string, unknown>;

  // updateComponents 메시지 처리
  if ("updateComponents" in msg) {
    const update = msg.updateComponents as { surfaceId: string; components: Array<{ id: string; component: string; text?: string; action?: string; children?: string[] }> };
    const components = update.components;
    const surfaceId = update.surfaceId;

    // 간단한 미리보기 렌더링
    return (
      <div className="a2ui-preview">
        {components.map((comp) => {
          if (comp.component === "Text" && comp.text) {
            return (
              <p key={comp.id} className={`a2ui-text ${comp.id.includes("header") ? "headline" : ""}`}>
                {comp.text}
              </p>
            );
          }
          if (comp.component === "Card" && comp.action) {
            const labelComp = components.find(c => c.id === comp.children?.[1]);
            return (
              <button
                key={comp.id}
                className="a2ui-card"
                onClick={() => onAction(surfaceId, comp.id, comp.action!)}
              >
                {labelComp?.text || comp.id}
              </button>
            );
          }
          if (comp.component === "Button" && comp.action) {
            const btnComp = comp as { id: string; label?: string; action: string; variant?: string };
            return (
              <button
                key={comp.id}
                className={`a2ui-button ${btnComp.variant || ""}`}
                onClick={() => onAction(surfaceId, comp.id, comp.action!)}
              >
                {btnComp.label || comp.id}
              </button>
            );
          }
          return null;
        })}
      </div>
    );
  }

  // createSurface 메시지는 무시
  if ("createSurface" in msg) {
    return null;
  }

  // updateDataModel 메시지는 무시
  if ("updateDataModel" in msg) {
    return null;
  }

  return (
    <pre className="a2ui-raw">
      {JSON.stringify(message, null, 2)}
    </pre>
  );
}
