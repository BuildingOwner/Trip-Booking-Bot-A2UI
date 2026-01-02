"""호텔 예약 폼 생성기"""

from typing import Optional
from .base import BaseFormGenerator


class HotelFormGenerator(BaseFormGenerator):
    """호텔 예약 폼 생성"""

    SURFACE_ID = "hotel-booking"

    def generate(self, entities: Optional[dict] = None) -> list[dict]:
        messages = []
        entities = entities or {}

        messages.append(self.create_surface(self.SURFACE_ID))
        messages.append({
            "updateComponents": {
                "surfaceId": self.SURFACE_ID,
                "components": self._get_components()
            }
        })
        messages.append({
            "updateDataModel": {
                "surfaceId": self.SURFACE_ID,
                "operations": self._get_initial_data(entities)
            }
        })
        return messages

    def _get_components(self) -> list[dict]:
        return [
            {
                "id": "root",
                "component": "Column",
                "children": ["header", "destination", "dates", "rooms", "guests", "options", "actions"]
            },
            {
                "id": "header",
                "component": "Text",
                "text": "호텔 검색",
                "style": "headline"
            },
            {
                "id": "destination",
                "component": "ChoicePicker",
                "label": "도시",
                "options": "/cities",
                "binding": "/hotel/destination",
                "searchable": True
            },
            {
                "id": "dates",
                "component": "Row",
                "children": ["checkin", "checkout"]
            },
            {
                "id": "checkin",
                "component": "DateTimeInput",
                "label": "체크인",
                "mode": "date",
                "binding": "/hotel/checkinDate",
                "minDate": "today"
            },
            {
                "id": "checkout",
                "component": "DateTimeInput",
                "label": "체크아웃",
                "mode": "date",
                "binding": "/hotel/checkoutDate",
                "minDate": "/hotel/checkinDate"
            },
            {
                "id": "rooms",
                "component": "Stepper",
                "label": "객실 수",
                "min": 1,
                "max": 10,
                "binding": "/hotel/rooms"
            },
            {
                "id": "guests",
                "component": "Row",
                "children": ["adults", "children"]
            },
            {
                "id": "adults",
                "component": "Stepper",
                "label": "성인",
                "min": 1,
                "max": 10,
                "binding": "/hotel/guests/adults"
            },
            {
                "id": "children",
                "component": "Stepper",
                "label": "아동",
                "min": 0,
                "max": 10,
                "binding": "/hotel/guests/children"
            },
            {
                "id": "options",
                "component": "CheckBox",
                "label": "조식 포함",
                "binding": "/hotel/breakfast"
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
                "label": "호텔 검색",
                "variant": "filled",
                "action": "search-hotels"
            }
        ]

    def _get_initial_data(self, entities: dict) -> list[dict]:
        # entities에서 값 추출 (호텔의 경우 arrival이 destination)
        destination = entities.get("arrival", "")
        checkin_date = entities.get("departureDate", "")
        checkout_date = entities.get("returnDate", "")
        adults = entities.get("adults", 2)
        children = entities.get("children", 0)
        rooms = entities.get("rooms", 1)
        breakfast = entities.get("breakfast", False)

        return [
            {
                "op": "add",
                "path": "/hotel",
                "value": {
                    "destination": destination,
                    "checkinDate": checkin_date,
                    "checkoutDate": checkout_date,
                    "rooms": rooms if isinstance(rooms, int) else 1,
                    "guests": {
                        "adults": adults if isinstance(adults, int) else 2,
                        "children": children if isinstance(children, int) else 0
                    },
                    "breakfast": breakfast if isinstance(breakfast, bool) else False
                }
            },
            {
                "op": "add",
                "path": "/cities",
                "value": [
                    {"value": "SEL", "label": "서울"},
                    {"value": "PUS", "label": "부산"},
                    {"value": "CJU", "label": "제주"},
                    {"value": "TYO", "label": "도쿄"},
                    {"value": "OSA", "label": "오사카"},
                    {"value": "FUK", "label": "후쿠오카"},
                    {"value": "BKK", "label": "방콕"},
                    {"value": "SGN", "label": "호치민"},
                    {"value": "HAN", "label": "하노이"},
                    {"value": "SIN", "label": "싱가포르"},
                    {"value": "HKG", "label": "홍콩"}
                ]
            }
        ]
