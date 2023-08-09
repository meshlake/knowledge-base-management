from pydantic import BaseModel
from .userDto import User

class SimilarKnowledge(BaseModel):
    id: int
    new_knowledge: str
    old_knowledge_id: int
    old_knowledge: str
    status: str
    new_knowledge_user: User
    old_knowledge_user: User
    new_knowledge_tags: str
    old_knowledge_tags: str
    
    class Config:
        orm_mode = True