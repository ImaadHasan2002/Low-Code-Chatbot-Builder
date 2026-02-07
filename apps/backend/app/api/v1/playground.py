from fastapi import APIRouter, Depends, WebSocket, Query
from app.models.conversation import Conversation
from app.core.security import get_current_user
from app.services.converstation import ConversationService
from app.services.chatbot_service import ChatbotService
router = APIRouter()

@router.post("/")
async def create_conversation(
    conversation: Conversation,
    current_user = Depends(get_current_user)
):
    print(f"Creating conversation...")
    conversation_service = ConversationService()
    conversation_id = await conversation_service.create_conversation(conversation)
    return {"conversation_id": conversation_id}

@router.websocket("/chat")
async def websocket(websocket: WebSocket):
    print("connecting to websocket...")
    await websocket.accept()
    print("websocket connected")

    # Read workspace_id from query params (e.g. ws://host/playground/chat?workspace_id=xxx)
    workspace_id = websocket.query_params.get("workspace_id")
    chatbot_service = ChatbotService(workspace_id=workspace_id)
    await chatbot_service.load_workspace_config()
    print(f"Chatbot configured for workspace: {workspace_id}")

    while True:
        data = await websocket.receive_text()
        print(f"Received message: {data}")

        try:
            response = await chatbot_service.generate_response_with_retrieval(data)
            await websocket.send_text(response)
        except Exception as e:
            await websocket.send_text(f"Error generating response: {e}")
