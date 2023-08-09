from pydantic import BaseModel, Field, validator
from datetime import datetime

class AppBaseModel(BaseModel): 
    userId: int = Field(
        -1,
        alias="user_id",
        description="user id of the user who created the knowledge base",
    )
    createdAt: int = Field(
        0, description="time in milliseconds since epoch when the base was created"
    )
    updatedAt: int = Field(
        0, description="time in milliseconds since epoch when the base was last updated"
    )

    class Config:
        orm_mode = True

    @validator("createdAt", "updatedAt", pre=True)
    @classmethod
    def datetime_convert(cls, v):
        if isinstance(v, int):
            return v
        elif isinstance(v, datetime):
            return int(v.timestamp() * 1000)
        return v