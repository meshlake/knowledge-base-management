from pydantic import BaseModel
from typing import Union
from app.models.enums import KnowledgeStructure

class KnowledgeItem(BaseModel):
    content: str
    tag: Union[int, None] = None
    structure: KnowledgeStructure
   