"""호텔 예약 폼 생성기"""

from .base import BaseFormGenerator


class HotelFormGenerator(BaseFormGenerator):
    """호텔 예약 폼 생성"""

    SURFACE_ID = "hotel-booking"

    def generate(self) -> list[dict]:
        messages = []
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
                "operations": self._get_initial_data()
            }
        })
        return messages

    def _get_components(self) -> list[dict]:
        return [
            {
                "id": "root",
                "component": "Column",
                "children": ["header", "destination", "dates", "rooms", "guests", "actions"]
            },
            {
                "id": "header",
                "component": "Text",
                "text": "호텔 검색",
                "style": "headline"
            },
            {
                "id": "destination",
                "component": "TextField",
                "label": "목적지",
                "hint": "도시, 지역 또는 호텔명",
                "binding": "/hotel/destination",
                "icon": "search"
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

    def _get_initial_data(self) -> list[dict]:
        return [
            {
                "op": "add",
                "path": "/hotel",
                "value": {
                    "destination": "",
                    "checkinDate": "",
                    "checkoutDate": "",
                    "rooms": 1,
                    "guests": {
                        "adults": 2,
                        "children": 0
                    }
                }
            }
        ]
