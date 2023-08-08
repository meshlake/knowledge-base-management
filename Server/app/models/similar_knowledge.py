from pydantic import BaseModel

class SimilarKnowledge(BaseModel):
    id: int
    new_knowledge: str
    old_knowledge_id: int
    old_knowledge: str
    status: str
    
    class Config:
        orm_mode = True