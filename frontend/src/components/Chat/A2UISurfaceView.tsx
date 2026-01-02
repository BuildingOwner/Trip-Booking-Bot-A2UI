/**
 * A2UI Surface 뷰 컴포넌트
 * useA2UI 훅의 상태를 받아서 Surface를 렌더링
 */

import type { Surface } from "../../hooks/useA2UI";
import type { A2UIComponent } from "../../types/a2ui";
import "../../components/A2UI/A2UIRenderer.css";

interface A2UISurfaceViewProps {
  a2ui: {
    activeSurface: Surface | null;
    getBoundValue: (surfaceId: string, binding: string) => unknown;
    updateDataValue: (surfaceId: string, path: string, value: unknown) => void;
  };
  onAction: (surfaceId: string, componentId: string, action: string, data?: Record<string, unknown>) => void;
}

export function A2UISurfaceView({ a2ui, onAction }: A2UISurfaceViewProps) {
  const { activeSurface } = a2ui;

  if (!activeSurface) {
    return (
      <div className="a2ui-empty">
        <p>대화를 시작하세요...</p>
      </div>
    );
  }

  const rootComponent = activeSurface.components.get("root");
  if (!rootComponent) {
    return null;
  }

  return (
    <div className="a2ui-surface-view">
      <ComponentRenderer
        component={rootComponent}
        surface={activeSurface}
        onAction={onAction}
        onValueChange={(path, value) => {
          a2ui.updateDataValue(activeSurface.surfaceId, path, value);
        }}
      />
    </div>
  );
}

interface ComponentRendererProps {
  component: A2UIComponent;
  surface: Surface;
  onAction: (surfaceId: string, componentId: string, action: string, data?: Record<string, unknown>) => void;
  onValueChange: (path: string, value: unknown) => void;
}

function ComponentRenderer({ component, surface, onAction, onValueChange }: ComponentRendererProps) {
  const { surfaceId, components, dataModel } = surface;

  // 자식 컴포넌트 렌더링
  const renderChildren = () => {
    if (!component.children) return null;
    return component.children.map((childId) => {
      const child = components.get(childId);
      if (!child) return null;

      // visible 조건 체크
      if (child.visible && !evaluateCondition(child.visible, dataModel)) {
        return null;
      }

      return (
        <ComponentRenderer
          key={childId}
          component={child}
          surface={surface}
          onAction={onAction}
          onValueChange={onValueChange}
        />
      );
    });
  };

  // 바인딩된 값 가져오기
  const getBoundValue = (binding?: string) => {
    if (!binding) return undefined;
    return getNestedValue(dataModel, binding.split("/").filter(Boolean));
  };

  // 옵션 가져오기
  const getOptions = (): Array<{ value: string; label: string }> => {
    if (!component.options) return [];
    if (typeof component.options === "string") {
      const opts = getBoundValue(component.options);
      return Array.isArray(opts) ? opts : [];
    }
    return component.options;
  };

  // 값 변경 핸들러
  const handleChange = (value: unknown) => {
    if (component.binding) {
      onValueChange(component.binding, value);
    }
  };

  switch (component.component) {
    case "Column":
      return <div className="a2ui-column">{renderChildren()}</div>;

    case "Row":
      return <div className="a2ui-row">{renderChildren()}</div>;

    case "Text":
      return (
        <p className={`a2ui-text ${component.style || ""}`}>
          {component.text || (component.binding ? String(getBoundValue(component.binding) ?? "") : "")}
        </p>
      );

    case "Icon":
      return <span className="a2ui-icon">{getIconEmoji(component.icon)}</span>;

    case "Card":
      return (
        <button
          className="a2ui-card"
          onClick={() => component.action && onAction(surfaceId, component.id, component.action, dataModel)}
        >
          {renderChildren()}
        </button>
      );

    case "Button":
      return (
        <button
          className={`a2ui-button ${component.variant || ""}`}
          onClick={() => component.action && onAction(surfaceId, component.id, component.action, dataModel)}
        >
          {component.icon ? getIconEmoji(component.icon) : component.label}
        </button>
      );

    case "ChoicePicker": {
      const rawOptions = getOptions();
      const currentValue = getBoundValue(component.binding) as string;

      // excludeBinding이 있으면 해당 값과 같은 옵션 제외
      const excludeValue = component.excludeBinding
        ? getBoundValue(component.excludeBinding)
        : undefined;
      const options = excludeValue
        ? rawOptions.filter((opt) => opt.value !== excludeValue)
        : rawOptions;

      // mode가 single이고 options이 2개면 라디오 버튼 스타일
      if (component.mode === "single" && options.length <= 3) {
        return (
          <div className="a2ui-choice-picker">
            {component.label && <label>{component.label}</label>}
            <div className="a2ui-radio-group">
              {options.map((opt) => (
                <label key={opt.value} className="a2ui-radio-option">
                  <input
                    type="radio"
                    name={component.id}
                    value={opt.value}
                    checked={currentValue === opt.value}
                    onChange={() => handleChange(opt.value)}
                  />
                  <span>{opt.label}</span>
                </label>
              ))}
            </div>
          </div>
        );
      }

      return (
        <div className="a2ui-choice-picker">
          {component.label && <label>{component.label}</label>}
          <select
            value={currentValue || ""}
            onChange={(e) => handleChange(e.target.value)}
          >
            <option value="">선택하세요</option>
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      );
    }

    case "DateTimeInput": {
      // minDate 처리: "today" 또는 경로 참조
      const getMinDate = (): string | undefined => {
        if (!component.minDate) return undefined;
        if (component.minDate === "today") {
          return new Date().toISOString().split("T")[0];
        }
        // 경로 참조 (예: "/flight/departureDate")
        const value = getBoundValue(component.minDate);
        return typeof value === "string" && value ? value : undefined;
      };

      // maxDate 처리
      const getMaxDate = (): string | undefined => {
        if (!component.maxDate) return undefined;
        if (component.maxDate === "today") {
          return new Date().toISOString().split("T")[0];
        }
        const value = getBoundValue(component.maxDate);
        return typeof value === "string" && value ? value : undefined;
      };

      return (
        <div className="a2ui-datetime">
          {component.label && <label>{component.label}</label>}
          <input
            type={component.mode === "datetime" ? "datetime-local" : "date"}
            value={(getBoundValue(component.binding) as string) || ""}
            min={getMinDate()}
            max={getMaxDate()}
            onChange={(e) => handleChange(e.target.value)}
          />
        </div>
      );
    }

    case "Stepper": {
      const value = (getBoundValue(component.binding) as number) ?? component.min ?? 0;
      return (
        <div className="a2ui-stepper">
          {component.label && <label>{component.label}</label>}
          <div className="a2ui-stepper-controls">
            <button
              type="button"
              onClick={() => handleChange(Math.max(component.min ?? 0, value - 1))}
              disabled={value <= (component.min ?? 0)}
            >
              -
            </button>
            <span>{value}</span>
            <button
              type="button"
              onClick={() => handleChange(Math.min(component.max ?? 99, value + 1))}
              disabled={value >= (component.max ?? 99)}
            >
              +
            </button>
          </div>
        </div>
      );
    }

    case "CheckBox":
      return (
        <div className="a2ui-checkbox">
          <input
            type="checkbox"
            id={component.id}
            checked={(getBoundValue(component.binding) as boolean) || false}
            onChange={(e) => handleChange(e.target.checked)}
          />
          <label htmlFor={component.id}>{component.label}</label>
        </div>
      );

    case "TextField":
      return (
        <div className="a2ui-textfield">
          {component.label && <label>{component.label}</label>}
          <input
            type="text"
            placeholder={component.hint}
            value={(getBoundValue(component.binding) as string) || ""}
            onChange={(e) => handleChange(e.target.value)}
          />
        </div>
      );

    default:
      return <div className="a2ui-unknown">Unknown: {component.component}</div>;
  }
}

/**
 * 조건 평가 (예: "/flight/tripType == 'roundtrip'")
 * 지원 연산자: ==, !=
 * 지원 값: 'string', true, false
 */
function evaluateCondition(condition: string, dataModel: Record<string, unknown>): boolean {
  // 문자열 값 비교: "/path == 'value'" 또는 "/path != 'value'"
  const stringMatch = condition.match(/^(.+?)\s*(==|!=)\s*'(.+)'$/);
  if (stringMatch) {
    const [, path, operator, expectedValue] = stringMatch;
    const actualValue = getNestedValue(dataModel, path.split("/").filter(Boolean));
    return operator === "=="
      ? actualValue === expectedValue
      : actualValue !== expectedValue;
  }

  // boolean 값 비교: "/path == true" 또는 "/path != false"
  const boolMatch = condition.match(/^(.+?)\s*(==|!=)\s*(true|false)$/);
  if (boolMatch) {
    const [, path, operator, boolStr] = boolMatch;
    const expectedValue = boolStr === "true";
    const actualValue = getNestedValue(dataModel, path.split("/").filter(Boolean));
    return operator === "=="
      ? actualValue === expectedValue
      : actualValue !== expectedValue;
  }

  return true;
}

/**
 * 중첩 객체에서 값 가져오기
 */
function getNestedValue(obj: Record<string, unknown>, path: string[]): unknown {
  let current: unknown = obj;
  for (const key of path) {
    if (current && typeof current === "object" && key in current) {
      current = (current as Record<string, unknown>)[key];
    } else {
      return undefined;
    }
  }
  return current;
}

/**
 * 아이콘 이모지 매핑
 */
function getIconEmoji(icon?: string): string {
  const icons: Record<string, string> = {
    airplane: "✈️",
    hotel: "🏨",
    car: "🚗",
    package: "📦",
    search: "🔍",
    swap: "🔄",
    "check-circle": "✅",
  };
  return icons[icon || ""] || "•";
}
