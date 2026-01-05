/**
 * REST API 서비스 - Agent 서버와 통신
 */

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

export interface ChatRequest {
  text?: string;
  userAction?: {
    surfaceId: string;
    componentId: string;
    action: string;
    data?: Record<string, unknown>;
  };
}

export interface ChatResponse {
  success: boolean;
  data?: unknown;
  error?: string;
}

// SSE 스트리밍 이벤트 타입 (Gemini 스타일)
export type StreamEvent =
  | { type: "status"; text: string }           // 상태 변경 (예: "검색 중...", "분석 중...")
  | { type: "thought"; text: string }          // 사고 로그 추가
  | { type: "answer"; text: string }           // 답변 토큰 (스트리밍)
  | { type: "done"; messages: unknown[]; reasoning?: string }  // 완료
  | { type: "error"; error: string };

class ApiService {
  private baseUrl: string;
  private clientId: string;
  private currentAbortController: AbortController | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.clientId = generateUUID();
  }

  /**
   * 현재 진행 중인 요청 취소
   */
  abortCurrentRequest(): boolean {
    if (this.currentAbortController) {
      this.currentAbortController.abort();
      this.currentAbortController = null;
      return true;
    }
    return false;
  }

  async getInitialUI(): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/init`, {
        method: "GET",
        headers: {
          "X-Client-ID": this.clientId,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error("Failed to get initial UI:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    // 이전 요청이 있으면 취소
    this.abortCurrentRequest();

    // 새 AbortController 생성
    this.currentAbortController = new AbortController();

    try {
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Client-ID": this.clientId,
        },
        body: JSON.stringify(request),
        signal: this.currentAbortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.currentAbortController = null;
      return { success: true, data };
    } catch (error) {
      this.currentAbortController = null;

      // 사용자가 취소한 경우
      if (error instanceof Error && error.name === "AbortError") {
        return {
          success: false,
          error: "aborted",
        };
      }

      console.error("API request failed:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  }

  /**
   * SSE 스트리밍으로 메시지 전송
   */
  async sendMessageStream(
    request: ChatRequest,
    onEvent: (event: StreamEvent) => void
  ): Promise<void> {
    // 이전 요청이 있으면 취소
    this.abortCurrentRequest();
    this.currentAbortController = new AbortController();

    try {
      const response = await fetch(`${this.baseUrl}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Client-ID": this.clientId,
        },
        body: JSON.stringify(request),
        signal: this.currentAbortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No response body");
      }

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // SSE 이벤트 파싱 (data: {...}\n\n 형식)
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || ""; // 마지막 불완전한 청크는 버퍼에 유지

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const jsonStr = line.slice(6); // "data: " 제거
              const event = JSON.parse(jsonStr) as StreamEvent;
              onEvent(event);
            } catch (e) {
              console.error("Failed to parse SSE event:", e, line);
            }
          }
        }
      }

      this.currentAbortController = null;
    } catch (error) {
      this.currentAbortController = null;

      if (error instanceof Error && error.name === "AbortError") {
        onEvent({ type: "error", error: "aborted" });
        return;
      }

      console.error("Stream request failed:", error);
      onEvent({
        type: "error",
        error: error instanceof Error ? error.message : "Unknown error",
      });
    }
  }

  getClientId(): string {
    return this.clientId;
  }
}

// 싱글톤 인스턴스
let apiService: ApiService | null = null;

export function getApiService(): ApiService {
  if (!apiService) {
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8003";
    apiService = new ApiService(apiUrl);
  }
  return apiService;
}

export { ApiService };
