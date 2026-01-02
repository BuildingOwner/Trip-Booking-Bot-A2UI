"""검색 결과 UI 생성기"""

from typing import Optional
from .base import BaseFormGenerator


class FlightResultsGenerator(BaseFormGenerator):
    """항공편 검색 결과 생성"""

    SURFACE_ID = "flight-results"

    def generate(self, form_data: Optional[dict] = None) -> list[dict]:
        messages = []
        form_data = form_data or {}

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
                "operations": self._get_initial_data(form_data)
            }
        })
        return messages

    def _get_components(self) -> list[dict]:
        return [
            {
                "id": "root",
                "component": "Column",
                "children": ["header", "results-list", "actions"]
            },
            {
                "id": "header",
                "component": "Text",
                "text": "항공편 검색 결과",
                "style": "headline"
            },
            {
                "id": "results-list",
                "component": "List",
                "binding": "/results",
                "itemTemplate": "flight-card"
            },
            {
                "id": "actions",
                "component": "Row",
                "children": ["back-btn"]
            },
            {
                "id": "back-btn",
                "component": "Button",
                "label": "검색 조건 수정",
                "variant": "outlined",
                "action": "select-flight"
            }
        ]

    def _get_initial_data(self, form_data: dict) -> list[dict]:
        # Mock 항공편 검색 결과
        operations = [
            {
                "op": "add",
                "path": "/results",
                "value": [
                    {
                        "id": "fl1",
                        "airline": "대한항공",
                        "flightNo": "KE1201",
                        "departure": "인천(ICN)",
                        "arrival": "오사카(KIX)",
                        "departureTime": "08:30",
                        "arrivalTime": "10:30",
                        "price": 189000,
                        "duration": "2시간"
                    },
                    {
                        "id": "fl2",
                        "airline": "아시아나항공",
                        "flightNo": "OZ112",
                        "departure": "인천(ICN)",
                        "arrival": "오사카(KIX)",
                        "departureTime": "10:15",
                        "arrivalTime": "12:15",
                        "price": 175000,
                        "duration": "2시간"
                    },
                    {
                        "id": "fl3",
                        "airline": "진에어",
                        "flightNo": "LJ201",
                        "departure": "인천(ICN)",
                        "arrival": "오사카(KIX)",
                        "departureTime": "14:00",
                        "arrivalTime": "16:00",
                        "price": 129000,
                        "duration": "2시간"
                    }
                ]
            }
        ]
        # 원래 폼 데이터 복사 (검색 조건 수정 시 유지)
        if "flight" in form_data:
            operations.append({"op": "add", "path": "/flight", "value": form_data["flight"]})
        if "airports" in form_data:
            operations.append({"op": "add", "path": "/airports", "value": form_data["airports"]})
        return operations


class HotelResultsGenerator(BaseFormGenerator):
    """호텔 검색 결과 생성"""

    SURFACE_ID = "hotel-results"

    def generate(self, form_data: Optional[dict] = None) -> list[dict]:
        messages = []
        form_data = form_data or {}

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
                "operations": self._get_initial_data(form_data)
            }
        })
        return messages

    def _get_components(self) -> list[dict]:
        return [
            {
                "id": "root",
                "component": "Column",
                "children": ["header", "results-list", "actions"]
            },
            {
                "id": "header",
                "component": "Text",
                "text": "호텔 검색 결과",
                "style": "headline"
            },
            {
                "id": "results-list",
                "component": "List",
                "binding": "/results",
                "itemTemplate": "hotel-card"
            },
            {
                "id": "actions",
                "component": "Row",
                "children": ["back-btn"]
            },
            {
                "id": "back-btn",
                "component": "Button",
                "label": "검색 조건 수정",
                "variant": "outlined",
                "action": "select-hotel"
            }
        ]

    def _get_initial_data(self, form_data: dict) -> list[dict]:
        # Mock 호텔 검색 결과
        operations = [
            {
                "op": "add",
                "path": "/results",
                "value": [
                    {
                        "id": "ht1",
                        "name": "신라스테이 삼성",
                        "rating": 4.5,
                        "location": "서울 강남구",
                        "pricePerNight": 120000,
                        "amenities": ["조식", "피트니스", "무료 WiFi"],
                        "image": "hotel1.jpg"
                    },
                    {
                        "id": "ht2",
                        "name": "노보텔 앰배서더 강남",
                        "rating": 4.3,
                        "location": "서울 강남구",
                        "pricePerNight": 150000,
                        "amenities": ["조식", "수영장", "피트니스"],
                        "image": "hotel2.jpg"
                    },
                    {
                        "id": "ht3",
                        "name": "이비스 스타일 강남",
                        "rating": 4.0,
                        "location": "서울 강남구",
                        "pricePerNight": 85000,
                        "amenities": ["무료 WiFi", "조식 별도"],
                        "image": "hotel3.jpg"
                    }
                ]
            }
        ]
        # 원래 폼 데이터 복사 (검색 조건 수정 시 유지)
        if "hotel" in form_data:
            operations.append({"op": "add", "path": "/hotel", "value": form_data["hotel"]})
        if "cities" in form_data:
            operations.append({"op": "add", "path": "/cities", "value": form_data["cities"]})
        return operations


class CarResultsGenerator(BaseFormGenerator):
    """렌터카 검색 결과 생성"""

    SURFACE_ID = "car-results"

    def generate(self, form_data: Optional[dict] = None) -> list[dict]:
        messages = []
        form_data = form_data or {}

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
                "operations": self._get_initial_data(form_data)
            }
        })
        return messages

    def _get_components(self) -> list[dict]:
        return [
            {
                "id": "root",
                "component": "Column",
                "children": ["header", "results-list", "actions"]
            },
            {
                "id": "header",
                "component": "Text",
                "text": "렌터카 검색 결과",
                "style": "headline"
            },
            {
                "id": "results-list",
                "component": "List",
                "binding": "/results",
                "itemTemplate": "car-card"
            },
            {
                "id": "actions",
                "component": "Row",
                "children": ["back-btn"]
            },
            {
                "id": "back-btn",
                "component": "Button",
                "label": "검색 조건 수정",
                "variant": "outlined",
                "action": "select-car"
            }
        ]

    def _get_initial_data(self, form_data: dict) -> list[dict]:
        # Mock 렌터카 검색 결과
        operations = [
            {
                "op": "add",
                "path": "/results",
                "value": [
                    {
                        "id": "car1",
                        "model": "현대 아반떼",
                        "type": "중형",
                        "company": "롯데렌터카",
                        "pricePerDay": 55000,
                        "features": ["네비게이션", "후방카메라", "블루투스"],
                        "image": "avante.jpg"
                    },
                    {
                        "id": "car2",
                        "model": "기아 K5",
                        "type": "중형",
                        "company": "SK렌터카",
                        "pricePerDay": 65000,
                        "features": ["네비게이션", "후방카메라", "통풍시트"],
                        "image": "k5.jpg"
                    },
                    {
                        "id": "car3",
                        "model": "현대 투싼",
                        "type": "SUV",
                        "company": "쏘카",
                        "pricePerDay": 75000,
                        "features": ["네비게이션", "360도 카메라", "4WD"],
                        "image": "tucson.jpg"
                    }
                ]
            }
        ]
        # 원래 폼 데이터 복사 (검색 조건 수정 시 유지)
        if "car" in form_data:
            operations.append({"op": "add", "path": "/car", "value": form_data["car"]})
        if "locations" in form_data:
            operations.append({"op": "add", "path": "/locations", "value": form_data["locations"]})
        return operations


def get_results_generator(result_type: str) -> BaseFormGenerator | None:
    """결과 타입에 맞는 생성기 반환"""
    generators = {
        "flights": FlightResultsGenerator,
        "hotels": HotelResultsGenerator,
        "cars": CarResultsGenerator,
    }

    generator_class = generators.get(result_type)
    if generator_class:
        return generator_class()
    return None
