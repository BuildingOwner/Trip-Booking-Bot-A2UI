"""여행 예약 에이전트 - LangGraph 기반"""

from typing import AsyncIterator
from langchain_core.messages import HumanMessage, AIMessage
from .graph import get_travel_graph
from .nodes import get_initial_ui, intent_node
from .nodes.llm import LLM_MODEL
from .nodes.conversation import conversation_stream

# GPT-5 모델 여부 (thinking 스트리밍 지원)
IS_REASONING_MODEL = LLM_MODEL.startswith("gpt-5") or "o1" in LLM_MODEL or "o3" in LLM_MODEL


class TravelAgent:
    """LangGraph 기반 여행 예약 챗봇 에이전트"""

    def __init__(self, thread_id: str):
        # 싱글톤 그래프 사용 (MemorySaver 포함)
        self.graph = get_travel_graph()
        # 세션 ID (MemorySaver가 이 ID로 대화 기록 관리)
        self.thread_id = thread_id
        # 현재 Surface
        self.current_surface: str | None = None

    def get_initial_ui(self) -> list[dict]:
        """초기 여행 타입 선택 UI 반환"""
        messages = get_initial_ui()
        self.current_surface = "travel-type-selector"
        return messages

    async def handle_message(self, message: dict) -> list[dict]:
        """사용자 메시지/액션 처리"""

        # 상태 초기화 (chat_history는 MemorySaver가 자동 관리)
        # 중요: user_action과 user_message 중 하나만 설정하고 다른 쪽은 명시적으로 초기화
        # (MemorySaver가 이전 state를 병합하기 때문에 이전 값이 남아있을 수 있음)
        state = {
            "user_action": None,
            "user_message": "",
            "current_data": {},
            "current_surface_id": "",
        }

        # 입력 타입 설정
        if "userAction" in message:
            state["user_action"] = message["userAction"]
        elif "text" in message:
            state["user_message"] = message["text"]
            # 현재 폼 데이터가 있으면 함께 전달
            if "currentData" in message:
                state["current_data"] = message["currentData"]
            if "surfaceId" in message:
                state["current_surface_id"] = message["surfaceId"]
        else:
            return []

        # 그래프 실행 (thread_id로 세션 구분)
        config = {"configurable": {"thread_id": self.thread_id}}
        result = self.graph.invoke(state, config)

        # 메시지 반환
        return result.get("messages", [])

    async def handle_message_stream(self, message: dict) -> AsyncIterator[dict]:
        """사용자 메시지/액션 처리 (Gemini 스타일 스트리밍)

        이벤트 타입:
        - status: 현재 상태 텍스트 (동적으로 변하는 제목)
        - thought: 사고 로그 (아코디언에 추가)
        - answer: 답변 토큰 (스트리밍)
        - done: 완료
        """

        # 상태 초기화
        state = {
            "user_action": None,
            "user_message": "",
            "current_data": {},
            "current_surface_id": "",
        }

        # userAction 처리 (스트리밍 없이)
        if "userAction" in message:
            state["user_action"] = message["userAction"]
            config = {"configurable": {"thread_id": self.thread_id}}
            result = self.graph.invoke(state, config)
            yield {"type": "done", "messages": result.get("messages", [])}
            return

        # 텍스트 메시지 처리
        if "text" in message:
            state["user_message"] = message["text"]
            if "currentData" in message:
                state["current_data"] = message["currentData"]
            if "surfaceId" in message:
                state["current_surface_id"] = message["surfaceId"]
        else:
            yield {"type": "done", "messages": []}
            return

        # 1단계: intent 분석
        yield {"type": "status", "text": "요청 분석 중"}

        intent_result = intent_node(state)
        intent_type = intent_result.get("intent_type", "unknown")
        print(f"[Stream] intent_type: {intent_type}")

        # 플로우 결정
        if intent_type in ("flight", "hotel", "car", "package"):
            flow = "booking"
        elif intent_type == "modify":
            flow = "modify"
        elif intent_type == "clarify":
            flow = "clarify"
        else:
            flow = "conversation"

        # 2단계: 플로우별 처리
        if flow == "conversation":
            # conversation: 스트리밍으로 처리
            yield {"type": "status", "text": "생각하는 중"}

            # 체크포인터에서 대화 히스토리 가져오기
            config = {"configurable": {"thread_id": self.thread_id}}
            graph_state = self.graph.get_state(config)
            chat_history = graph_state.values.get("chat_history", []) if graph_state.values else []

            # conversation_stream으로 스트리밍 (모든 이벤트 전달)
            new_chat_history = None
            async for event in conversation_stream(state["user_message"], chat_history):
                event_type = event.get("type")

                if event_type in ("status", "thought", "answer"):
                    yield event
                elif event_type == "done":
                    new_chat_history = event.get("chat_history", [])
                    yield {
                        "type": "done",
                        "messages": event.get("messages", []),
                        "reasoning": event.get("reasoning"),
                    }

            # 대화 히스토리를 LangGraph 체크포인터에 저장
            if new_chat_history:
                new_messages = []
                for msg in new_chat_history:
                    if msg.get("type") == "human":
                        new_messages.append(HumanMessage(content=msg["content"]))
                    elif msg.get("type") == "ai":
                        new_messages.append(AIMessage(content=msg["content"]))
                self.graph.update_state(config, {"chat_history": new_messages})
            return

        else:
            # 다른 플로우: LangGraph로 처리
            if flow == "booking":
                yield {"type": "status", "text": "예약 폼 생성 중"}
            elif flow == "modify":
                yield {"type": "status", "text": "수정 처리 중"}
            elif flow == "clarify":
                yield {"type": "status", "text": "확인 중"}

            config = {"configurable": {"thread_id": self.thread_id}}
            result = self.graph.invoke(state, config)
            yield {"type": "done", "messages": result.get("messages", [])}
