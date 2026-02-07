from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form, Query, Cookie, Body
from typing import List
from bson import ObjectId

from ...models.knowledge_base import KnowledgeBase
from ...services.knowledge_base_service import KnowledgeBaseService
from ...services.background_job_service import BackgroundJobService
from ...core.security import get_current_user, get_current_workspace, get_current_workspace_id

router = APIRouter()

@router.post("/upload")
async def upload_pdf(
    workspace_id: str = Form(...),
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
) -> dict:
    
    kb_service = KnowledgeBaseService(workspace_id=ObjectId(workspace_id))
    result = await kb_service.upload_pdf_and_create_knowledge_base(
        workspace_id=ObjectId(workspace_id),
        file=file,
        user_id=current_user.id
    )
    print(f"Result: {result}")
    return {"message": "File uploaded successfully", "knowledge_base_id": str(result)}

@router.post("/link")
async def scrape_link(
    workspace_id: str = Depends(get_current_workspace_id),
    link: str = Body(...),
    current_user = Depends(get_current_user)
) -> dict:
    kb_service = KnowledgeBaseService(workspace_id=ObjectId(workspace_id))
    result = await kb_service.scrape_link(
        workspace_id=ObjectId(workspace_id),
        link=link,
    )
    return {"message": "Link uploaded successfully", "knowledge_base_id": str(result)} 

@router.get("/links")
async def get_links(
    workspace_id: str = Query(...),
    current_user = Depends(get_current_user)
) -> dict:
    print("workspace_id in get_links: ", workspace_id)
    kb_service = KnowledgeBaseService(workspace_id=ObjectId(workspace_id))
    links = await kb_service.get_knowledge_base_links(ObjectId(workspace_id))
    return {"links": links}

@router.get("/pdfs", response_model=List[KnowledgeBase])
async def get_knowledge_bases(
    workspace_id: str = Query(...),
    current_user = Depends(get_current_user)
) -> List[KnowledgeBase]:
    print("workspace_id in get_knowledge_bases: ", workspace_id)
    kb_service = KnowledgeBaseService(workspace_id=ObjectId(workspace_id))
    knowledge_bases = await kb_service.get_by_workspace(ObjectId(workspace_id))
    return knowledge_bases

@router.delete("/{knowledge_base_id}")
async def delete_knowledge_base(
    knowledge_base_id: str,
    workspace_id: str = Query(...),
    current_user = Depends(get_current_user)
):
    kb_service = KnowledgeBaseService(workspace_id=ObjectId(workspace_id))
    await kb_service.delete_knowledge_base(knowledge_base_id, workspace_id)
    return {"message": "Knowledge base deleted successfully"}
