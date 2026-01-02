"""UI 생성 유틸"""


def get_initial_ui() -> list[dict]:
    """초기 여행 타입 선택 UI"""
    return [
        {"createSurface": {"surfaceId": "travel-type-selector", "catalogId": "travel-booking"}},
        {
            "updateComponents": {
                "surfaceId": "travel-type-selector",
                "components": [
                    {"id": "root", "component": "Column", "children": ["header", "type-cards"]},
                    {
                        "id": "header",
                        "component": "Text",
                        "text": "어떤 여행을 계획하고 계신가요?",
                        "style": "headline",
                    },
                    {
                        "id": "type-cards",
                        "component": "Row",
                        "children": ["flight-card", "hotel-card", "car-card", "package-card"],
                    },
                    {
                        "id": "flight-card",
                        "component": "Card",
                        "children": ["flight-icon", "flight-label"],
                        "action": "select-flight",
                    },
                    {"id": "flight-icon", "component": "Icon", "icon": "airplane"},
                    {"id": "flight-label", "component": "Text", "text": "항공권"},
                    {
                        "id": "hotel-card",
                        "component": "Card",
                        "children": ["hotel-icon", "hotel-label"],
                        "action": "select-hotel",
                    },
                    {"id": "hotel-icon", "component": "Icon", "icon": "hotel"},
                    {"id": "hotel-label", "component": "Text", "text": "호텔"},
                    {
                        "id": "car-card",
                        "component": "Card",
                        "children": ["car-icon", "car-label"],
                        "action": "select-car",
                    },
                    {"id": "car-icon", "component": "Icon", "icon": "car"},
                    {"id": "car-label", "component": "Text", "text": "렌터카"},
                    {
                        "id": "package-card",
                        "component": "Card",
                        "children": ["package-icon", "package-label"],
                        "action": "select-package",
                    },
                    {"id": "package-icon", "component": "Icon", "icon": "package"},
                    {"id": "package-label", "component": "Text", "text": "패키지"},
                ],
            }
        },
    ]
