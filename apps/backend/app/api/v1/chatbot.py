from fastapi import APIRouter, Depends, HTTPException
from bson.objectid import ObjectId

from ...services.chatbot_service import ChatbotService
from ...core.security import get_current_user
from ...models.workspace import Workspace


router = APIRouter()

@router.post("/query")
async def query_chatbot(
    workspace_id: str,
    query: str,
    user_id: str,
    current_user = Depends(get_current_user)
) -> dict:
    try:
        # Get workspace-specific configuration
        workspace = await Workspace.get(ObjectId(workspace_id))
        
        # Initialize chatbot with workspace settings
        chatbot_service = ChatbotService(workspace.settings)
        
        response = await chatbot_service.generate_response_with_retrieval(
            query=query,
            user_id=user_id,
            workspace_id=workspace_id
        )
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def provide_feedback(
    conversation_id: str,
    feedback: str,
    current_user = Depends(get_current_user)
) -> dict:
    chatbot_service = ChatbotService()
    await chatbot_service.update_feedback(conversation_id, feedback)
    return {"message": "Feedback recorded successfully"}
