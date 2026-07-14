from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from ...core.security import get_current_user
from ...models.workspace import Workspace
from ...services.chatbot_service import ChatbotService

router = APIRouter()


@router.post("/query")
async def query_chatbot(
    workspace_id: str,
    query: str,
    current_user=Depends(get_current_user),
) -> dict:
    try:
        workspace = await Workspace.get(ObjectId(workspace_id))
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")

        chatbot_service = ChatbotService(workspace_id=workspace_id)
        await chatbot_service.load_workspace_config()

        response = await chatbot_service.generate_response_with_retrieval(
            query=query,
            save=True,
            user_id=str(current_user.id),
        )

        return {"response": response}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def provide_feedback(
    conversation_id: str,
    feedback: str,
    current_user=Depends(get_current_user),
) -> dict:
    chatbot_service = ChatbotService()
    updated = await chatbot_service.update_feedback(conversation_id, feedback)
    if not updated:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Feedback recorded successfully"}
