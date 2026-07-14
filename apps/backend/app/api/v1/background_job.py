from fastapi import APIRouter, Depends, HTTPException, status

from ...core.security import get_current_user, get_current_workspace_id
from ...services.background_job_service import BackgroundJobService

router = APIRouter()


@router.post("/create")
async def create_background_job(
    job_type: str,
    current_user=Depends(get_current_user),
    workspace_id: str = Depends(get_current_workspace_id),
) -> dict:
    background_job_service = BackgroundJobService()
    job = await background_job_service.create_job(job_type, current_user.id, workspace_id)
    return {"message": "Background job created successfully", "job_id": str(job.id)}


@router.get("/{job_id}")
async def get_background_job(
    job_id: str,
    current_user=Depends(get_current_user),
) -> dict:
    background_job_service = BackgroundJobService()
    job = await background_job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return {"job_id": str(job.id), "status": job.status, "job_type": job.job_type}
