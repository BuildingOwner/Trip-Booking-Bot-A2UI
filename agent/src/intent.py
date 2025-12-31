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
        if not self.client:
            # API 키 없으면 키워드 기반 분석
            return self._keyword_based_analysis(text)

        prompt = """사용자의 여행 관련 요청을 분석하세요.

다음 중 하나의 의도를 JSON으로 반환하세요:
- flight: 항공권 예약
- hotel: 호텔 예약
- car: 렌터카 예약
- package: 패키지 여행
- unknown: 파악 불가

추출 가능한 정보도 포함하세요:
- destination: 목적지
- departure: 출발지
- date: 날짜
- passengers: 인원

JSON만 반환하세요. 예시:
{"type": "flight", "destination": "제주", "departure": "서울"}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"}
            )

            result = response.choices[0].message.content
            return json.loads(result)

        except Exception as e:
            print(f"Intent analysis error: {e}")
            return self._keyword_based_analysis(text)

    def _keyword_based_analysis(self, text: str) -> dict:
        """키워드 기반 간단한 의도 분석 (폴백)"""
        text_lower = text.lower()

        if any(kw in text_lower for kw in ["항공", "비행기", "flight", "fly"]):
            return {"type": "flight"}
        elif any(kw in text_lower for kw in ["호텔", "숙소", "hotel", "stay"]):
            return {"type": "hotel"}
        elif any(kw in text_lower for kw in ["렌터카", "차량", "car", "rent"]):
            return {"type": "car"}
        elif any(kw in text_lower for kw in ["패키지", "여행", "package", "tour"]):
            return {"type": "package"}

        return {"type": "unknown"}
