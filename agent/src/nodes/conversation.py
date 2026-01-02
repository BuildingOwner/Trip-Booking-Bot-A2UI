"""일반 대화 노드"""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from ..graph.state import TravelState
from .llm import get_llm, LLM_REASONING_EFFORT


SYSTEM_PROMPT = """당신은 친절한 여행 예약 도우미입니다.
사용자와 자연스럽게 대화하면서 여행 계획을 도와주세요.

규칙:
- 친근하고 도움이 되는 톤으로 대화하세요
- 이전 대화 맥락을 기억하고 자연스럽게 이어가세요
- 여행 관련 질문에는 유용한 정보를 제공하세요
- 예약이 필요한 경우 "항공권 예약", "호텔 예약", "렌터카 예약"을 안내하세요
- 응답은 2-3문장 정도로 간결하게 하세요
- 한국어로 응답하세요"""


def _extract_reasoning_summary(response) -> str | None:
    """응답에서 reasoning summary 추출"""
    # content가 리스트인 경우 (responses/v1 형식)
    if hasattr(response, "content") and isinstance(response.content, list):
        for item in response.content:
            if isinstance(item, dict) and item.get("type") == "reasoning":
                # reasoning 항목에서 summary 추출
                summary_list = item.get("summary", [])
                if summary_list:
                    return "\n".join(s.get("text", "") for s in summary_list if s.get("text"))

    # additional_kwargs에서 추출 시도
    if hasattr(response, "additional_kwargs"):
        reasoning = response.additional_kwargs.get("reasoning")
        if reasoning and isinstance(reasoning, dict):
            summary = reasoning.get("summary")
            if summary:
                return summary

    return None


def _extract_text_content(response) -> str:
    """응답에서 텍스트 컨텐츠 추출"""
    if hasattr(response, "content"):
        # content가 문자열인 경우
        if isinstance(response.content, str):
            return response.content
        # content가 리스트인 경우 (responses/v1 형식)
        if isinstance(response.content, list):
            texts = []
            for item in response.content:
                if isinstance(item, dict) and item.get("type") == "text":
                    texts.append(item.get("text", ""))
                elif isinstance(item, str):
                    texts.append(item)
            return "".join(texts)
    return str(response)


def conversation_node(state: TravelState) -> TravelState:
    """일반 대화 응답 노드"""
    user_message = state.get("user_message", "")
    chat_history = state.get("chat_history", [])

    llm = get_llm()

    if not llm:
        fallback_msg = "죄송해요, 지금은 일반 대화가 어려워요. 항공권, 호텔, 렌터카 예약을 도와드릴 수 있어요!"
        return {
            "messages": [{"assistantMessage": fallback_msg}],
            "chat_history": [
                HumanMessage(content=user_message),
                AIMessage(content=fallback_msg),
            ],
        }

    try:
        # 메시지 구성
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        messages.extend(chat_history)
        messages.append(HumanMessage(content=user_message))

        # invoke 호출 (reasoning effort 설정)
        invoke_kwargs = {}
        if LLM_REASONING_EFFORT:
            invoke_kwargs["reasoning"] = {
                "effort": LLM_REASONING_EFFORT,
                "summary": "auto"
            }

        response = llm.invoke(messages, **invoke_kwargs)

        # 텍스트와 reasoning summary 추출
        assistant_msg = _extract_text_content(response)
        reasoning_summary = _extract_reasoning_summary(response)

        # 응답 메시지 구성
        response_msg = {"assistantMessage": assistant_msg}
        if reasoning_summary:
            response_msg["reasoning"] = reasoning_summary

        return {
            "messages": [response_msg],
            "chat_history": [
                HumanMessage(content=user_message),
                AIMessage(content=assistant_msg),
            ],
        }

    except Exception as e:
        print(f"[Conversation Node] Error: {e}")
        fallback_msg = "죄송해요, 잠시 문제가 생겼어요. 항공권, 호텔, 렌터카 예약을 도와드릴 수 있어요!"
        return {"messages": [{"assistantMessage": fallback_msg}]}
