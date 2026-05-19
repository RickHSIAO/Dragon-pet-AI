"""
API routes for dragon-pet-ai backend.

TASK-005 keeps the runtime skeleton stable while moving mock chat generation
behind service modules.

Safety boundaries:
- /chat does not call any external AI API.
- /chat does not execute shell commands.
- /chat does not read or write user files.
- /chat does not read or write the database.
"""

from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import generate_mock_chat_reply

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Liveness check endpoint.
    Returns ok status if the backend is running.
    """
    return {"status": "ok", "service": "dragon-pet-ai"}


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Mock chat endpoint.

    The route only adapts the API request/response and delegates mock reply
    generation to the chat service.
    """
    return ChatResponse(**generate_mock_chat_reply(request.message))
