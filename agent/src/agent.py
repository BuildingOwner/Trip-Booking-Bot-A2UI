"""여행 예약 에이전트 - LangGraph 기반"""

from .graph import get_travel_graph
from .nodes import get_initial_ui


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
