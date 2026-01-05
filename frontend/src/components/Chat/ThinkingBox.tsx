/**
 * Gemini 스타일 Thinking UI 컴포넌트
 *
 * - isThinking=true: "✦ {currentStatus}" + 로딩 애니메이션 (클릭하면 로그 펼침)
 * - isThinking=false: "✦ Thoughts ›" 클릭하면 아코디언 펼침
 */

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./ThinkingBox.css";

interface ThinkingBoxProps {
  isThinking: boolean;
  currentStatus: string;
  thinkingLogs: string[];
}

export function ThinkingBox({ isThinking, currentStatus, thinkingLogs }: ThinkingBoxProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // 로그가 없으면 표시 안 함 (thinking 중이 아닐 때)
  if (!isThinking && thinkingLogs.length === 0) {
    return null;
  }

  return (
    <div className={`thinking-box ${isThinking ? "thinking" : "completed"}`}>
      <button
        className="thinking-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="thinking-sparkle">✦</span>
        {isThinking ? (
          <>
            <span className="thinking-status">{currentStatus || "Thinking"}</span>
            <span className="thinking-dots">
              <span></span>
              <span></span>
              <span></span>
            </span>
          </>
        ) : (
          <span className="thinking-label">Thoughts</span>
        )}
        {thinkingLogs.length > 0 && (
          <span className={`thinking-arrow ${isExpanded ? "expanded" : ""}`}>
            ›
          </span>
        )}
      </button>
      {isExpanded && thinkingLogs.length > 0 && (
        <div className="thinking-logs">
          {thinkingLogs.map((log, idx) => (
            <div key={idx} className="thinking-log-item">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {log}
              </ReactMarkdown>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
