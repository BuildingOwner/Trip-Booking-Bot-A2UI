"""LLM 클라이언트 및 설정 모듈"""

import os
from langchain_openai import ChatOpenAI


# 환경변수에서 모델 설정 (기본값: gpt-4o-mini)
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))

# Reasoning effort: 환경변수로 직접 설정하거나, 모델에 따라 자동 설정
# 직접 설정: LLM_REASONING_EFFORT=high
# 자동 설정: LLM_REASONING_EFFORT=auto (GPT-5면 medium, 아니면 없음)
_reasoning_env = os.getenv("LLM_REASONING_EFFORT", "auto")


def get_reasoning_effort() -> str:
    """모델에 따른 reasoning effort 반환"""
    if _reasoning_env == "auto":
        # GPT-5 계열이면 medium, 아니면 빈 문자열
        if LLM_MODEL.startswith("gpt-5"):
            return "medium"
        return ""
    return _reasoning_env


LLM_REASONING_EFFORT = get_reasoning_effort()

_llm_instance = None


def get_llm() -> ChatOpenAI | None:
    """ChatOpenAI 인스턴스 싱글톤"""
    global _llm_instance
    if _llm_instance is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            # GPT-5 모델이면 Responses API 사용
            use_responses = LLM_MODEL.startswith("gpt-5")

            _llm_instance = ChatOpenAI(
                model=LLM_MODEL,
                api_key=api_key,
                max_tokens=LLM_MAX_TOKENS,
                use_responses_api=use_responses,
                output_version="responses/v1" if use_responses else None,
            )

            # 로그 출력
            reasoning_info = f", reasoning={LLM_REASONING_EFFORT}" if LLM_REASONING_EFFORT else ""
            print(f"[LLM] Model: {LLM_MODEL}, max_tokens: {LLM_MAX_TOKENS}{reasoning_info}")
    return _llm_instance
