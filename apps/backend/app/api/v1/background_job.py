from fastapi import APIRouter, HTTPException
from bson.objectid import ObjectId

from ...services.background_job_service import BackgroundJobService
from ...core.security import get_current_user

router = APIRouter()

@router.post("/create")
async def create_background_job(
    job_type: str,
    current_user = Depends(get_current_user)
) -> dict:
    background_job_service = BackgroundJobService()
    job = await background_job_service.create_job(job_type, current_user.id)
    return {"message": "Background job created successfully"}