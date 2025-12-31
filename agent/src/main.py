"""FastAPI 엔트리포인트 - WebSocket 기반 A2UI 통신"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
from dotenv import load_dotenv

from .agent import TravelAgent

load_dotenv()

app = FastAPI(title="Travel Booking Agent")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    """WebSocket 연결 관리"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.agents: dict[str, TravelAgent] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.agents[client_id] = TravelAgent()

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.agents:
            del self.agents[client_id]

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    def get_agent(self, client_id: str) -> TravelAgent | None:
        return self.agents.get(client_id)


manager = ConnectionManager()


@app.websocket("/ws/chat/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)

    agent = manager.get_agent(client_id)
    if agent:
        # 초기 여행 타입 선택 UI 전송
        initial_messages = agent.get_initial_ui()
        for msg in initial_messages:
            await manager.send_message(client_id, msg)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # 사용자 메시지 또는 userAction 처리
            if agent:
                responses = await agent.handle_message(message)
                for response in responses:
                    await manager.send_message(client_id, response)

    except WebSocketDisconnect:
        manager.disconnect(client_id)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
