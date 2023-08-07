from pydantic import BaseModel
from typing import Union

class File(BaseModel):
    id: int
    name: str
    knowledge_base_id: int
    path: str

    class Config:
        orm_mode = True

class FileCreate(BaseModel):
    name: str
    knowledge_base_id: int
    path: str
   