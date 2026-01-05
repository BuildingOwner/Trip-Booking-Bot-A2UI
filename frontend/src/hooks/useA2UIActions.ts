/**
 * A2UI 액션 처리 훅
 * 클라이언트 액션과 서버 액션을 분리하여 처리
 */

type SendActionFn = (
  surfaceId: string,
  componentId: string,
  action: string,
  data?: Record<string, unknown>
) => void;

interface A2UIHookReturn {
  getBoundValue: (surfaceId: string, binding: string) => unknown;
  updateDataValue: (surfaceId: string, path: string, value: unknown) => void;
}

interface UseA2UIActionsProps {
  a2ui: A2UIHookReturn;
  sendAction: SendActionFn;
}

interface UseA2UIActionsReturn {
  handleAction: (
    surfaceId: string,
    componentId: string,
    action: string,
    data?: Record<string, unknown>
  ) => void;
}

/**
 * A2UI 액션 처리 훅
 * - 클라이언트 액션: swap-route 등 서버 통신 없이 처리
 * - 서버 액션: search-flights 등 백엔드로 전송
 */
export function useA2UIActions({
  a2ui,
  sendAction,
}: UseA2UIActionsProps): UseA2UIActionsReturn {
  const handleAction = (
    surfaceId: string,
    componentId: string,
    action: string,
    data?: Record<string, unknown>
  ) => {
    // 클라이언트 액션: swap-route (출발지/도착지 교환)
    if (action === "swap-route") {
      const departure = a2ui.getBoundValue(surfaceId, "/flight/departure");
      const arrival = a2ui.getBoundValue(surfaceId, "/flight/arrival");
      a2ui.updateDataValue(surfaceId, "/flight/departure", arrival || "");
      a2ui.updateDataValue(surfaceId, "/flight/arrival", departure || "");
      return;
    }

    // 서버 액션: 백엔드로 전송
    sendAction(surfaceId, componentId, action, data);
  };

  return { handleAction };
}
