from datetime import datetime
from typing import Any, Dict, Optional

from bson import ObjectId

from app.models.background_job import BackgroundJob
from app.repositories.background_job_repository import BackgroundJobRepository

class BackgroundJobService:
    def __init__(self):
        self.background_job_repository = BackgroundJobRepository()

    def _object_id(self, value) -> ObjectId:
        return value if isinstance(value, ObjectId) else ObjectId(str(value))

    async def create_job(
        self,
        job_type: str,
        user_id: str,
        workspace_id: str,
        payload: Optional[Dict[str, Any]] = None,
    ):
        job = BackgroundJob(
            job_type=job_type,
            user_id=self._object_id(user_id),
            status="pending",
            workspace_id=self._object_id(workspace_id),
            payload=payload or {},
        )
        return await self.background_job_repository.create_job(job)

    async def get_job(self, job_id: str):
        return await self.background_job_repository.get_job(job_id)

    async def update_job_status(self, job_id: str, status: str):
        job = await self.get_job(job_id)
        job.status = status
        job.updated_at = datetime.now()
        if status in {"completed", "failed"}:
            job.completed_at = datetime.now()
        return await self.background_job_repository.update_job(job_id, job)

    async def update_job_progress(
        self,
        job_id: str,
        *,
        status: Optional[str] = None,
        message: Optional[str] = None,
        processed_items: Optional[int] = None,
        total_items: Optional[int] = None,
    ):
        job = await self.get_job(job_id)
        if status:
            job.status = status
        if message is not None:
            job.message = message
        if processed_items is not None:
            job.processed_items = processed_items
        if total_items is not None:
            job.total_items = total_items
        job.updated_at = datetime.now()
        if job.status in {"completed", "failed"}:
            job.completed_at = datetime.now()
        return await self.background_job_repository.update_job(job_id, job)

    async def update_job(self, job_id: str, job: BackgroundJob):
        return await self.background_job_repository.update_job(job_id, job)

    async def delete_job(self, job_id: str):
        return await self.background_job_repository.delete_job(job_id)

    async def get_all_jobs(self):
        return await self.background_job_repository.get_all_jobs()

    async def get_workspace_jobs(self, workspace_id: str, job_type: str | None = None):
        return await self.background_job_repository.get_jobs_by_workspace(workspace_id, job_type)


