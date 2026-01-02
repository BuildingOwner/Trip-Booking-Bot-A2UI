/**
 * 채팅 입력 컴포넌트
 */

import { useState, useRef, useEffect, useImperativeHandle, forwardRef, type FormEvent, type KeyboardEvent } from "react";
import "./ChatInput.css";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export interface ChatInputHandle {
  focus: () => void;
}

export const ChatInput = forwardRef<ChatInputHandle, ChatInputProps>(({ onSend, disabled }, ref) => {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 외부에서 focus() 호출 가능하게 expose
  useImperativeHandle(ref, () => ({
    focus: () => textareaRef.current?.focus(),
  }));

  // 자동 높이 조절
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  }, [input]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput("");
      // 전송 후 입력창에 포커스 유지
      textareaRef.current?.focus();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter로 전송, Shift+Enter로 줄바꿈
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="메시지를 입력하세요..."
        disabled={disabled}
        rows={1}
      />
      <button type="submit" disabled={disabled || !input.trim()}>
        전송
      </button>
    </form>
  );
});
