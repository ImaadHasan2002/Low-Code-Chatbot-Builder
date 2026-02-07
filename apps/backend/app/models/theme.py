from beanie import Document
from pydantic import Field
from bson.objectid import ObjectId
from .user import PyObjectId

class Theme(Document):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    theme: str = Field(default="light")
    position: str = Field(default="bottom-right")
    primary_color: str = Field(default="#3B82F6")
    secondary_color: str = Field(default="#F3F4F6")
    text_color: str = Field(default="#000000")
    header_text: str = Field(default="Chat with me")
    input_placeholder: str = Field(default="Type your message here...")
    width: str = Field(default="300px")
    height: str = Field(default="500px")
    border_radius: str = Field(default="8px")
    launcher: bool = Field(default=True)
    show_header: bool = Field(default=True)

    class Config:
        json_encoders = {ObjectId: str}

    class Settings:
        name = "theme_config"
