"""사용자 액션 처리 노드"""

from ..graph.state import TravelState
from ..forms import get_form_generator
from ..forms.results import get_results_generator
from .ui import get_initial_ui


def _extract_entities_from_data(current_data: dict, travel_type: str) -> dict:
    """current_data에서 폼 생성용 entities 추출"""
    entities = {}

    if travel_type == "flight" and "flight" in current_data:
        flight = current_data["flight"]
        entities["departure"] = flight.get("departure", "")
        entities["arrival"] = flight.get("arrival", "")
        entities["departureDate"] = flight.get("departureDate", "")
        entities["returnDate"] = flight.get("returnDate", "")
        entities["tripType"] = flight.get("tripType", "roundtrip")
        passengers = flight.get("passengers", {})
        entities["adults"] = passengers.get("adults", 1)
        entities["children"] = passengers.get("children", 0)

    elif travel_type == "hotel" and "hotel" in current_data:
        hotel = current_data["hotel"]
        entities["arrival"] = hotel.get("destination", "")
        entities["departureDate"] = hotel.get("checkinDate", "")
        entities["returnDate"] = hotel.get("checkoutDate", "")
        entities["rooms"] = hotel.get("rooms", 1)
        guests = hotel.get("guests", {})
        entities["adults"] = guests.get("adults", 2)
        entities["children"] = guests.get("children", 0)
        entities["breakfast"] = hotel.get("breakfast", False)

    elif travel_type == "car" and "car" in current_data:
        car = current_data["car"]
        entities["departureDate"] = car.get("pickupDateTime", "")
        entities["returnDate"] = car.get("dropoffDateTime", "")

    return entities


def action_handler_node(state: TravelState) -> TravelState:
    """사용자 액션(버튼 클릭 등) 처리 노드"""
    user_action = state.get("user_action", {})
    action_type = user_action.get("action", "")
    current_data = user_action.get("data", {})
    surface_id = user_action.get("surfaceId", "")

    messages = []

    # 여행 타입 선택 액션
    if action_type.startswith("select-"):
        travel_type = action_type.replace("select-", "")

        # 검색 결과에서 온 경우 기존 Surface 삭제
        if surface_id and surface_id.endswith("-results"):
            messages.append({"deleteSurface": {"surfaceId": surface_id}})

        generator = get_form_generator(travel_type)
        if generator:
            # 기존 데이터가 있으면 유지
            entities = _extract_entities_from_data(current_data, travel_type)
            messages.extend(generator.generate(entities))

    # 뒤로가기 액션
    elif action_type == "back":
        messages.extend(get_initial_ui())

    # 검색 액션
    elif action_type.startswith("search-"):
        result_type = action_type.replace("search-", "")  # flights, hotels, cars
        generator = get_results_generator(result_type)
        if generator:
            messages.append({"assistantMessage": "검색 결과를 찾았어요!"})
            messages.extend(generator.generate(current_data))
        else:
            messages.append({"assistantMessage": "검색 결과를 불러오는 중입니다..."})

    return {"messages": messages}
