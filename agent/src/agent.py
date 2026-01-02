"""여행 예약 에이전트 - LangGraph 기반"""

from langchain_core.messages import BaseMessage

from .graph import create_travel_graph
from .nodes import get_initial_ui


class TravelAgent:
    """LangGraph 기반 여행 예약 챗봇 에이전트"""

    def __init__(self):
        # LangGraph 그래프 생성
        self.graph = create_travel_graph()
        # 대화 히스토리 (LangChain 메시지 타입)
        self.chat_history: list[BaseMessage] = []
        # 현재 Surface
        self.current_surface: str | None = None

    def get_initial_ui(self) -> list[dict]:
        """초기 여행 타입 선택 UI 반환"""
        messages = get_initial_ui()
        self.current_surface = "travel-type-selector"
        return messages

    async def handle_message(self, message: dict) -> list[dict]:
        """사용자 메시지/액션 처리"""

        # 상태 초기화
        state = {
            "chat_history": self.chat_history,
        }

        # 입력 타입 설정
        if "userAction" in message:
            state["user_action"] = message["userAction"]
        elif "text" in message:
            state["user_message"] = message["text"]
        else:
            return []

        # 그래프 실행
        result = self.graph.invoke(state)

        # 히스토리 업데이트 (add_messages reducer로 자동 누적됨)
        if "chat_history" in result:
            self.chat_history = result["chat_history"]

        # 메시지 반환
        return result.get("messages", [])
