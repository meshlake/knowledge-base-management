from pydantic import BaseModel
from typing import Union

class KnowledgeItem(BaseModel):
    content: str
    tag: Union[int, None] = None
   