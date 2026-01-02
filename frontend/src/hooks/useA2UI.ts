/**
 * A2UI 상태 관리 훅
 * Surface, Components, DataModel을 관리
 */

import { useState, useCallback, useMemo } from "react";
import type {
  A2UIMessage,
  A2UIComponent,
  CreateSurfaceMessage,
  UpdateComponentsMessage,
  UpdateDataModelMessage,
  DeleteSurfaceMessage,
} from "../types/a2ui";

export interface Surface {
  surfaceId: string;
  catalogId: string;
  components: Map<string, A2UIComponent>;
  dataModel: Record<string, unknown>;
}

export interface A2UIState {
  surfaces: Map<string, Surface>;
  activeSurfaceId: string | null;
}

export function useA2UI() {
  const [state, setState] = useState<A2UIState>({
    surfaces: new Map(),
    activeSurfaceId: null,
  });

  /**
   * A2UI 메시지 처리
   */
  const processMessage = useCallback((message: A2UIMessage) => {
    setState((prev) => {
      const newSurfaces = new Map(prev.surfaces);
      let newActiveSurfaceId = prev.activeSurfaceId;

      // createSurface 처리
      if ("createSurface" in message) {
        const msg = message as CreateSurfaceMessage;
        const { surfaceId, catalogId } = msg.createSurface;
        newSurfaces.set(surfaceId, {
          surfaceId,
          catalogId,
          components: new Map(),
          dataModel: {},
        });
        newActiveSurfaceId = surfaceId;
      }

      // updateComponents 처리
      if ("updateComponents" in message) {
        const msg = message as UpdateComponentsMessage;
        const { surfaceId, components } = msg.updateComponents;
        const surface = newSurfaces.get(surfaceId);
        if (surface) {
          const newComponents = new Map(surface.components);
          for (const comp of components) {
            newComponents.set(comp.id, comp);
          }
          newSurfaces.set(surfaceId, {
            ...surface,
            components: newComponents,
          });
        }
      }

      // updateDataModel 처리
      if ("updateDataModel" in message) {
        const msg = message as UpdateDataModelMessage;
        const { surfaceId, operations } = msg.updateDataModel;
        const surface = newSurfaces.get(surfaceId);
        if (surface) {
          const newDataModel = { ...surface.dataModel };
          for (const op of operations) {
            applyOperation(newDataModel, op);
          }
          newSurfaces.set(surfaceId, {
            ...surface,
            dataModel: newDataModel,
          });
        }
      }

      // deleteSurface 처리
      if ("deleteSurface" in message) {
        const msg = message as DeleteSurfaceMessage;
        const { surfaceId } = msg.deleteSurface;
        newSurfaces.delete(surfaceId);
        if (newActiveSurfaceId === surfaceId) {
          // 다른 surface가 있으면 그것을 활성화
          const remaining = Array.from(newSurfaces.keys());
          newActiveSurfaceId = remaining.length > 0 ? remaining[remaining.length - 1] : null;
        }
      }

      return {
        surfaces: newSurfaces,
        activeSurfaceId: newActiveSurfaceId,
      };
    });
  }, []);

  /**
   * 여러 메시지 일괄 처리
   */
  const processMessages = useCallback(
    (messages: A2UIMessage[]) => {
      for (const message of messages) {
        processMessage(message);
      }
    },
    [processMessage]
  );

  /**
   * DataModel 값 업데이트
   */
  const updateDataValue = useCallback(
    (surfaceId: string, path: string, value: unknown) => {
      setState((prev) => {
        const surface = prev.surfaces.get(surfaceId);
        if (!surface) return prev;

        const newDataModel = { ...surface.dataModel };
        setNestedValue(newDataModel, path.split("/").filter(Boolean), value);

        const newSurfaces = new Map(prev.surfaces);
        newSurfaces.set(surfaceId, {
          ...surface,
          dataModel: newDataModel,
        });

        return {
          ...prev,
          surfaces: newSurfaces,
        };
      });
    },
    []
  );

  /**
   * 현재 활성 Surface 가져오기
   */
  const activeSurface = useMemo(() => {
    if (!state.activeSurfaceId) return null;
    return state.surfaces.get(state.activeSurfaceId) || null;
  }, [state.surfaces, state.activeSurfaceId]);

  /**
   * Surface의 컴포넌트 트리 가져오기
   */
  const getComponentTree = useCallback(
    (surfaceId: string) => {
      const surface = state.surfaces.get(surfaceId);
      if (!surface) return null;

      const root = surface.components.get("root");
      if (!root) return null;

      return buildTree(root, surface.components);
    },
    [state.surfaces]
  );

  /**
   * 바인딩된 값 가져오기
   */
  const getBoundValue = useCallback(
    (surfaceId: string, binding: string) => {
      const surface = state.surfaces.get(surfaceId);
      if (!surface) return undefined;

      return getNestedValue(surface.dataModel, binding.split("/").filter(Boolean));
    },
    [state.surfaces]
  );

  /**
   * 활성 Surface 닫기
   */
  const closeActiveSurface = useCallback(() => {
    setState((prev) => {
      if (!prev.activeSurfaceId) return prev;

      const newSurfaces = new Map(prev.surfaces);
      newSurfaces.delete(prev.activeSurfaceId);

      // 다른 surface가 있으면 그것을 활성화
      const remaining = Array.from(newSurfaces.keys());
      const newActiveSurfaceId = remaining.length > 0 ? remaining[remaining.length - 1] : null;

      return {
        surfaces: newSurfaces,
        activeSurfaceId: newActiveSurfaceId,
      };
    });
  }, []);

  /**
   * 초기화
   */
  const reset = useCallback(() => {
    setState({
      surfaces: new Map(),
      activeSurfaceId: null,
    });
  }, []);

  return {
    state,
    activeSurface,
    processMessage,
    processMessages,
    updateDataValue,
    getComponentTree,
    getBoundValue,
    closeActiveSurface,
    reset,
  };
}

/**
 * DataModel operation 적용
 */
function applyOperation(
  dataModel: Record<string, unknown>,
  op: { op: string; path: string; value?: unknown }
) {
  const path = op.path.split("/").filter(Boolean);

  switch (op.op) {
    case "add":
    case "replace":
      setNestedValue(dataModel, path, op.value);
      break;
    case "remove":
      removeNestedValue(dataModel, path);
      break;
  }
}

/**
 * 중첩 객체에 값 설정
 */
function setNestedValue(obj: Record<string, unknown>, path: string[], value: unknown) {
  if (path.length === 0) return;

  let current = obj;
  for (let i = 0; i < path.length - 1; i++) {
    if (!(path[i] in current) || typeof current[path[i]] !== "object") {
      current[path[i]] = {};
    }
    current = current[path[i]] as Record<string, unknown>;
  }
  current[path[path.length - 1]] = value;
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
 * 중첩 객체에서 값 제거
 */
function removeNestedValue(obj: Record<string, unknown>, path: string[]) {
  if (path.length === 0) return;

  let current = obj;
  for (let i = 0; i < path.length - 1; i++) {
    if (!(path[i] in current)) return;
    current = current[path[i]] as Record<string, unknown>;
  }
  delete current[path[path.length - 1]];
}

/**
 * 컴포넌트 트리 빌드
 */
interface TreeNode extends A2UIComponent {
  childNodes?: TreeNode[];
}

function buildTree(
  component: A2UIComponent,
  components: Map<string, A2UIComponent>
): TreeNode {
  const node: TreeNode = { ...component };

  if (component.children) {
    node.childNodes = component.children
      .map((childId) => {
        const child = components.get(childId);
        if (!child) return null;
        return buildTree(child, components);
      })
      .filter((n): n is TreeNode => n !== null);
  }

  return node;
}
