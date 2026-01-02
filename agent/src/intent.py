"""의도 분석 모듈 - GPT 기반 사용자 의도 파악"""

import os
import json
from openai import OpenAI


class IntentAnalyzer:
    """사용자 입력에서 의도를 분석"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None

    async def analyze(self, text: str) -> dict:
        """텍스트에서 여행 관련 의도 분석"""
        print(f"[DEBUG IntentAnalyzer] Analyzing: {text}")
        print(f"[DEBUG IntentAnalyzer] OpenAI client exists: {self.client is not None}")

        if not self.client:
            # API 키 없으면 키워드 기반 분석
            print("[DEBUG IntentAnalyzer] Using keyword-based analysis (no API key)")
            return self._keyword_based_analysis(text)

        prompt = """당신은 여행 예약 의도 분석기입니다. 사용자가 **실제로 예약을 요청**하는지 판단하세요.

## 핵심 규칙
1. 사용자가 명확히 "예약", "예약하고 싶어", "예약해줘" 등 예약 의도를 표현할 때만 예약 타입으로 분류
2. 단순히 여행 관련 대화, 질문, 상담, 일정 계획 등은 "unknown"으로 분류
3. "~말고", "~아니고", "~대신" 등 부정 표현이 있으면 해당 타입 제외

## 예약 타입 분류 (명확한 예약 의도가 있을 때만)
- 항공권 예약 요청: type: "flight"
- 호텔/숙소 예약 요청: type: "hotel"
- 렌터카 예약 요청: type: "car"
- 패키지 여행 예약 요청: type: "package"
- 그 외 모든 경우: type: "unknown"

## 응답 형식 (JSON)
{"type": "flight|hotel|car|package|unknown"}

## 예시
- "항공권 예약해줘" → {"type": "flight"} (예약 요청 O)
- "호텔 예약하고 싶어" → {"type": "hotel"} (예약 요청 O)
- "제주도 여행 가려고 하는데 일정 좀 짜줘" → {"type": "unknown"} (일정 상담, 예약 X)
- "패키지 말고 자유여행 하고 싶어" → {"type": "unknown"} (패키지 거부, 상담 요청)
- "후쿠오카 3박 4일 여행 계획 세워줘" → {"type": "unknown"} (계획 상담, 예약 X)
- "비행기 vs 배 뭐가 좋아?" → {"type": "unknown"} (질문, 예약 X)
- "여행 추천해줘" → {"type": "unknown"} (추천 요청, 예약 X)
- "렌터카 빌리고 싶어" → {"type": "car"} (예약 요청 O)"""

        try:
            print("[DEBUG IntentAnalyzer] Calling GPT...")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"}
            )

            result = response.choices[0].message.content
            print(f"[DEBUG IntentAnalyzer] GPT response: {result}")
            parsed = json.loads(result)

            # GPT 판단을 신뢰 (unknown도 유효한 판단)
            print(f"[DEBUG IntentAnalyzer] Final intent: {parsed}")
            return parsed

        except Exception as e:
            print(f"[DEBUG IntentAnalyzer] Error: {e}")
            return self._keyword_based_analysis(text)

    def _keyword_based_analysis(self, text: str) -> dict:
        """키워드 기반 간단한 의도 분석 (폴백)"""
        print(f"[DEBUG Keyword] Running keyword analysis on: {text}")
        text_lower = text.lower()

        if any(kw in text_lower for kw in ["항공", "비행기", "flight", "fly"]):
            print("[DEBUG Keyword] Matched: flight")
            return {"type": "flight"}
        elif any(kw in text_lower for kw in ["호텔", "숙소", "hotel", "stay"]):
            print("[DEBUG Keyword] Matched: hotel")
            return {"type": "hotel"}
        elif any(kw in text_lower for kw in ["렌터카", "차량", "car", "rent"]):
            print("[DEBUG Keyword] Matched: car")
            return {"type": "car"}
        elif any(kw in text_lower for kw in ["패키지", "여행", "package", "tour"]):
            print("[DEBUG Keyword] Matched: package")
            return {"type": "package"}

        print("[DEBUG Keyword] No match, returning unknown")
        return {"type": "unknown"}
