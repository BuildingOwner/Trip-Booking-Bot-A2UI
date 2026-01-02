"""사용자 액션 처리 노드"""

from ..graph.state import TravelState
from ..forms import get_form_generator
from .ui import get_initial_ui


def action_handler_node(state: TravelState) -> TravelState:
    """사용자 액션(버튼 클릭 등) 처리 노드"""
    user_action = state.get("user_action", {})
    action_type = user_action.get("action", "")

    messages = []

    # 여행 타입 선택 액션
    if action_type.startswith("select-"):
        travel_type = action_type.replace("select-", "")
        generator = get_form_generator(travel_type)
        if generator:
            messages.extend(generator.generate())

    # 뒤로가기 액션
    elif action_type == "back":
        messages.extend(get_initial_ui())

    # 검색 액션
    elif action_type.startswith("search-"):
        messages.append(
            {
                "updateComponents": {
                    "surfaceId": "search-results",
                    "components": [
                        {
                            "id": "root",
                            "component": "Text",
                            "text": "검색 결과를 불러오는 중...",
                        }
                    ],
                }
            }
        )

    return {"messages": messages}
