from pydantic import BaseModel
from typing import Union

class Role(BaseModel):
    id: int
    name: str
    code: str
    description: Union[str, None] = None
    
    class Config:
        orm_mode = True

class RoleCreate(BaseModel):
    name: str
    code: str
    description: Union[str, None] = None

class RoleUpdate(BaseModel):
    id: int
    name: str
    description: Union[str, None] = None