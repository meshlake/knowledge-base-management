from pydantic import BaseModel, Field, validator
from pydantic import BaseModel
from datetime import datetime
from typing import List
from app.models.knowledge_base import KnowledgeBase

class ChatbotBase(BaseModel):
    id: int = Field(0, description="chatbot id")
    name: str = Field(..., description="name of chatbot")
    description: str = Field(..., description="description for the chatbot")
    userId: int = Field(-1, alias="user_id", description="user id of the user who created the chatbot")
    createdAt: int = Field(0, description="time in milliseconds since epoch when the base was created")
    updatedAt: int = Field(0, description="time in milliseconds since epoch when the base was last updated")
    knowledgeBases: List[KnowledgeBase] = []

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