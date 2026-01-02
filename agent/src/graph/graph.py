"""LangGraph 그래프 정의"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

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


# 싱글톤: 체크포인터 (세션별 대화 기록 자동 관리)
_checkpointer = MemorySaver()

# 싱글톤: 컴파일된 그래프
_compiled_graph = None


def get_travel_graph():
    """싱글톤 그래프 반환 (체크포인터 포함)"""
    global _compiled_graph
    if _compiled_graph is None:
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

        # 체크포인터와 함께 컴파일
        _compiled_graph = graph.compile(checkpointer=_checkpointer)

    return _compiled_graph
