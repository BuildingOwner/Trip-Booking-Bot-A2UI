"""FastAPI 엔트리포인트 - REST API 기반 A2UI 통신"""

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from .agent import TravelAgent

load_dotenv()

app = FastAPI(title="Travel Booking Agent")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경: 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response 모델
class UserAction(BaseModel):
    surfaceId: str
    componentId: str
    action: str
    data: Optional[dict] = None


class ChatRequest(BaseModel):
    text: Optional[str] = None
    userAction: Optional[UserAction] = None


# 클라이언트별 에이전트 관리
agents: dict[str, TravelAgent] = {}


def get_or_create_agent(client_id: str) -> TravelAgent:
    """클라이언트별 에이전트 가져오기 또는 생성"""
    if client_id not in agents:
        agents[client_id] = TravelAgent()
    return agents[client_id]


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/chat/init")
async def chat_init(x_client_id: str = Header(alias="X-Client-ID")):
    """초기화 - 에이전트 생성만 하고 UI는 보내지 않음"""
    get_or_create_agent(x_client_id)
    # 초기 인사 메시지만 반환 (UI 없음)
    return {
        "messages": [{
            "assistantMessage": "안녕하세요! 여행 예약을 도와드릴게요. 항공권, 호텔, 렌터카 중 무엇을 예약하시겠어요?"
        }]
    }


@app.post("/chat")
async def chat(request: ChatRequest, x_client_id: str = Header(alias="X-Client-ID")):
    """채팅 메시지 처리"""
    agent = get_or_create_agent(x_client_id)

    # 요청을 dict로 변환
    message = {}
    if request.text:
        message["text"] = request.text
    elif request.userAction:
        message["userAction"] = request.userAction.model_dump()

    # 에이전트에서 응답 처리
    responses = await agent.handle_message(message)

    # 모든 메시지를 배열로 반환
    return {"messages": responses}
