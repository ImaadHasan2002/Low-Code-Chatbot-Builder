from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId
from beanie import Document

class KnowledgeBaseType(str, Enum):
    PDF = "pdf"
    LINK = "link"
    VIDEO = "video"
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    XLSX = "xlsx"
    
class KnowledgeBase(Document):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    workspace_id: PyObjectId
    type: KnowledgeBaseType
    file_url: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    name: str

    class Config:
        json_encoders = {ObjectId: str}

    class Settings:
        name = "knowledge_bases"
