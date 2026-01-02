/**
 * A2UI 타입 정의
 */

export interface A2UIComponent {
  id: string;
  component: string;
  children?: string[];
  text?: string;
  label?: string;
  style?: string;
  icon?: string;
  action?: string;
  binding?: string;
  options?: string | A2UIOption[];
  visible?: string;
  mode?: string;
  min?: number;
  max?: number;
  minDate?: string;
  maxDate?: string;
  hint?: string;
  variant?: string;
  searchable?: boolean;
  excludeBinding?: string; // 해당 바인딩의 값과 같은 옵션을 제외
}

export interface A2UIOption {
  value: string;
  label: string;
}

export interface CreateSurfaceMessage {
  createSurface: {
    surfaceId: string;
    catalogId: string;
  };
}

export interface UpdateComponentsMessage {
  updateComponents: {
    surfaceId: string;
    components: A2UIComponent[];
  };
}

export interface UpdateDataModelMessage {
  updateDataModel: {
    surfaceId: string;
    operations: DataModelOperation[];
  };
}

export interface DeleteSurfaceMessage {
  deleteSurface: {
    surfaceId: string;
  };
}

export interface DataModelOperation {
  op: "add" | "remove" | "replace";
  path: string;
  value?: unknown;
}

export interface UserActionMessage {
  userAction: {
    surfaceId: string;
    componentId: string;
    action: string;
    data?: Record<string, unknown>;
  };
}

export interface AssistantMessage {
  assistantMessage: string;
  reasoning?: string;  // GPT-5 thinking summary
}

export type A2UIMessage =
  | CreateSurfaceMessage
  | UpdateComponentsMessage
  | UpdateDataModelMessage
  | DeleteSurfaceMessage
  | AssistantMessage;

export interface ChatMessage {
  id: string;
  type: "user" | "agent" | "ui";
  content?: string;
  reasoning?: string;  // GPT-5 thinking summary
  a2ui?: A2UIMessage;
  timestamp: Date;
}
