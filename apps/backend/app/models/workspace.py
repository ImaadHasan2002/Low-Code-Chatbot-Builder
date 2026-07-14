from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId
from beanie import Document

class WorkspaceCreate(BaseModel):
    name: str
    website_url: Optional[str] = None
    crawl_max_pages: int = 25
    crawl_max_depth: int = 2
    crawl_include_paths: List[str] = Field(default_factory=list)
    crawl_exclude_paths: List[str] = Field(default_factory=list)

class Workspace(Document):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    owner_id: PyObjectId
    theme_config_id: Optional[PyObjectId] = None
    advanced_config_id: Optional[PyObjectId] = None
    name: str
    members: List[PyObjectId] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {ObjectId: str}

    class Settings:
        name = "workspaces"
