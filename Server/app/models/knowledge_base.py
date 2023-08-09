from pydantic import BaseModel, Field, validator
from datetime import datetime

from app.models.base import AppBaseModel

class KnowledgeBase(BaseModel):
    id: int = Field(0, description="knowledge base id")
    name: str = Field(..., description="name of knowledge base")
    description: str = Field(..., description="description for the knowledge base")
    userId: int = Field(
        -1,
        alias="user_id",
        description="user id of the user who created the knowledge base",
    )
    createdAt: int = Field(
        0, description="time in milliseconds since epoch when the base was created"
    )
    updatedAt: int = Field(
        0, description="time in milliseconds since epoch when the base was last updated"
    )

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


class KnowledgeBaseUpdate(BaseModel):
    name: str = Field(..., description="name of knowledge base")
    description: str = Field(..., description="description for the knowledge base")

class KnowledgeBaseSimple(BaseModel):
    id: int = Field(..., description="id of knowledge base")
    name: str = Field(..., description="name of knowledge base")
    description: str = Field(None, description="description for the knowledge base")
    class Config:
        orm_mode = True

class KnowledgeBaseTag(AppBaseModel):
    id: int = Field(None, description="knowledge base tag id")
    name: str = Field(..., description="name of knowledge base tag")
    knowledgeBaseId: int = Field(None, alias="knowledge_base_id", description="knowledge base id")
    parentId: int = Field(None, alias="parent_id", description="parent knowledge base tag id")
    description: str = Field(None, description="description for the knowledge base tag")