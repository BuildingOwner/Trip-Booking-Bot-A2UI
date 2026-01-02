"""여행 예약 에이전트 - LLM 기반 의도 분석 및 폼 생성"""

import os
from openai import OpenAI
from .intent import IntentAnalyzer
from .forms import get_form_generator


class TravelAgent:
    """여행 예약 챗봇 에이전트"""

    def __init__(self):
        self.intent_analyzer = IntentAnalyzer()
        self.current_surface: str | None = None
        self.data_model: dict = {}
        # LLM 클라이언트 초기화
        api_key = os.getenv("OPENAI_API_KEY")
        self.llm_client = OpenAI(api_key=api_key) if api_key else None
        # 대화 히스토리 (멀티턴 지원)
        self.conversation_history: list[dict] = []
        self.max_history = 20  # 최대 저장할 대화 수

    def get_initial_ui(self) -> list[dict]:
        """초기 여행 타입 선택 UI 반환"""
        messages = []

        # Surface 생성
        messages.append({
            "createSurface": {
                "surfaceId": "travel-type-selector",
                "catalogId": "travel-booking"
            }
        })

        # 컴포넌트 정의
        messages.append({
            "updateComponents": {
                "surfaceId": "travel-type-selector",
                "components": [
                    {
                        "id": "root",
                        "component": "Column",
                        "children": ["header", "type-cards"]
                    },
                    {
                        "id": "header",
                        "component": "Text",
                        "text": "어떤 여행을 계획하고 계신가요?",
                        "style": "headline"
                    },
                    {
                        "id": "type-cards",
                        "component": "Row",
                        "children": ["flight-card", "hotel-card", "car-card", "package-card"]
                    },
                    {
                        "id": "flight-card",
                        "component": "Card",
                        "children": ["flight-icon", "flight-label"],
                        "action": "select-flight"
                    },
                    {
                        "id": "flight-icon",
                        "component": "Icon",
                        "icon": "airplane"
                    },
                    {
                        "id": "flight-label",
                        "component": "Text",
                        "text": "항공권"
                    },
                    {
                        "id": "hotel-card",
                        "component": "Card",
                        "children": ["hotel-icon", "hotel-label"],
                        "action": "select-hotel"
                    },
                    {
                        "id": "hotel-icon",
                        "component": "Icon",
                        "icon": "hotel"
                    },
                    {
                        "id": "hotel-label",
                        "component": "Text",
                        "text": "호텔"
                    },
                    {
                        "id": "car-card",
                        "component": "Card",
                        "children": ["car-icon", "car-label"],
                        "action": "select-car"
                    },
                    {
                        "id": "car-icon",
                        "component": "Icon",
                        "icon": "car"
                    },
                    {
                        "id": "car-label",
                        "component": "Text",
                        "text": "렌터카"
                    },
                    {
                        "id": "package-card",
                        "component": "Card",
                        "children": ["package-icon", "package-label"],
                        "action": "select-package"
                    },
                    {
                        "id": "package-icon",
                        "component": "Icon",
                        "icon": "package"
                    },
                    {
                        "id": "package-label",
                        "component": "Text",
                        "text": "패키지"
                    }
                ]
            }
        })

        self.current_surface = "travel-type-selector"
        return messages

    async def handle_message(self, message: dict) -> list[dict]:
        """사용자 메시지/액션 처리"""
        responses = []

        # userAction 처리
        if "userAction" in message:
            action = message["userAction"]
            action_type = action.get("action", "")

            # 여행 타입 선택
            if action_type.startswith("select-"):
                travel_type = action_type.replace("select-", "")
                responses.extend(self._show_booking_form(travel_type))

            # 뒤로가기
            elif action_type == "back":
                responses.extend(self.get_initial_ui())

            # 검색
            elif action_type.startswith("search-"):
                data = action.get("data", {})
                responses.extend(self._handle_search(action_type, data))

        # 텍스트 메시지 처리 (자연어 입력)
        elif "text" in message:
            text = message["text"]
            print(f"[DEBUG] User text: {text}")
            intent = await self.intent_analyzer.analyze(text)
            print(f"[DEBUG] Intent result: {intent}")
            responses.extend(await self._handle_intent(intent, text))
            print(f"[DEBUG] Responses: {responses}")

        return responses

    def _show_booking_form(self, travel_type: str) -> list[dict]:
        """예약 유형별 폼 표시"""
        generator = get_form_generator(travel_type)
        if generator:
            return generator.generate()
        return []

    def _handle_search(self, action_type: str, data: dict) -> list[dict]:
        """검색 처리 (Mock 데이터 반환)"""
        # TODO: Phase 4에서 구현
        return [{
            "updateComponents": {
                "surfaceId": "search-results",
                "components": [
                    {
                        "id": "root",
                        "component": "Text",
                        "text": "검색 결과를 불러오는 중..."
                    }
                ]
            }
        }]

    async def _handle_intent(self, intent: dict, user_text: str) -> list[dict]:
        """의도 분석 결과 처리"""
        intent_type = intent.get("type")

        # 사용자 메시지를 히스토리에 추가
        self._add_to_history("user", user_text)

        # 여행 타입별 응답 메시지
        type_messages = {
            "flight": "항공권 예약을 도와드릴게요! 아래 정보를 입력해주세요.",
            "hotel": "호텔 예약을 도와드릴게요! 원하시는 조건을 입력해주세요.",
            "car": "렌터카 예약을 도와드릴게요! 필요한 정보를 입력해주세요.",
            "package": "패키지 여행을 도와드릴게요! 원하시는 조건을 입력해주세요.",
        }

        if intent_type in type_messages:
            assistant_msg = type_messages[intent_type]
            # 응답을 히스토리에 추가
            self._add_to_history("assistant", assistant_msg)

            responses = []
            responses.append({"assistantMessage": assistant_msg})
            responses.extend(self._show_booking_form(intent_type))
            return responses

        # unknown이거나 인식 못한 경우 - LLM으로 일반 대화 응답
        assistant_msg = await self._generate_conversation_response(user_text)
        # 응답을 히스토리에 추가
        self._add_to_history("assistant", assistant_msg)

        return [{"assistantMessage": assistant_msg}]

    def _add_to_history(self, role: str, content: str):
        """대화 히스토리에 메시지 추가"""
        self.conversation_history.append({"role": role, "content": content})
        # 최대 개수 초과 시 오래된 것부터 제거
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    async def _generate_conversation_response(self, user_text: str) -> str:
        """LLM을 사용하여 일반 대화 응답 생성 (멀티턴 지원)"""
        if not self.llm_client:
            return "죄송해요, 지금은 일반 대화가 어려워요. 항공권, 호텔, 렌터카 예약을 도와드릴 수 있어요!"

        try:
            # 시스템 메시지 + 대화 히스토리 구성
            messages = [
                {
                    "role": "system",
                    "content": """당신은 친절한 여행 예약 도우미입니다.
사용자와 자연스럽게 대화하면서 여행 계획을 도와주세요.

규칙:
- 친근하고 도움이 되는 톤으로 대화하세요
- 이전 대화 맥락을 기억하고 자연스럽게 이어가세요
- 여행 관련 질문에는 유용한 정보를 제공하세요
- 예약이 필요한 경우 "항공권 예약", "호텔 예약", "렌터카 예약"을 안내하세요
- 응답은 2-3문장 정도로 간결하게 하세요
- 한국어로 응답하세요"""
                }
            ]

            # 이전 대화 히스토리 추가 (현재 메시지 제외 - 이미 히스토리에 추가됨)
            # 마지막 user 메시지는 제외 (아래서 다시 추가)
            history_without_current = self.conversation_history[:-1] if self.conversation_history else []
            messages.extend(history_without_current)

            # 현재 사용자 메시지 추가
            messages.append({"role": "user", "content": user_text})

            print(f"[DEBUG] Conversation history length: {len(self.conversation_history)}")

            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Conversation generation error: {e}")
            return "죄송해요, 잠시 문제가 생겼어요. 항공권, 호텔, 렌터카 예약을 도와드릴 수 있어요!"
