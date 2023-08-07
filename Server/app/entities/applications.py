from sqlalchemy import Column, JSON, ForeignKey, String, Integer, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.db import Base
from app.entities.base import BaseModel
from enum import Enum


class Category(Enum):
    WX_PUBLIC = "WX_PUBLIC"
    WX_CHATBOT = "WX_CHATBOT"
    MANAGEMENT_PLATFORM = "MANAGEMENT_PLATFORM"


class Application(Base, BaseModel):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(255))
    category = Column(SQLAlchemyEnum(Category), nullable=True)
    user_id = Column(Integer, name="user_id")
    api_key = Column(String(255))
    properties = Column(JSON)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"))

    chatbot = relationship("Chatbot", backref="applications")

    def __repr__(self):
        return f"<Application(id={self.id}, name={self.name}, description={self.description}, chatbot_id={self.chatbot_id})>"
