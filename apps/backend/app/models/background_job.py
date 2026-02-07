from beanie import Document
from pydantic import Field
from .user import PyObjectId
from datetime import datetime
from typing import Literal

class BackgroundJob(Document):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    workspace_id: PyObjectId
    user_id: PyObjectId
    job_type: str
    status: Literal["pending", "running", "completed", "failed"]
    created_at: datetime = Field(default_factory=datetime.now)


