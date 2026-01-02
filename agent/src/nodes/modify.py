"""폼 데이터 수정 핸들러 노드"""

from ..graph.state import TravelState


# Surface ID별 필드-경로 매핑 (실제 바인딩 경로)
FIELD_PATH_MAP = {
    "flight-booking": {
        "departure": "/flight/departure",
        "arrival": "/flight/arrival",
        "departureDate": "/flight/departureDate",
        "returnDate": "/flight/returnDate",
        "tripType": "/flight/tripType",
        "adults": "/flight/passengers/adults",
        "children": "/flight/passengers/children",
        "infants": "/flight/passengers/infants",
        "class": "/flight/class",
    },
    "hotel-booking": {
        "checkIn": "/hotel/checkIn",
        "checkOut": "/hotel/checkOut",
        "rooms": "/hotel/rooms",
        "guests": "/hotel/guests",
    },
    "car-rental": {
        "pickupDate": "/car/pickupDate",
        "returnDate": "/car/returnDate",
        "pickupLocation": "/car/pickupLocation",
    },
}


def modify_handler_node(state: TravelState) -> TravelState:
    """채팅으로 요청된 폼 데이터 수정을 처리하는 노드"""

    entities = state.get("entities", {})
    current_surface_id = state.get("current_surface_id", "")
    current_data = state.get("current_data", {})

    modify_field = entities.get("modifyField")
    modify_value = entities.get("modifyValue")

    print(f"[Modify Handler] Surface: {current_surface_id}")
    print(f"[Modify Handler] Field: {modify_field}, Value: {modify_value}")
    print(f"[Modify Handler] Current Data: {current_data}")

    # 활성 Surface가 없으면 에러 메시지
    if not current_surface_id:
        return {
            "messages": [{
                "assistantMessage": "현재 활성화된 폼이 없어요. 먼저 항공권, 호텔 등을 검색해주세요."
            }]
        }

    # 수정할 필드/값이 없으면 안내 메시지
    if not modify_field or modify_value is None:
        return {
            "messages": [{
                "assistantMessage": "어떤 항목을 어떻게 변경할지 말씀해주세요. 예: \"좌석을 비즈니스로 바꿔줘\""
            }]
        }

    # 필드별 실제 경로 조회
    field_paths = FIELD_PATH_MAP.get(current_surface_id, {})
    data_path = field_paths.get(modify_field)

    if not data_path:
        return {
            "messages": [{
                "assistantMessage": f"'{modify_field}' 필드를 찾을 수 없어요. 다시 말씀해주세요."
            }]
        }

    # 숫자 필드는 정수로 변환
    if modify_field in ("adults", "children", "infants", "rooms", "guests"):
        try:
            modify_value = int(modify_value)
        except (ValueError, TypeError):
            pass

    # updateDataModel 메시지 생성
    update_message = {
        "updateDataModel": {
            "surfaceId": current_surface_id,
            "operations": [
                {
                    "op": "replace",
                    "path": data_path,
                    "value": modify_value,
                }
            ],
        }
    }

    # 필드명 한글 변환 (사용자 친화적 메시지용)
    field_names = {
        "departure": "출발지",
        "arrival": "도착지",
        "departureDate": "출발일",
        "returnDate": "귀국일",
        "tripType": "여행 타입",
        "adults": "성인 수",
        "children": "아동 수",
        "infants": "유아 수",
        "class": "좌석 등급",
        "checkIn": "체크인",
        "checkOut": "체크아웃",
        "pickupDate": "픽업일",
        "returnDateCar": "반납일",
    }

    # 값 한글 변환
    value_names = {
        "economy": "이코노미",
        "business": "비즈니스",
        "first": "퍼스트",
        "roundtrip": "왕복",
        "oneway": "편도",
    }

    field_kr = field_names.get(modify_field, modify_field)
    value_kr = value_names.get(modify_value, modify_value)

    # 확인 메시지
    assistant_message = {
        "assistantMessage": f"{field_kr}을(를) '{value_kr}'(으)로 변경했어요."
    }

    print(f"[Modify Handler] Generated updateDataModel: {update_message}")

    return {
        "messages": [update_message, assistant_message]
    }
