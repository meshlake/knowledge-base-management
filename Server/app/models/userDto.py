from pydantic import BaseModel
from typing import Union
from .organizationDto import Organization
from .roleDto import Role

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    id: int
    username: str
    organization: Union[Organization, None] = None
    nickname: Union[str, None] = None
    disabled: Union[bool, None] = None
    email: Union[str, None] = None
    phone_number: Union[str, None] = None
    role: Union[Role, None] = None
    
    class Config:
        orm_mode = True


class UserInDB(User):
    password: str

    def delete_password(self):
        del self.password


class UserCreate(BaseModel):
    username: str
    password: str
    nickname: str
    email: Union[str, None] = None
    phone_number: Union[str, None] = None
    organization_id: int
    role_id: int

class UserUpdate(BaseModel):
    nickname: str
    email: Union[str, None] = None
    phone_number: Union[str, None] = None
    organization_id: int
    role_id: int
    disabled: bool