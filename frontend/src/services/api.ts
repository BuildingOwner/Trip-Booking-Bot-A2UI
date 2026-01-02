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

class ApiService {
  private baseUrl: string;
  private clientId: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.clientId = generateUUID();
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
    try {
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Client-ID": this.clientId,
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error("API request failed:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
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
