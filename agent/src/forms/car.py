"""렌터카 예약 폼 생성기"""

from .base import BaseFormGenerator


class CarFormGenerator(BaseFormGenerator):
    """렌터카 예약 폼 생성"""

    SURFACE_ID = "car-rental"

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
                "children": ["header", "same-location", "pickup", "dropoff", "dates", "car-type", "actions"]
            },
            {
                "id": "header",
                "component": "Text",
                "text": "렌터카 검색",
                "style": "headline"
            },
            {
                "id": "same-location",
                "component": "CheckBox",
                "label": "동일 장소 반납",
                "binding": "/car/sameLocation"
            },
            {
                "id": "pickup",
                "component": "ChoicePicker",
                "label": "픽업 장소",
                "options": "/locations",
                "binding": "/car/pickupLocation",
                "searchable": True
            },
            {
                "id": "dropoff",
                "component": "ChoicePicker",
                "label": "반납 장소",
                "options": "/locations",
                "binding": "/car/dropoffLocation",
                "searchable": True,
                "visible": "/car/sameLocation == false"
            },
            {
                "id": "dates",
                "component": "Row",
                "children": ["pickup-datetime", "dropoff-datetime"]
            },
            {
                "id": "pickup-datetime",
                "component": "DateTimeInput",
                "label": "픽업 일시",
                "mode": "datetime",
                "binding": "/car/pickupDateTime",
                "minDate": "today"
            },
            {
                "id": "dropoff-datetime",
                "component": "DateTimeInput",
                "label": "반납 일시",
                "mode": "datetime",
                "binding": "/car/dropoffDateTime",
                "minDate": "/car/pickupDateTime"
            },
            {
                "id": "car-type",
                "component": "ChoicePicker",
                "label": "차종",
                "options": [
                    {"value": "compact", "label": "소형"},
                    {"value": "mid", "label": "중형"},
                    {"value": "full", "label": "대형"},
                    {"value": "suv", "label": "SUV"},
                    {"value": "van", "label": "밴/미니밴"},
                    {"value": "luxury", "label": "프리미엄"}
                ],
                "binding": "/car/type"
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
                "label": "렌터카 검색",
                "variant": "filled",
                "action": "search-cars"
            }
        ]

    def _get_initial_data(self) -> list[dict]:
        return [
            {
                "op": "add",
                "path": "/car",
                "value": {
                    "sameLocation": True,
                    "pickupLocation": "",
                    "dropoffLocation": "",
                    "pickupDateTime": "",
                    "dropoffDateTime": "",
                    "type": "mid"
                }
            },
            {
                "op": "add",
                "path": "/locations",
                "value": [
                    {"value": "ICN", "label": "인천공항"},
                    {"value": "GMP", "label": "김포공항"},
                    {"value": "CJU", "label": "제주공항"},
                    {"value": "JEJU_CITY", "label": "제주시내"},
                    {"value": "SEOGWIPO", "label": "서귀포"}
                ]
            }
        ]
