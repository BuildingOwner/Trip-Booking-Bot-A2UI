"""의도 분석 및 엔티티 추출 노드"""

import json
from langchain_core.messages import HumanMessage, SystemMessage

from ..graph.state import TravelState
from .llm import get_llm


INTENT_PROMPT = """당신은 여행 예약/검색 의도 분석기입니다. 사용자의 의도와 관련 정보를 추출하세요.

## 핵심 규칙
1. "예약", "검색", "찾아줘", "알아봐줘", "해줘" 등 여행 서비스 요청 시 해당 타입으로 분류
2. "숙소", "호텔", "게스트하우스", "에어비앤비" 등은 모두 "hotel" 타입
3. "항공", "비행기", "항공권", "티켓" 등은 모두 "flight" 타입
4. 단순 질문이나 일반 대화는 "unknown"으로 분류

## 타입 분류
- 항공권 관련 요청: type: "flight"
- 호텔/숙소 관련 요청: type: "hotel"
- 렌터카 관련 요청: type: "car"
- 패키지 여행 요청: type: "package"
- 그 외: type: "unknown"

## 엔티티 추출 (있는 경우만)
- departure: 출발지 (도시명 또는 공항코드)
- arrival: 도착지/목적지
- departureDate: 출발일/체크인 (YYYY-MM-DD 형식)
- returnDate: 귀국일/체크아웃 (YYYY-MM-DD 형식)
- tripType: 왕복이면 "roundtrip", 편도면 "oneway"
- adults: 성인 수 (숫자)
- children: 아동 수 (숫자)

## 공항 코드 매핑 (알려진 경우)
- 인천: ICN, 김포: GMP, 제주: CJU, 부산/김해: PUS
- 도쿄/나리타: NRT, 오사카/간사이: KIX, 후쿠오카: FUK
- 방콕: BKK, 싱가포르: SIN, 홍콩: HKG

## 응답 형식 (JSON)
반드시 아래 형식의 JSON만 출력하세요:
{{"type": "flight|hotel|car|package|unknown", "entities": {{"departure": "출발지 또는 null", "arrival": "도착지 또는 null", "departureDate": "YYYY-MM-DD 또는 null", "returnDate": "YYYY-MM-DD 또는 null", "tripType": "roundtrip|oneway 또는 null", "adults": 숫자 또는 null, "children": 숫자 또는 null}}}}

## 현재 날짜 정보
오늘 날짜: {today}
"""


def intent_node(state: TravelState) -> TravelState:
    """사용자 의도 분석 및 엔티티 추출 노드"""
    from datetime import date

    user_message = state.get("user_message", "")

    if not user_message:
        return {"intent_type": "unknown", "entities": {}}

    llm = get_llm()

    if not llm:
        intent_type = _keyword_based_analysis(user_message)
        return {"intent_type": intent_type, "entities": {}}

    try:
        print(f"[Intent Node] Starting analysis for: {user_message}")

        # 오늘 날짜를 프롬프트에 포함
        today = date.today().isoformat()
        prompt = INTENT_PROMPT.format(today=today)

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=user_message),
        ]

        print(f"[Intent Node] Calling LLM...")
        response = llm.invoke(messages)

        # 디버깅: 응답 구조 확인
        print(f"[Intent Node] Response type: {type(response.content)}")
        print(f"[Intent Node] Response content: {response.content}")

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

        print(f"[Intent Node] Parsed content: {content}")
        result = json.loads(content)
        intent_type = result.get("type", "unknown")
        entities = result.get("entities", {})

        # null 값 제거
        entities = {k: v for k, v in entities.items() if v is not None}

        print(f"[Intent Node] type={intent_type}, entities={entities}")
        return {"intent_type": intent_type, "entities": entities}

    except json.JSONDecodeError as e:
        print(f"[Intent Node] JSON Parse Error: {e}")
        print(f"[Intent Node] Raw content: {content}")
        intent_type = _keyword_based_analysis(user_message)
        return {"intent_type": intent_type, "entities": {}}
    except Exception as e:
        print(f"[Intent Node] Error: {e}")
        intent_type = _keyword_based_analysis(user_message)
        return {"intent_type": intent_type, "entities": {}}


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
