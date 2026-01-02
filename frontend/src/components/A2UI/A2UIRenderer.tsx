/**
 * A2UI Surface 렌더러
 * A2UI JSON 메시지를 받아서 UI로 렌더링
 */

import { useEffect, useRef, useCallback } from "react";
import type { A2UIComponent, A2UIMessage } from "../../types/a2ui";

interface Surface {
  surfaceId: string;
  components: Map<string, A2UIComponent>;
  dataModel: Record<string, unknown>;
  componentTree: A2UIComponent | null;
}

interface A2UIRendererProps {
  messages: A2UIMessage[];
  onAction: (surfaceId: string, componentId: string, action: string, data?: Record<string, unknown>) => void;
}

/**
 * A2UI 메시지를 파싱하여 Surface 상태를 관리하고 렌더링
 */
export function A2UIRenderer({ messages, onAction }: A2UIRendererProps) {
  const surfacesRef = useRef<Map<string, Surface>>(new Map());

  // 메시지 처리
  useEffect(() => {
    for (const message of messages) {
      processMessage(message, surfacesRef.current);
    }
  }, [messages]);

  const handleAction = useCallback(
    (surfaceId: string, componentId: string, action: string) => {
      const surface = surfacesRef.current.get(surfaceId);
      onAction(surfaceId, componentId, action, surface?.dataModel);
    },
    [onAction]
  );

  // 가장 최근 Surface 렌더링
  const latestSurface = Array.from(surfacesRef.current.values()).pop();

  if (!latestSurface) {
    return <div className="a2ui-empty">UI를 기다리는 중...</div>;
  }

  return (
    <div className="a2ui-renderer">
      <SurfaceRenderer surface={latestSurface} onAction={handleAction} />
    </div>
  );
}

/**
 * 메시지를 처리하여 Surface 상태 업데이트
 */
function processMessage(message: A2UIMessage, surfaces: Map<string, Surface>) {
  if ("createSurface" in message) {
    const { surfaceId } = message.createSurface;
    surfaces.set(surfaceId, {
      surfaceId,
      components: new Map(),
      dataModel: {},
      componentTree: null,
    });
  }

  if ("updateComponents" in message) {
    const { surfaceId, components } = message.updateComponents;
    const surface = surfaces.get(surfaceId);
    if (surface) {
      for (const comp of components) {
        surface.components.set(comp.id, comp);
      }
      // root 컴포넌트를 트리로 설정
      const root = surface.components.get("root");
      if (root) {
        surface.componentTree = root;
      }
    }
  }

  if ("updateDataModel" in message) {
    const { surfaceId, operations } = message.updateDataModel;
    const surface = surfaces.get(surfaceId);
    if (surface) {
      for (const op of operations) {
        if (op.op === "add" || op.op === "replace") {
          const path = op.path.split("/").filter(Boolean);
          setNestedValue(surface.dataModel, path, op.value);
        }
      }
    }
  }

  if ("deleteSurface" in message) {
    const { surfaceId } = message.deleteSurface;
    surfaces.delete(surfaceId);
  }
}

/**
 * 중첩 객체에 값 설정
 */
function setNestedValue(obj: Record<string, unknown>, path: string[], value: unknown) {
  let current = obj;
  for (let i = 0; i < path.length - 1; i++) {
    if (!(path[i] in current)) {
      current[path[i]] = {};
    }
    current = current[path[i]] as Record<string, unknown>;
  }
  current[path[path.length - 1]] = value;
}

/**
 * Surface 렌더러
 */
interface SurfaceRendererProps {
  surface: Surface;
  onAction: (surfaceId: string, componentId: string, action: string) => void;
}

function SurfaceRenderer({ surface, onAction }: SurfaceRendererProps) {
  if (!surface.componentTree) {
    return null;
  }

  return (
    <div className="a2ui-surface">
      <ComponentRenderer
        component={surface.componentTree}
        components={surface.components}
        dataModel={surface.dataModel}
        surfaceId={surface.surfaceId}
        onAction={onAction}
      />
    </div>
  );
}

/**
 * 컴포넌트 렌더러
 */
interface ComponentRendererProps {
  component: A2UIComponent;
  components: Map<string, A2UIComponent>;
  dataModel: Record<string, unknown>;
  surfaceId: string;
  onAction: (surfaceId: string, componentId: string, action: string) => void;
}

function ComponentRenderer({
  component,
  components,
  dataModel,
  surfaceId,
  onAction,
}: ComponentRendererProps) {
  const renderChildren = () => {
    if (!component.children) return null;
    return component.children.map((childId) => {
      const child = components.get(childId);
      if (!child) return null;
      return (
        <ComponentRenderer
          key={childId}
          component={child}
          components={components}
          dataModel={dataModel}
          surfaceId={surfaceId}
          onAction={onAction}
        />
      );
    });
  };

  // 바인딩된 값 가져오기
  const getBoundValue = (binding?: string) => {
    if (!binding) return undefined;
    const path = binding.split("/").filter(Boolean);
    let value: unknown = dataModel;
    for (const key of path) {
      if (value && typeof value === "object" && key in value) {
        value = (value as Record<string, unknown>)[key];
      } else {
        return undefined;
      }
    }
    return value;
  };

  // 옵션 가져오기 (문자열이면 dataModel에서 조회)
  const getOptions = () => {
    if (!component.options) return [];
    if (typeof component.options === "string") {
      return (getBoundValue(component.options) as Array<{ value: string; label: string }>) || [];
    }
    return component.options;
  };

  switch (component.component) {
    case "Column":
      return <div className="a2ui-column">{renderChildren()}</div>;

    case "Row":
      return <div className="a2ui-row">{renderChildren()}</div>;

    case "Text":
      return (
        <p className={`a2ui-text ${component.style || ""}`}>
          {component.text || (component.binding ? String(getBoundValue(component.binding)) : "")}
        </p>
      );

    case "Icon":
      return <span className={`a2ui-icon icon-${component.icon}`}>{getIconEmoji(component.icon)}</span>;

    case "Card":
      return (
        <button
          className="a2ui-card"
          onClick={() => component.action && onAction(surfaceId, component.id, component.action)}
        >
          {renderChildren()}
        </button>
      );

    case "Button":
      return (
        <button
          className={`a2ui-button ${component.variant || ""}`}
          onClick={() => component.action && onAction(surfaceId, component.id, component.action)}
        >
          {component.label}
        </button>
      );

    case "ChoicePicker":
      return (
        <div className="a2ui-choice-picker">
          <label>{component.label}</label>
          <select defaultValue={getBoundValue(component.binding) as string}>
            <option value="">선택하세요</option>
            {getOptions().map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      );

    case "DateTimeInput":
      return (
        <div className="a2ui-datetime">
          <label>{component.label}</label>
          <input
            type={component.mode === "datetime" ? "datetime-local" : "date"}
            defaultValue={getBoundValue(component.binding) as string}
          />
        </div>
      );

    case "Stepper":
      return (
        <div className="a2ui-stepper">
          <label>{component.label}</label>
          <input
            type="number"
            min={component.min}
            max={component.max}
            defaultValue={(getBoundValue(component.binding) as number) || component.min || 0}
          />
        </div>
      );

    case "CheckBox":
      return (
        <div className="a2ui-checkbox">
          <input
            type="checkbox"
            id={component.id}
            defaultChecked={getBoundValue(component.binding) as boolean}
          />
          <label htmlFor={component.id}>{component.label}</label>
        </div>
      );

    case "TextField":
      return (
        <div className="a2ui-textfield">
          <label>{component.label}</label>
          <input
            type="text"
            placeholder={component.hint}
            defaultValue={getBoundValue(component.binding) as string}
          />
        </div>
      );

    default:
      return <div className="a2ui-unknown">Unknown: {component.component}</div>;
  }
}

/**
 * 아이콘 이름을 이모지로 변환
 */
function getIconEmoji(icon?: string): string {
  const icons: Record<string, string> = {
    airplane: "✈️",
    hotel: "🏨",
    car: "🚗",
    package: "📦",
    search: "🔍",
    swap: "⇄",
  };
  return icons[icon || ""] || "•";
}
