"""LangGraph 그래프 정의"""

from langgraph.graph import StateGraph, END

from .state import TravelState
from ..nodes import (
    intent_node,
    form_generator_node,
    conversation_node,
    action_handler_node,
)


def route_input(state: TravelState) -> str:
    """입력 타입에 따라 라우팅"""
    if state.get("user_action"):
        return "action_handler"
    elif state.get("user_message"):
        return "intent"
    return END


def route_intent(state: TravelState) -> str:
    """의도 분석 결과에 따라 라우팅"""
    intent_type = state.get("intent_type", "unknown")

    if intent_type in ("flight", "hotel", "car", "package"):
        return "form_generator"
    else:
        return "conversation"


def create_travel_graph():
    """여행 예약 에이전트 그래프 생성"""

    # 그래프 생성
    graph = StateGraph(TravelState)

    # 노드 추가
    graph.add_node("intent", intent_node)
    graph.add_node("form_generator", form_generator_node)
    graph.add_node("conversation", conversation_node)
    graph.add_node("action_handler", action_handler_node)

    # 시작점: 조건부 엔트리 포인트
    graph.set_conditional_entry_point(route_input)

    # intent 노드 이후 조건부 라우팅
    graph.add_conditional_edges(
        "intent",
        route_intent,
        {
            "form_generator": "form_generator",
            "conversation": "conversation",
        },
    )

    # 각 노드에서 종료
    graph.add_edge("form_generator", END)
    graph.add_edge("conversation", END)
    graph.add_edge("action_handler", END)

    # 컴파일
    return graph.compile()
