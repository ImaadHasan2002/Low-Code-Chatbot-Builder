from typing import Any, List, Optional

from bson import ObjectId
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field

from ...core.security import get_current_user
from ...models.knowledge_base import KnowledgeBase, KnowledgeBaseType
from ...services.background_job_service import BackgroundJobService
from ...services.knowledge_base_service import KnowledgeBaseService

router = APIRouter()


class CrawlRequest(BaseModel):
    base_url: str = Field(..., min_length=1)
    max_pages: int = Field(default=25, ge=1, le=500)
    max_depth: int = Field(default=2, ge=0, le=10)
    include_paths: List[str] = Field(default_factory=list)
    exclude_paths: List[str] = Field(default_factory=list)


def _require_object_id(value: str, label: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {label}",
        )
    return ObjectId(value)


def _crawl_request_from_payload(payload: Any) -> CrawlRequest:
    if isinstance(payload, str):
        return CrawlRequest(base_url=payload)
    if isinstance(payload, dict):
        if "link" in payload and "base_url" not in payload:
            payload = {**payload, "base_url": payload["link"]}
        return CrawlRequest(**payload)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Expected a URL string or crawl settings object",
    )


def _job_to_dict(job) -> dict:
    return {
        "job_id": str(job.id),
        "workspace_id": str(job.workspace_id),
        "job_type": job.job_type,
        "status": job.status,
        "message": job.message,
        "processed_items": job.processed_items,
        "total_items": job.total_items,
        "payload": job.payload,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "completed_at": job.completed_at,
    }


@router.post("/upload")
async def upload_file(
    workspace_id: str = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
) -> dict:
    workspace_object_id = _require_object_id(workspace_id, "workspace id")
    kb_service = KnowledgeBaseService(workspace_id=workspace_object_id)
    result = await kb_service.upload_file_and_create_knowledge_base(
        workspace_id=workspace_object_id,
        file=file,
        user_id=current_user.id,
    )
    return {
        "message": "File uploaded and indexed successfully",
        "knowledge_base_id": str(result.id),
        "type": result.type,
    }


@router.post("/link")
async def scrape_link(
    payload: Any = Body(...),
    workspace_id: str = Query(...),
    current_user=Depends(get_current_user),
) -> dict:
    crawl_request = _crawl_request_from_payload(payload)
    workspace_object_id = _require_object_id(workspace_id, "workspace id")
    kb_service = KnowledgeBaseService(workspace_id=workspace_object_id)
    results = await kb_service.scrape_link(
        workspace_id=workspace_object_id,
        link=crawl_request.base_url,
        max_pages=crawl_request.max_pages,
        max_depth=crawl_request.max_depth,
        include_paths=crawl_request.include_paths,
        exclude_paths=crawl_request.exclude_paths,
    )
    return {
        "message": "Website crawled and indexed successfully",
        "knowledge_base_ids": [str(item.id) for item in results],
        "pages_indexed": len(results),
    }


@router.post("/crawl", status_code=status.HTTP_202_ACCEPTED)
async def start_crawl(
    crawl_request: CrawlRequest,
    background_tasks: BackgroundTasks,
    workspace_id: str = Query(...),
    current_user=Depends(get_current_user),
) -> dict:
    workspace_object_id = _require_object_id(workspace_id, "workspace id")
    job_service = BackgroundJobService()
    job = await job_service.create_job(
        "website_crawl",
        str(current_user.id),
        str(workspace_object_id),
        payload=crawl_request.model_dump(),
    )

    kb_service = KnowledgeBaseService(workspace_id=workspace_object_id)
    background_tasks.add_task(
        kb_service.run_crawl_job,
        job_id=str(job.id),
        workspace_id=str(workspace_object_id),
        base_url=crawl_request.base_url,
        max_pages=crawl_request.max_pages,
        max_depth=crawl_request.max_depth,
        include_paths=crawl_request.include_paths,
        exclude_paths=crawl_request.exclude_paths,
    )
    return {"message": "Crawl started", "job": _job_to_dict(job)}


@router.get("/crawl/jobs")
async def get_crawl_jobs(
    workspace_id: str = Query(...),
    current_user=Depends(get_current_user),
) -> dict:
    _require_object_id(workspace_id, "workspace id")
    jobs = await BackgroundJobService().get_workspace_jobs(workspace_id, "website_crawl")
    return {"jobs": [_job_to_dict(job) for job in jobs]}


@router.get("/crawl/jobs/{job_id}")
async def get_crawl_job(
    job_id: str,
    workspace_id: str = Query(...),
    current_user=Depends(get_current_user),
) -> dict:
    _require_object_id(workspace_id, "workspace id")
    _require_object_id(job_id, "job id")
    job = await BackgroundJobService().get_job(job_id)
    if not job or str(job.workspace_id) != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return {"job": _job_to_dict(job)}


@router.get("/links")
async def get_links(
    workspace_id: str = Query(...),
    current_user=Depends(get_current_user),
) -> dict:
    workspace_object_id = _require_object_id(workspace_id, "workspace id")
    kb_service = KnowledgeBaseService(workspace_id=workspace_object_id)
    links = await kb_service.get_knowledge_base_links(workspace_object_id)
    return {"links": links}


@router.get("/files", response_model=List[KnowledgeBase])
async def get_files(
    workspace_id: str = Query(...),
    kb_type: Optional[KnowledgeBaseType] = Query(default=None, alias="type"),
    current_user=Depends(get_current_user),
) -> List[KnowledgeBase]:
    workspace_object_id = _require_object_id(workspace_id, "workspace id")
    kb_service = KnowledgeBaseService(workspace_id=workspace_object_id)
    return await kb_service.get_by_workspace(workspace_object_id, kb_type=kb_type)


@router.get("/pdfs", response_model=List[KnowledgeBase])
async def get_knowledge_bases(
    workspace_id: str = Query(...),
    current_user=Depends(get_current_user),
) -> List[KnowledgeBase]:
    workspace_object_id = _require_object_id(workspace_id, "workspace id")
    kb_service = KnowledgeBaseService(workspace_id=workspace_object_id)
    return await kb_service.get_by_workspace(
        workspace_object_id, kb_type=KnowledgeBaseType.PDF
    )


@router.get("/{knowledge_base_id}", response_model=KnowledgeBase)
async def get_knowledge_base(
    knowledge_base_id: str,
    workspace_id: str = Query(...),
    current_user=Depends(get_current_user),
) -> KnowledgeBase:
    workspace_object_id = _require_object_id(workspace_id, "workspace id")
    kb_service = KnowledgeBaseService(workspace_id=workspace_object_id)
    return await kb_service.get_knowledge_base(
        knowledge_base_id=knowledge_base_id,
        workspace_id=workspace_object_id,
    )


@router.delete("/{knowledge_base_id}")
async def delete_knowledge_base(
    knowledge_base_id: str,
    workspace_id: str = Query(...),
    current_user=Depends(get_current_user),
):
    _require_object_id(workspace_id, "workspace id")
    kb_service = KnowledgeBaseService(workspace_id=ObjectId(workspace_id))
    await kb_service.delete_knowledge_base(knowledge_base_id, workspace_id)
    return {"message": "Knowledge base deleted successfully"}
