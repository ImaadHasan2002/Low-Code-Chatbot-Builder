from beanie import Document
from pydantic import Field
from .user import PyObjectId
from datetime import datetime
from typing import Any, Dict, Literal, Optional

class BackgroundJob(Document):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    workspace_id: PyObjectId
    user_id: PyObjectId
    job_type: str
    status: Literal["pending", "running", "completed", "failed"]
    payload: Dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None
    processed_items: int = 0
    total_items: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


