"""항공권 예약 폼 생성기"""

from .base import BaseFormGenerator


class FlightFormGenerator(BaseFormGenerator):
    """항공권 예약 폼 생성"""

    SURFACE_ID = "flight-booking"

    def generate(self) -> list[dict]:
        messages = []

        # Surface 생성
        messages.append(self.create_surface(self.SURFACE_ID))

        # 컴포넌트 정의
        messages.append({
            "updateComponents": {
                "surfaceId": self.SURFACE_ID,
                "components": self._get_components()
            }
        })

        # 초기 데이터 모델
        messages.append({
            "updateDataModel": {
                "surfaceId": self.SURFACE_ID,
                "operations": self._get_initial_data()
            }
        })

        return messages

    def _get_components(self) -> list[dict]:
        return [
            {
                "id": "root",
                "component": "Column",
                "children": ["header", "trip-type", "route", "dates", "passengers", "class", "actions"]
            },
            {
                "id": "header",
                "component": "Text",
                "text": "항공권 검색",
                "style": "headline"
            },
            {
                "id": "trip-type",
                "component": "ChoicePicker",
                "label": "여행 유형",
                "mode": "single",
                "options": [
                    {"value": "roundtrip", "label": "왕복"},
                    {"value": "oneway", "label": "편도"}
                ],
                "binding": "/flight/tripType"
            },
            {
                "id": "route",
                "component": "Row",
                "children": ["departure", "swap-btn", "arrival"]
            },
            {
                "id": "departure",
                "component": "ChoicePicker",
                "label": "출발지",
                "options": "/airports",
                "binding": "/flight/departure",
                "searchable": True
            },
            {
                "id": "swap-btn",
                "component": "Button",
                "icon": "swap",
                "variant": "icon",
                "action": "swap-route"
            },
            {
                "id": "arrival",
                "component": "ChoicePicker",
                "label": "도착지",
                "options": "/airports",
                "binding": "/flight/arrival",
                "searchable": True
            },
            {
                "id": "dates",
                "component": "Row",
                "children": ["departure-date", "return-date"]
            },
            {
                "id": "departure-date",
                "component": "DateTimeInput",
                "label": "출발일",
                "mode": "date",
                "binding": "/flight/departureDate",
                "minDate": "today"
            },
            {
                "id": "return-date",
                "component": "DateTimeInput",
                "label": "귀국일",
                "mode": "date",
                "binding": "/flight/returnDate",
                "minDate": "/flight/departureDate",
                "visible": "/flight/tripType == 'roundtrip'"
            },
            {
                "id": "passengers",
                "component": "Row",
                "children": ["adults", "children", "infants"]
            },
            {
                "id": "adults",
                "component": "Stepper",
                "label": "성인",
                "min": 1,
                "max": 9,
                "binding": "/flight/passengers/adults"
            },
            {
                "id": "children",
                "component": "Stepper",
                "label": "아동 (2-11세)",
                "min": 0,
                "max": 9,
                "binding": "/flight/passengers/children"
            },
            {
                "id": "infants",
                "component": "Stepper",
                "label": "유아 (0-2세)",
                "min": 0,
                "max": 9,
                "binding": "/flight/passengers/infants"
            },
            {
                "id": "class",
                "component": "ChoicePicker",
                "label": "좌석 등급",
                "options": [
                    {"value": "economy", "label": "이코노미"},
                    {"value": "premium", "label": "프리미엄 이코노미"},
                    {"value": "business", "label": "비즈니스"},
                    {"value": "first", "label": "퍼스트"}
                ],
                "binding": "/flight/class"
            },
            {
                "id": "actions",
                "component": "Row",
                "children": ["back-btn", "search-btn"]
            },
            {
                "id": "back-btn",
                "component": "Button",
                "label": "이전",
                "variant": "outlined",
                "action": "back"
            },
            {
                "id": "search-btn",
                "component": "Button",
                "label": "항공편 검색",
                "variant": "filled",
                "action": "search-flights"
            }
        ]

    def _get_initial_data(self) -> list[dict]:
        return [
            {
                "op": "add",
                "path": "/flight",
                "value": {
                    "tripType": "roundtrip",
                    "departure": "",
                    "arrival": "",
                    "departureDate": "",
                    "returnDate": "",
                    "passengers": {
                        "adults": 1,
                        "children": 0,
                        "infants": 0
                    },
                    "class": "economy"
                }
            },
            {
                "op": "add",
                "path": "/airports",
                "value": [
                    {"value": "ICN", "label": "인천국제공항 (ICN)"},
                    {"value": "GMP", "label": "김포국제공항 (GMP)"},
                    {"value": "CJU", "label": "제주국제공항 (CJU)"},
                    {"value": "PUS", "label": "김해국제공항 (PUS)"},
                    {"value": "NRT", "label": "도쿄 나리타 (NRT)"},
                    {"value": "KIX", "label": "오사카 간사이 (KIX)"},
                    {"value": "BKK", "label": "방콕 수완나품 (BKK)"}
                ]
            }
        ]
