from app.models.background_job import BackgroundJob

class BackgroundJobRepository:

    async def create_job(self, job: BackgroundJob):
        await job.insert()
        return job

    async def get_job(self, job_id: str):
        return await BackgroundJob.get(job_id)

    async def update_job(self, job_id: str, job: BackgroundJob):
        await job.save()
        return job

    async def delete_job(self, job_id: str):
        await BackgroundJob.delete(job_id)

