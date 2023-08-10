from typing import Union
from pydantic import BaseModel

class User(BaseModel):
    id: int
    nickname: Union[str, None] = None
    
    class Config:
        orm_mode = True

class SimilarKnowledge(BaseModel):
    id: int
    new_knowledge: str
    old_knowledge_id: int
    old_knowledge: str
    status: str
    new_knowledge_user: User
    old_knowledge_user: User
    new_knowledge_tags: Union[list[str], None] = None
    old_knowledge_tags: Union[list[str], None] = None

    class Config:
        orm_mode = True

class SimilarKnowledgeCreate(BaseModel):
    new_knowledge: str
    old_knowledge_id: int
    old_knowledge: str
    status: str
    new_knowledge_user: int
    old_knowledge_user: int
    new_knowledge_tags: Union[list[str], None] = None
    old_knowledge_tags: Union[list[str], None] = None
    source: str
    knowledge_base_id: int

    class Config:
        orm_mode = True