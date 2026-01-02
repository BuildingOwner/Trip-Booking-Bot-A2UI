"""폼 생성 노드"""

from langchain_core.messages import HumanMessage, AIMessage

from ..graph.state import TravelState
from ..forms import get_form_generator


def form_generator_node(state: TravelState) -> TravelState:
    """예약 폼 생성 노드"""
    intent_type = state.get("intent_type", "unknown")
    user_message = state.get("user_message", "")

    type_messages = {
        "flight": "항공권 예약을 도와드릴게요! 아래 정보를 입력해주세요.",
        "hotel": "호텔 예약을 도와드릴게요! 원하시는 조건을 입력해주세요.",
        "car": "렌터카 예약을 도와드릴게요! 필요한 정보를 입력해주세요.",
        "package": "패키지 여행을 도와드릴게요! 원하시는 조건을 입력해주세요.",
    }

    assistant_msg = type_messages.get(intent_type, "")
    messages = []

    if assistant_msg:
        messages.append({"assistantMessage": assistant_msg})

    # 폼 생성
    generator = get_form_generator(intent_type)
    if generator:
        messages.extend(generator.generate())

    # 히스토리 업데이트 (add_messages reducer가 자동으로 추가)
    new_messages = []
    if user_message:
        new_messages.append(HumanMessage(content=user_message))
    if assistant_msg:
        new_messages.append(AIMessage(content=assistant_msg))

    return {
        "messages": messages,
        "chat_history": new_messages,
    }
