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
5. **활성 폼이 있는 상태에서** "변경", "바꿔", "수정" 등의 표현은 "modify" 타입

## 타입 분류
- 항공권 관련 요청: type: "flight"
- 호텔/숙소 관련 요청: type: "hotel"
- 렌터카 관련 요청: type: "car"
- 패키지 여행 요청: type: "package"
- **기존 폼 데이터 변경 요청**: type: "modify" (예: "좌석 비즈니스로 바꿔줘", "출발지 변경해줘")
- 그 외: type: "unknown"

## 엔티티 추출 (있는 경우만)
### 공통
- departure: 출발지 (도시명 또는 공항코드)
- arrival: 도착지/목적지/도시
- departureDate: 출발일/체크인/픽업일 (YYYY-MM-DD 형식)
- returnDate: 귀국일/체크아웃/반납일 (YYYY-MM-DD 형식)
- adults: 성인 수 (숫자)
- children: 아동 수 (숫자)

### 항공권 전용
- tripType: 왕복이면 "roundtrip", 편도면 "oneway"
- infants: 유아 수 (숫자)
- class: 좌석 등급 ("economy", "business", "first")

### 호텔 전용
- rooms: 객실 수 (숫자)
- breakfast: 조식 포함 여부 (true/false)

### 렌터카 전용
- carType: 차종 ("compact"=경형/소형, "mid"=중형, "full"=대형, "suv"=SUV, "van"=승합, "luxury"=고급)
- insurance: 보험 배열 (["basic"=기본자차, "full"=완전자차, "super"=슈퍼보험])
- options: 추가옵션 배열 (["gps"=네비게이션, "childseat"=카시트, "wifi"=와이파이, "etc"=하이패스])
- pickupLocation: 픽업 장소

## modify 타입 규칙 (폼 수정 시)
**중요**: 활성 폼이 있고 사용자가 값을 변경하려 할 때 modify 타입 사용
- 여러 필드를 동시에 변경하는 경우: 각 필드를 직접 추출 (departureDate, returnDate, carType 등)
- 단일 필드만 변경하는 경우: modifyField/modifyValue 사용 가능

예시 (렌터카 폼이 활성화된 상태):
- "인천공항에서 1월 8일부터 11일까지 소형차로 완전자차에 네비 추가"
  → {{"type": "modify", "entities": {{"pickupLocation": "ICN", "departureDate": "2026-01-08", "returnDate": "2026-01-11", "carType": "compact", "insurance": ["full"], "options": ["gps"]}}}}
- "픽업 장소를 김포로 바꿔줘"
  → {{"type": "modify", "entities": {{"pickupLocation": "GMP"}}}}

### 필드 매핑 (사용자 표현 → modifyField)
- "출발지", "출발", "떠나는 곳" → departure
- "도착지", "목적지", "가는 곳", "도시" → arrival
- "출발일", "가는 날", "떠나는 날", "체크인" → departureDate
- "귀국일", "돌아오는 날", "복귀일", "체크아웃" → returnDate
- "왕복", "편도" → tripType
- "성인", "어른" → adults
- "아동", "어린이", "아이" → children
- "유아", "영아", "애기", "아기" → infants
- "좌석", "좌석등급", "클래스" → class
- "객실", "방" → rooms
- "조식", "아침" → breakfast
- "차종", "차량" → carType

### 값 매핑 (사용자 표현 → modifyValue)
- "비즈니스", "비지니스" → business
- "이코노미", "일반석" → economy
- "퍼스트", "일등석" → first
- "왕복" → roundtrip
- "편도" → oneway

## 공항 코드 매핑 (알려진 경우)
- 인천: ICN, 김포: GMP, 제주: CJU, 부산/김해: PUS
- 도쿄/나리타: NRT, 오사카/간사이: KIX, 후쿠오카: FUK
- 방콕: BKK, 싱가포르: SIN, 홍콩: HKG

## 응답 형식 (JSON)
반드시 아래 형식의 JSON만 출력하세요:
{{"type": "flight|hotel|car|package|modify|unknown", "entities": {{"departure": "출발지 또는 null", "arrival": "도착지/도시 또는 null", "departureDate": "YYYY-MM-DD 또는 null", "returnDate": "YYYY-MM-DD 또는 null", "tripType": "roundtrip|oneway 또는 null", "adults": 숫자 또는 null, "children": 숫자 또는 null, "infants": 숫자 또는 null, "class": "economy|business|first 또는 null", "rooms": 숫자 또는 null, "breakfast": true|false 또는 null, "carType": "차종 또는 null", "insurance": ["basic","full","super"] 또는 null, "options": ["gps","childseat","wifi","etc"] 또는 null, "pickupLocation": "픽업장소 또는 null", "modifyField": "필드명 또는 null", "modifyValue": "변경값 또는 null"}}}}

## 현재 날짜 정보
오늘 날짜: {today}

## 현재 활성 Surface 정보
{surface_context}
"""


def intent_node(state: TravelState) -> TravelState:
    """사용자 의도 분석 및 엔티티 추출 노드"""
    from datetime import date

    user_message = state.get("user_message", "")
    current_surface_id = state.get("current_surface_id", "")
    current_data = state.get("current_data", {})

    if not user_message:
        return {"intent_type": "unknown", "entities": {}}

    llm = get_llm()

    if not llm:
        intent_type = _keyword_based_analysis(user_message, current_surface_id)
        return {"intent_type": intent_type, "entities": {}}

    try:
        print(f"[Intent Node] Starting analysis for: {user_message}")
        print(f"[Intent Node] Active Surface: {current_surface_id}, Data: {current_data}")

        # 오늘 날짜를 프롬프트에 포함
        today = date.today().isoformat()

        # 활성 Surface 컨텍스트 생성
        if current_surface_id and current_data:
            surface_context = f"활성 Surface ID: {current_surface_id}\n현재 폼 데이터: {json.dumps(current_data, ensure_ascii=False)}"
        else:
            surface_context = "활성 Surface 없음 (폼 수정 불가)"

        prompt = INTENT_PROMPT.format(today=today, surface_context=surface_context)

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
        intent_type = _keyword_based_analysis(user_message, current_surface_id)
        return {"intent_type": intent_type, "entities": {}}
    except Exception as e:
        print(f"[Intent Node] Error: {e}")
        intent_type = _keyword_based_analysis(user_message, current_surface_id)
        return {"intent_type": intent_type, "entities": {}}


def _keyword_based_analysis(text: str, current_surface_id: str = "") -> str:
    """키워드 기반 의도 분석 (폴백)"""
    text_lower = text.lower()

    # 활성 Surface가 있고 변경 관련 키워드가 있으면 modify
    if current_surface_id and any(kw in text_lower for kw in ["변경", "바꿔", "수정", "change", "modify"]):
        return "modify"
    elif any(kw in text_lower for kw in ["항공", "비행기", "flight", "fly"]):
        return "flight"
    elif any(kw in text_lower for kw in ["호텔", "숙소", "hotel", "stay"]):
        return "hotel"
    elif any(kw in text_lower for kw in ["렌터카", "차량", "car", "rent"]):
        return "car"
    elif any(kw in text_lower for kw in ["패키지", "package", "tour"]):
        return "package"

    return "unknown"
