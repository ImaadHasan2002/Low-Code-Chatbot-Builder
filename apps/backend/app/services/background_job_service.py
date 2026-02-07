from app.models.background_job import BackgroundJob
from app.repositories.background_job_repository import BackgroundJobRepository

class BackgroundJobService:
    def __init__(self):
        self.background_job_repository = BackgroundJobRepository()

    async def create_job(self, job_type: str, user_id: str, workspace_id: str):
        job = BackgroundJob(
            job_type=job_type,
            user_id=user_id,
            status="pending",
            workspace_id=workspace_id
        )
        return await self.background_job_repository.create_job(job)

    async def get_job(self, job_id: str):
        return await self.background_job_repository.get_job(job_id)

    async def update_job_status(self, job_id: str, status: str):
        job = await self.get_job(job_id)
        job.status = status
        return await self.background_job_repository.update_job(job_id, job)

    async def update_job(self, job_id: str, job: BackgroundJob):
        return await self.background_job_repository.update_job(job_id, job)

    async def delete_job(self, job_id: str):
        return await self.background_job_repository.delete_job(job_id)

    async def get_all_jobs(self):
        return await self.background_job_repository.get_all_jobs()


