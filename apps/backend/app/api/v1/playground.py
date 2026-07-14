import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from ...core.security import get_current_user
from ...models.conversation import Conversation
from ...services.chatbot_service import ChatbotService
from ...services.converstation import ConversationService

router = APIRouter()


@router.post("/")
async def create_conversation(
    conversation: Conversation,
    current_user=Depends(get_current_user),
):
    conversation_service = ConversationService()
    conversation_id = await conversation_service.create_conversation(conversation)
    return {"conversation_id": conversation_id}


@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    # Read workspace_id from query params
    # (e.g. ws://host/api/v1/playground/chat?workspace_id=xxx)
    workspace_id = websocket.query_params.get("workspace_id")
    thread_id = str(uuid.uuid4())  # isolate conversation memory per connection

    try:
        chatbot_service = ChatbotService(workspace_id=workspace_id)
        await chatbot_service.load_workspace_config()
    except Exception as e:
        await websocket.send_text(f"Error initialising chatbot: {e}")
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_text()
            try:
                response = await chatbot_service.generate_response_with_retrieval(
                    data, thread_id=thread_id
                )
                await websocket.send_text(response)
            except Exception as e:
                await websocket.send_text(f"Error generating response: {e}")
    except WebSocketDisconnect:
        pass
