from pydantic import BaseModel

class Organization(BaseModel):
    id: int
    name: str
    code: str
    
    class Config:
        orm_mode = True

class OrganizationCreate(BaseModel):
    name: str
    code: str

class OrganizationUpdate(BaseModel):
    id: int
    name: str