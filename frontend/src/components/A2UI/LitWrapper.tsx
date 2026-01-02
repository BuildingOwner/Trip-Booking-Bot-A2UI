/**
 * Lit Web Component를 React에서 사용하기 위한 래퍼
 */

import { useEffect, useRef } from "react";

// A2UI Lit 컴포넌트 타입 선언
declare global {
  namespace JSX {
    interface IntrinsicElements {
      "a2ui-surface": React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          surfaceId?: string;
          surface?: unknown;
          processor?: unknown;
        },
        HTMLElement
      >;
      "a2ui-root": React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          surfaceId?: string;
          processor?: unknown;
          childComponents?: unknown[];
        },
        HTMLElement
      >;
    }
  }
}

interface LitWrapperProps {
  children: React.ReactNode;
}

/**
 * Lit 컴포넌트를 감싸는 래퍼
 * A2UI Lit 컴포넌트들이 React 내에서 정상 작동하도록 함
 */
export function LitWrapper({ children }: LitWrapperProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // A2UI Lit 컴포넌트 등록 (동적 import)
    import("@a2ui/lit").catch((err) => {
      console.warn("A2UI Lit import failed:", err);
    });
  }, []);

  return (
    <div ref={containerRef} className="lit-wrapper">
      {children}
    </div>
  );
}
