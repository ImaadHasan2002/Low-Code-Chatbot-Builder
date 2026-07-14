from bson import ObjectId

from app.models.background_job import BackgroundJob

class BackgroundJobRepository:
    def _object_id(self, value) -> ObjectId:
        return value if isinstance(value, ObjectId) else ObjectId(str(value))

    async def create_job(self, job: BackgroundJob):
        await job.insert()
        return job

    async def get_job(self, job_id: str):
        return await BackgroundJob.get(self._object_id(job_id))

    async def get_jobs_by_workspace(self, workspace_id: str, job_type: str | None = None):
        filters = [BackgroundJob.workspace_id == self._object_id(workspace_id)]
        if job_type:
            filters.append(BackgroundJob.job_type == job_type)
        return await BackgroundJob.find(*filters).sort("-created_at").to_list()

    async def update_job(self, job_id: str, job: BackgroundJob):
        await job.save()
        return job

    async def delete_job(self, job_id: str):
        job = await self.get_job(job_id)
        if job:
            await job.delete()

    async def get_all_jobs(self):
        return await BackgroundJob.find_all().sort("-created_at").to_list()

