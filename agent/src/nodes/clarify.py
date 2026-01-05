"""명확화 질문 핸들러 노드"""

from langchain_core.messages import HumanMessage, AIMessage

from ..graph.state import TravelState


def clarify_handler_node(state: TravelState) -> TravelState:
    """모호한 요청에 대한 명확화 질문 응답 노드"""

    user_message = state.get("user_message", "")
    entities = state.get("entities", {})

    # LLM이 생성한 명확화 질문 사용
    clarify_question = entities.get("clarifyQuestion")

    if clarify_question:
        return {
            "messages": [{"assistantMessage": clarify_question}],
            "chat_history": [
                HumanMessage(content=user_message),
                AIMessage(content=clarify_question),
            ],
        }

    # 기본 명확화 질문 (clarifyQuestion이 없는 경우)
    ambiguous_value = entities.get("ambiguousValue", "")
    candidate_fields = entities.get("candidateFields", [])

    # 필드명 한글 변환
    field_names = {
        "departure": "출발지",
        "arrival": "도착지",
        "departureDate": "출발일",
        "returnDate": "귀국일",
        "checkinDate": "체크인",
        "checkoutDate": "체크아웃",
        "pickupLocation": "픽업 장소",
        "dropoffLocation": "반납 장소",
        "pickupDateTime": "픽업 일시",
        "dropoffDateTime": "반납 일시",
        "adults": "성인 수",
        "children": "아동 수",
        "infants": "유아 수",
        "rooms": "객실 수",
    }

    if candidate_fields:
        field_names_kr = [field_names.get(f, f) for f in candidate_fields]
        options = ", ".join(field_names_kr[:-1]) + f" 중 어떤 것을 변경할까요?" if len(field_names_kr) > 1 else field_names_kr[0]

        if ambiguous_value:
            message = f"'{ambiguous_value}'로 변경하시려는 것 같은데, {options}"
        else:
            message = f"어떤 항목을 변경하시려는 건가요? ({', '.join(field_names_kr)})"
    else:
        message = "어떤 항목을 어떻게 변경할지 조금 더 구체적으로 말씀해주세요."

    return {
        "messages": [{"assistantMessage": message}],
        "chat_history": [
            HumanMessage(content=user_message),
            AIMessage(content=message),
        ],
    }
