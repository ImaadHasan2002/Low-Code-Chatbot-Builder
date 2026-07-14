from typing import Optional

from beanie import Document
from pydantic import BaseModel, ConfigDict, Field, model_validator
from bson.objectid import ObjectId
from .user import PyObjectId


_CAMEL_TO_SNAKE = {
    "primaryColor": "primary_color",
    "secondaryColor": "secondary_color",
    "textColor": "text_color",
    "headerText": "header_text",
    "inputPlaceholder": "input_placeholder",
    "borderRadius": "border_radius",
    "showHeader": "show_header",
}


class ThemeUpdate(BaseModel):
    """Payload for creating/updating a theme. All fields optional."""

    model_config = ConfigDict(extra="ignore")

    theme: Optional[str] = None
    position: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    text_color: Optional[str] = None
    header_text: Optional[str] = None
    input_placeholder: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    border_radius: Optional[str] = None
    launcher: Optional[bool] = None
    show_header: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def accept_camel_case_keys(cls, data):
        if not isinstance(data, dict):
            return data
        return {_CAMEL_TO_SNAKE.get(key, key): value for key, value in data.items()}


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
