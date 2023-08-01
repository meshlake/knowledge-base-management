from pydantic import BaseModel, Field

class KnowledgeBase(BaseModel):
    id: int
    name: str = Field(..., description="name of knowledge base")
    description: str = Field(..., description="description for the knowledge base")
    createdAt: int = Field(0, alias="created_at", description="time in milliseconds since epoch when the base was created")
    updatedAt: int = Field(0, alias="updated_at", description="time in milliseconds since epoch when the base was last updated")
    
    class Config:
        orm_mode = True
