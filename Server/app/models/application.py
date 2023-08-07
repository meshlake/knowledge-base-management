from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.models.chatbot import ChatbotSimple
from app.entities.applications import Category


class ApplicationProperties(BaseModel):
    webhook_url: str = Field(None)
    puppet_token: str = Field(None)
    private_enable: bool = Field(True)
    room_enable: bool = Field(True)


class ApplicationCreate(BaseModel):
    name: str
    description: str = Field(None)
    chatbot_id: int
    category: Category
    properties: ApplicationProperties = Field(None)


class ApplicationUpdate(BaseModel):
    name: str = Field(None)
    description: str = Field(None)
    chatbot_id: int = Field(None)
    properties: ApplicationProperties = Field(None)


class Application(BaseModel):
    id: int
    name: str
    description: str
    user_id: str
    category: Category
    createdAt: int = Field(0)
    updatedAt: int = Field(0)
    api_key: str
    properties: ApplicationProperties = Field(None)
    chatbot: ChatbotSimple = Field(None)

    class Config:
        orm_mode = True

    @validator("createdAt", "updatedAt", pre=True)
    @classmethod
    def datetime_convert(cls, v):
        if isinstance(v, int):
            return v
        elif isinstance(v, datetime):
            return int(v.timestamp() * 1000)
        return v
