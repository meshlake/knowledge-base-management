from pydantic import BaseModel, Field
from app.models.base import AppBaseModel

class MessageModel(AppBaseModel): 
    id : int = Field(..., description="id of the message")
    content : str = Field(..., description="content of the message")
    role : str = Field(..., description="role of the message", regex="^(bot|user)$")

    class Config:
        orm_mode = True

class ConversationModel(AppBaseModel): 
    id : int = Field(..., description="id of the conversation")
    topic : str = Field(None, description="topic of the conversation")
    description : str = Field(None, description="description of the conversation")
    userId: int = Field(
        ...,
        alias="user_id",
        description="user id of the user who created the knowledge base",
    )
    bot : int = Field(..., alias="bot_id", description="id of the bot")
    messages: list[MessageModel] = Field([], description="list of messages in the conversation")

    class Config:
        orm_mode = True

class ConversationCreateModel(BaseModel):
    bot: int = Field(..., description="id of the bot")

class MessageCreateModel(BaseModel): 
    content : str = Field(..., description="content of the message")
    role : str = Field('user', description="role of the message", regex="^(bot|user)$")