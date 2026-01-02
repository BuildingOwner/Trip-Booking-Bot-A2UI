"""폼 데이터 수정 핸들러 노드"""

from ..graph.state import TravelState


# 도시명 → 코드 매핑 (ChoicePicker value 변환용)
CITY_CODE_MAP = {
    # 한국
    "서울": "SEL", "부산": "PUS", "제주": "CJU",
    # 일본
    "도쿄": "TYO", "오사카": "OSA", "후쿠오카": "FUK",
    # 동남아
    "방콕": "BKK", "호치민": "SGN", "하노이": "HAN",
    "싱가포르": "SIN", "홍콩": "HKG",
}

# 공항 코드 매핑
AIRPORT_CODE_MAP = {
    "인천": "ICN", "김포": "GMP", "제주": "CJU", "부산": "PUS", "김해": "PUS",
    "나리타": "NRT", "하네다": "HND", "간사이": "KIX", "후쿠오카": "FUK",
    "방콕": "BKK", "싱가포르": "SIN", "홍콩": "HKG",
}

# 렌터카 픽업 장소 코드 매핑
LOCATION_CODE_MAP = {
    "인천공항": "ICN", "인천": "ICN",
    "김포공항": "GMP", "김포": "GMP",
    "제주공항": "CJU", "제주": "CJU",
    "제주시내": "JEJU_CITY", "제주시": "JEJU_CITY",
    "서귀포": "SEOGWIPO",
}


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
        # Intent에서 arrival로 추출되지만 호텔에서는 destination
        "arrival": "/hotel/destination",
        "destination": "/hotel/destination",
        # Intent에서 departureDate/returnDate로 추출되지만 호텔에서는 checkin/checkout
        "departureDate": "/hotel/checkinDate",
        "returnDate": "/hotel/checkoutDate",
        "checkinDate": "/hotel/checkinDate",
        "checkoutDate": "/hotel/checkoutDate",
        "checkIn": "/hotel/checkinDate",
        "checkOut": "/hotel/checkoutDate",
        "rooms": "/hotel/rooms",
        "adults": "/hotel/guests/adults",
        "children": "/hotel/guests/children",
        "breakfast": "/hotel/breakfast",
    },
    "car-rental": {
        "pickupLocation": "/car/pickupLocation",
        "dropoffLocation": "/car/dropoffLocation",
        "pickupDateTime": "/car/pickupDateTime",
        "dropoffDateTime": "/car/dropoffDateTime",
        "departureDate": "/car/pickupDateTime",
        "returnDate": "/car/dropoffDateTime",
        "type": "/car/type",
        "carType": "/car/type",
        "sameLocation": "/car/sameLocation",
        "insurance": "/car/insurance",
        "options": "/car/options",
    },
}


def modify_handler_node(state: TravelState) -> TravelState:
    """채팅으로 요청된 폼 데이터 수정을 처리하는 노드"""

    entities = state.get("entities", {})
    current_surface_id = state.get("current_surface_id", "")
    current_data = state.get("current_data", {})

    print(f"[Modify Handler] Surface: {current_surface_id}")
    print(f"[Modify Handler] Entities: {entities}")
    print(f"[Modify Handler] Current Data: {current_data}")

    # 활성 Surface가 없으면 에러 메시지
    if not current_surface_id:
        return {
            "messages": [{
                "assistantMessage": "현재 활성화된 폼이 없어요. 먼저 항공권, 호텔 등을 검색해주세요."
            }]
        }

    # 필드별 실제 경로 조회
    field_paths = FIELD_PATH_MAP.get(current_surface_id, {})

    # 수정할 필드 목록
    fields_to_update = {}

    # 1. 직접 필드 추출 (departure, arrival, departureDate 등)
    skip_fields = {"modifyField", "modifyValue"}
    for field, value in entities.items():
        if field in skip_fields:
            continue
        if value is None or value == "":
            continue
        if field in field_paths:
            fields_to_update[field] = value

    # 2. modifyField/modifyValue 쌍 처리 (LLM이 이 형식으로 추출한 경우)
    modify_field = entities.get("modifyField")
    modify_value = entities.get("modifyValue")
    if modify_field and modify_value is not None and modify_field in field_paths:
        fields_to_update[modify_field] = modify_value

    # 수정할 필드가 없으면 안내 메시지
    if not fields_to_update:
        return {
            "messages": [{
                "assistantMessage": "어떤 항목을 어떻게 변경할지 말씀해주세요. 예: \"출발일을 1월 10일로 바꿔줘\""
            }]
        }

    # 여러 필드 업데이트를 위한 operations 생성
    operations = []
    updated_fields = []

    for field, value in fields_to_update.items():
        data_path = field_paths[field]

        # 숫자 필드는 정수로 변환
        if field in ("adults", "children", "infants", "rooms", "guests"):
            try:
                value = int(value)
            except (ValueError, TypeError):
                pass

        # boolean 필드 처리
        if field == "breakfast":
            value = True if value else False

        # 도시/공항명 → 코드 변환 (ChoicePicker value용)
        if field in ("arrival", "destination") and isinstance(value, str):
            # 호텔의 경우 도시 코드로 변환
            if current_surface_id == "hotel-booking":
                value = CITY_CODE_MAP.get(value, value)
            # 항공권의 경우 공항 코드로 변환
            else:
                value = AIRPORT_CODE_MAP.get(value, value)

        if field == "departure" and isinstance(value, str):
            value = AIRPORT_CODE_MAP.get(value, value)

        # 렌터카 픽업/반납 장소 코드 변환
        if field in ("pickupLocation", "dropoffLocation") and isinstance(value, str):
            value = LOCATION_CODE_MAP.get(value, value)

        # 렌터카 픽업/반납 일시: 날짜만 있으면 기본 시간 추가 (DateTimeInput은 datetime 형식 필요)
        if field in ("pickupDateTime", "dropoffDateTime") and isinstance(value, str):
            # "2026-01-08" → "2026-01-08T10:00" (픽업은 10시, 반납은 18시 기본)
            if "T" not in value and len(value) == 10:  # YYYY-MM-DD 형식
                default_time = "10:00" if field == "pickupDateTime" else "18:00"
                value = f"{value}T{default_time}"

        operations.append({
            "op": "replace",
            "path": data_path,
            "value": value,
        })
        updated_fields.append(field)

    # updateDataModel 메시지 생성
    update_message = {
        "updateDataModel": {
            "surfaceId": current_surface_id,
            "operations": operations,
        }
    }

    # 필드명 한글 변환 (사용자 친화적 메시지용)
    field_names = {
        "departure": "출발지",
        "arrival": "도착지",
        "destination": "도시",
        "departureDate": "출발일",
        "returnDate": "귀국일",
        "tripType": "여행 타입",
        "adults": "성인 수",
        "children": "아동 수",
        "infants": "유아 수",
        "class": "좌석 등급",
        "checkIn": "체크인",
        "checkOut": "체크아웃",
        "checkinDate": "체크인",
        "checkoutDate": "체크아웃",
        "rooms": "객실 수",
        "breakfast": "조식 포함",
        "pickupLocation": "픽업 장소",
        "dropoffLocation": "반납 장소",
        "pickupDateTime": "픽업 일시",
        "dropoffDateTime": "반납 일시",
        "type": "차종",
        "carType": "차종",
        "insurance": "보험",
        "options": "추가 옵션",
    }

    # 보험/옵션 값 한글 변환
    insurance_names = {
        "basic": "기본 자차",
        "full": "완전 자차",
        "super": "슈퍼 보험",
    }
    option_names = {
        "gps": "네비게이션",
        "childseat": "카시트",
        "wifi": "와이파이",
        "etc": "하이패스",
    }

    # 값 한글 변환
    value_names = {
        "economy": "이코노미",
        "business": "비즈니스",
        "first": "퍼스트",
        "roundtrip": "왕복",
        "oneway": "편도",
        True: "포함",
        False: "미포함",
        # 차종
        "compact": "소형",
        "mid": "중형",
        "full": "대형",
        "suv": "SUV",
        "van": "승합",
        "luxury": "고급",
        # 픽업 장소
        "ICN": "인천공항",
        "GMP": "김포공항",
        "CJU": "제주공항",
        "JEJU_CITY": "제주시내",
        "SEOGWIPO": "서귀포",
    }

    # 변경된 필드들의 한글 목록 생성
    updated_names = []
    for field in updated_fields:
        field_kr = field_names.get(field, field)
        value = fields_to_update[field]

        # 배열 값 처리 (보험, 옵션)
        if field == "insurance" and isinstance(value, list):
            value_kr = ", ".join([insurance_names.get(v, v) for v in value])
        elif field == "options" and isinstance(value, list):
            value_kr = ", ".join([option_names.get(v, v) for v in value])
        else:
            value_kr = value_names.get(value, str(value))

        updated_names.append(f"{field_kr}: {value_kr}")

    # 확인 메시지
    if len(updated_names) == 1:
        message_text = f"{updated_names[0]}(으)로 변경했어요."
    else:
        message_text = "다음 항목들을 변경했어요: " + ", ".join(updated_names)

    assistant_message = {
        "assistantMessage": message_text
    }

    print(f"[Modify Handler] Generated updateDataModel: {update_message}")
    print(f"[Modify Handler] Updated fields: {updated_fields}")

    return {
        "messages": [update_message, assistant_message]
    }
