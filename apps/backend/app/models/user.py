from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from beanie import Document


# TODO: Move this Class to some utils file
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *args, **kwargs):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class UserBase(BaseModel):
    email: EmailStr
    subscription_plan: str = "free"

class UserCreate(UserBase):
    email: EmailStr
    password: str
    subscription_plan: str = "free"

class UserInDB(Document):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: Optional[str] = None
    email: str = Field(unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    subscription_plan: str = "free"

    class Config:
        json_encoders = {ObjectId: str}

    class Settings:
        name = "users"
