"""의도 분석 노드"""

import json
from langchain_core.messages import HumanMessage, SystemMessage

from ..graph.state import TravelState
from .llm import get_llm


INTENT_PROMPT = """당신은 여행 예약 의도 분석기입니다. 사용자가 **실제로 예약을 요청**하는지 판단하세요.

## 핵심 규칙
1. 사용자가 명확히 "예약", "예약하고 싶어", "예약해줘" 등 예약 의도를 표현할 때만 예약 타입으로 분류
2. 단순히 여행 관련 대화, 질문, 상담, 일정 계획 등은 "unknown"으로 분류
3. "~말고", "~아니고", "~대신" 등 부정 표현이 있으면 해당 타입 제외

## 예약 타입 분류 (명확한 예약 의도가 있을 때만)
- 항공권 예약 요청: type: "flight"
- 호텔/숙소 예약 요청: type: "hotel"
- 렌터카 예약 요청: type: "car"
- 패키지 여행 예약 요청: type: "package"
- 그 외 모든 경우: type: "unknown"

## 응답 형식 (JSON)
{"type": "flight|hotel|car|package|unknown"}"""


def intent_node(state: TravelState) -> TravelState:
    """사용자 의도 분석 노드"""
    user_message = state.get("user_message", "")

    if not user_message:
        return {"intent_type": "unknown"}

    llm = get_llm()

    if not llm:
        intent_type = _keyword_based_analysis(user_message)
        return {"intent_type": intent_type}

    try:
        # JSON 응답을 위한 LLM 설정
        llm_with_json = llm.bind(response_format={"type": "json_object"})

        messages = [
            SystemMessage(content=INTENT_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = llm_with_json.invoke(messages)

        # content가 리스트인 경우 (responses/v1 형식) 텍스트 추출
        content = response.content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_parts.append(item)
            content = "".join(text_parts)

        result = json.loads(content)
        return {"intent_type": result.get("type", "unknown")}

    except Exception as e:
        print(f"[Intent Node] Error: {e}")
        intent_type = _keyword_based_analysis(user_message)
        return {"intent_type": intent_type}


def _keyword_based_analysis(text: str) -> str:
    """키워드 기반 의도 분석 (폴백)"""
    text_lower = text.lower()

    if any(kw in text_lower for kw in ["항공", "비행기", "flight", "fly"]):
        return "flight"
    elif any(kw in text_lower for kw in ["호텔", "숙소", "hotel", "stay"]):
        return "hotel"
    elif any(kw in text_lower for kw in ["렌터카", "차량", "car", "rent"]):
        return "car"
    elif any(kw in text_lower for kw in ["패키지", "package", "tour"]):
        return "package"

    return "unknown"
