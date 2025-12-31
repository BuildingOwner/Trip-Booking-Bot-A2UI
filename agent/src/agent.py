"""여행 예약 에이전트 - LLM 기반 의도 분석 및 폼 생성"""

import os
from .intent import IntentAnalyzer
from .forms import get_form_generator


class TravelAgent:
    """여행 예약 챗봇 에이전트"""

    def __init__(self):
        self.intent_analyzer = IntentAnalyzer()
        self.current_surface: str | None = None
        self.data_model: dict = {}

    def get_initial_ui(self) -> list[dict]:
        """초기 여행 타입 선택 UI 반환"""
        messages = []

        # Surface 생성
        messages.append({
            "createSurface": {
                "surfaceId": "travel-type-selector",
                "catalogId": "travel-booking"
            }
        })

        # 컴포넌트 정의
        messages.append({
            "updateComponents": {
                "surfaceId": "travel-type-selector",
                "components": [
                    {
                        "id": "root",
                        "component": "Column",
                        "children": ["header", "type-cards"]
                    },
                    {
                        "id": "header",
                        "component": "Text",
                        "text": "어떤 여행을 계획하고 계신가요?",
                        "style": "headline"
                    },
                    {
                        "id": "type-cards",
                        "component": "Row",
                        "children": ["flight-card", "hotel-card", "car-card", "package-card"]
                    },
                    {
                        "id": "flight-card",
                        "component": "Card",
                        "children": ["flight-icon", "flight-label"],
                        "action": "select-flight"
                    },
                    {
                        "id": "flight-icon",
                        "component": "Icon",
                        "icon": "airplane"
                    },
                    {
                        "id": "flight-label",
                        "component": "Text",
                        "text": "항공권"
                    },
                    {
                        "id": "hotel-card",
                        "component": "Card",
                        "children": ["hotel-icon", "hotel-label"],
                        "action": "select-hotel"
                    },
                    {
                        "id": "hotel-icon",
                        "component": "Icon",
                        "icon": "hotel"
                    },
                    {
                        "id": "hotel-label",
                        "component": "Text",
                        "text": "호텔"
                    },
                    {
                        "id": "car-card",
                        "component": "Card",
                        "children": ["car-icon", "car-label"],
                        "action": "select-car"
                    },
                    {
                        "id": "car-icon",
                        "component": "Icon",
                        "icon": "car"
                    },
                    {
                        "id": "car-label",
                        "component": "Text",
                        "text": "렌터카"
                    },
                    {
                        "id": "package-card",
                        "component": "Card",
                        "children": ["package-icon", "package-label"],
                        "action": "select-package"
                    },
                    {
                        "id": "package-icon",
                        "component": "Icon",
                        "icon": "package"
                    },
                    {
                        "id": "package-label",
                        "component": "Text",
                        "text": "패키지"
                    }
                ]
            }
        })

        self.current_surface = "travel-type-selector"
        return messages

    async def handle_message(self, message: dict) -> list[dict]:
        """사용자 메시지/액션 처리"""
        responses = []

        # userAction 처리
        if "userAction" in message:
            action = message["userAction"]
            action_type = action.get("action", "")

            # 여행 타입 선택
            if action_type.startswith("select-"):
                travel_type = action_type.replace("select-", "")
                responses.extend(self._show_booking_form(travel_type))

            # 뒤로가기
            elif action_type == "back":
                responses.extend(self.get_initial_ui())

            # 검색
            elif action_type.startswith("search-"):
                data = action.get("data", {})
                responses.extend(self._handle_search(action_type, data))

        # 텍스트 메시지 처리 (자연어 입력)
        elif "text" in message:
            text = message["text"]
            intent = await self.intent_analyzer.analyze(text)
            responses.extend(self._handle_intent(intent))

        return responses

    def _show_booking_form(self, travel_type: str) -> list[dict]:
        """예약 유형별 폼 표시"""
        generator = get_form_generator(travel_type)
        if generator:
            return generator.generate()
        return []

    def _handle_search(self, action_type: str, data: dict) -> list[dict]:
        """검색 처리 (Mock 데이터 반환)"""
        # TODO: Phase 4에서 구현
        return [{
            "updateComponents": {
                "surfaceId": "search-results",
                "components": [
                    {
                        "id": "root",
                        "component": "Text",
                        "text": "검색 결과를 불러오는 중..."
                    }
                ]
            }
        }]

    def _handle_intent(self, intent: dict) -> list[dict]:
        """의도 분석 결과 처리"""
        intent_type = intent.get("type")
        if intent_type in ["flight", "hotel", "car", "package"]:
            return self._show_booking_form(intent_type)
        return []
