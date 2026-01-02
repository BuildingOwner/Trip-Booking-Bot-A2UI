"""폼 생성 노드"""

from langchain_core.messages import HumanMessage, AIMessage

from ..graph.state import TravelState
from ..forms import get_form_generator


def _merge_entities_with_current_data(current_data: dict, entities: dict, intent_type: str) -> dict:
    """기존 폼 데이터에 새로 추출한 entities를 병합

    Args:
        current_data: 현재 폼의 dataModel (e.g., {"flight": {"departure": "ICN", ...}})
        entities: 추출된 엔티티 (e.g., {"departure": "GMP", "arrival": "CJU"})
        intent_type: 의도 타입 (e.g., "flight", "hotel", "car")

    Returns:
        병합된 entities (e.g., {"departure": "GMP", "arrival": "CJU", ...})
    """
    if not current_data:
        return entities

    # current_data에서 해당 타입의 데이터 추출 (e.g., current_data["flight"])
    type_data = current_data.get(intent_type, {})
    if not type_data:
        return entities

    # 기존 데이터를 기반으로 새 entities 병합 (entities가 우선)
    merged = dict(type_data)  # 기존 데이터 복사
    for key, value in entities.items():
        if value:  # entities에 값이 있으면 덮어쓰기
            merged[key] = value

    return merged


def form_generator_node(state: TravelState) -> TravelState:
    """예약 폼 생성 노드"""
    intent_type = state.get("intent_type", "unknown")
    user_message = state.get("user_message", "")
    entities = state.get("entities", {})
    current_data = state.get("current_data", {})
    current_surface_id = state.get("current_surface_id", "")

    # 기존 폼 데이터가 있으면 병합
    merged_entities = _merge_entities_with_current_data(current_data, entities, intent_type)

    # 폼 업데이트인지 새 폼인지에 따라 메시지 분기
    is_update = bool(current_data and current_data.get(intent_type))

    type_messages = {
        "flight": "항공권 예약을 도와드릴게요! 아래 정보를 입력해주세요.",
        "hotel": "호텔 예약을 도와드릴게요! 원하시는 조건을 입력해주세요.",
        "car": "렌터카 예약을 도와드릴게요! 필요한 정보를 입력해주세요.",
        "package": "패키지 여행을 도와드릴게요! 원하시는 조건을 입력해주세요.",
    }

    update_messages = {
        "flight": "조건을 변경했어요. 확인해주세요!",
        "hotel": "조건을 변경했어요. 확인해주세요!",
        "car": "조건을 변경했어요. 확인해주세요!",
        "package": "조건을 변경했어요. 확인해주세요!",
    }

    if is_update:
        assistant_msg = update_messages.get(intent_type, "")
    else:
        assistant_msg = type_messages.get(intent_type, "")

    messages = []

    if assistant_msg:
        messages.append({"assistantMessage": assistant_msg})

    # 폼 생성 (병합된 entities를 전달하여 초기값 설정)
    generator = get_form_generator(intent_type)
    if generator:
        messages.extend(generator.generate(merged_entities))

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
