from pydantic import BaseModel, Field, validator
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.models.knowledge_base import KnowledgeBaseSimple


class PromptConfig(BaseModel):
    prompt: Optional[str]
    role: Optional[str]
    name: Optional[str]
    work: Optional[str]
    style: Optional[str]

class ChatbotBase(BaseModel):
    id: int = Field(0, description="chatbot id")
    name: str = Field(..., description="name of chatbot")
    description: str = Field(None, description="description for the chatbot")
    userId: int = Field(-1, alias="user_id", description="user id of the user who created the chatbot")
    createdAt: int = Field(0, description="time in milliseconds since epoch when the bot was created")
    updatedAt: int = Field(0, description="time in milliseconds since epoch when the bot was last updated")
    knowledgeBases: List[KnowledgeBaseSimple] = Field([], alias="knowledge_bases", description="list of knowledge base")
    promptConfig: PromptConfig = Field(None, alias="prompt_config", description="chatbot prompt config")

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


class ChatbotUpdate(BaseModel):
    name: str = Field(None, max_length=255)
    description: str = Field(None, max_length=255)
    knowledgeBaseList: List[int] = Field(None, alias="knowledge_bases")
    promptConfig: PromptConfig = Field(None, alias="prompt_config",)
