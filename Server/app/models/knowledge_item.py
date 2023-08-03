from pydantic import BaseModel
from typing import Union

class KnowledgeItem(BaseModel):
    content: str
    tags: Union[list[str], None] = None
   