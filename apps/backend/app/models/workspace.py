from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId
from .theme import Theme
from beanie import Document

class WorkspaceCreate(BaseModel):
    name: str

class Workspace(Document):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    owner_id: PyObjectId
    theme_config_id: PyObjectId
    advanced_config_id: PyObjectId
    name: str
    members: List[PyObjectId] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {ObjectId: str}

    class Settings:
        name = "workspaces"
