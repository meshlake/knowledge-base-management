from typing import Union
from pydantic import BaseModel


class User(BaseModel):
    id: int
    nickname: Union[str, None] = None

    class Config:
        orm_mode = True


class KnowledgeBaseTag(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class KnowledgeBase(BaseModel):
    id: int
    name: str

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
    new_knowledge_tag: Union[KnowledgeBaseTag, None] = None
    old_knowledge_tag: Union[KnowledgeBaseTag, None] = None
    knowledge_base: KnowledgeBase
    old_knowledge_structure: str
    new_knowledge_structure: str

    class Config:
        orm_mode = True


class SimilarKnowledgeCreate(BaseModel):
    new_knowledge: str
    old_knowledge_id: int
    old_knowledge: str
    status: str
    new_knowledge_user_id: int
    old_knowledge_user_id: int
    new_knowledge_tag_id: Union[int, None] = None
    old_knowledge_tag_id: Union[int, None] = None
    new_knowledge_structure: Union[str, None] = None
    old_knowledge_structure: Union[str, None] = None
    source: str
    knowledge_base_id: int

    class Config:
        orm_mode = True
