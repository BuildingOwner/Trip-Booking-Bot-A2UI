"""그래프 상태 정의"""

from typing import TypedDict, Literal, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class TravelState(TypedDict, total=False):
    """여행 예약 에이전트 상태"""

    # 입력
    user_message: str  # 사용자 텍스트 메시지
    user_action: dict  # 사용자 액션 (버튼 클릭 등)

    # 현재 폼 데이터 (폼 업데이트용)
    current_data: dict  # 현재 활성 폼의 dataModel
    current_surface_id: str  # 현재 활성 Surface ID

    # 의도 분석 결과
    intent_type: Literal["flight", "hotel", "car", "package", "modify", "unknown"]
    entities: dict  # 추출된 엔티티 (departure, arrival, departureDate, returnDate 등)

    # 대화 히스토리 (LangChain 메시지 타입, add_messages reducer)
    chat_history: Annotated[list[BaseMessage], add_messages]

    # 출력 (A2UI 메시지들)
    messages: list[dict]
