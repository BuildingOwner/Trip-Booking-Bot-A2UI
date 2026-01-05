# A2UI 여행 예약 봇 - Frontend

React + TypeScript + Vite 기반 프론트엔드

## 기술 스택

- **React 19** + TypeScript
- **Vite** - 빌드 도구
- **@a2ui/lit** - A2UI 렌더러 (Web Components)

## 프로젝트 구조

```
src/
├── components/
│   ├── Chat/           # 채팅 UI 컴포넌트
│   │   ├── ChatContainer.tsx
│   │   ├── ChatInput.tsx
│   │   ├── MessageList.tsx
│   │   ├── A2UISurfaceView.tsx
│   │   └── ThinkingBox.tsx
│   └── A2UI/           # A2UI 렌더러
│       ├── A2UIRenderer.tsx
│       └── LitWrapper.tsx
├── hooks/
│   ├── useChat.ts      # 채팅 상태 관리
│   └── useA2UI.ts      # A2UI Surface 관리
├── services/
│   └── api.ts          # REST API 클라이언트
├── types/
│   └── a2ui.d.ts       # A2UI 타입 정의
├── App.tsx
└── main.tsx
```

## 실행 방법

```bash
# 의존성 설치
npm install

# 개발 서버 (http://localhost:5173)
npm run dev

# 프로덕션 빌드
npm run build

# 린트
npm run lint
```

## 환경 변수

`.env` 파일 생성:

```env
VITE_API_URL=http://localhost:8003
```
