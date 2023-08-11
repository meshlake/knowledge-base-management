from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db import Base, engine
from app.entities.base import BaseModel

class Conversation(Base, BaseModel): 

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bot_id = Column(Integer, ForeignKey('chatbots.id'), nullable=False)
    topic = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(255), nullable=False, default="active")

    messages = relationship("Message", backref="conversations")

    def __repr__(self):
        return f"<Conversation(id={self.id}, bot_id={self.bot_id}, topic={self.topic}, description={self.description})>"
    
class Message(Base, BaseModel):
    
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    role = Column(String(255), nullable=False)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)

    def __repr__(self):
        return f"<Message(id={self.id}, content={self.content}, role={self.role}, conversation_id={self.conversation_id}), createdAt={self.createdAt}, updatedAt={self.updatedAt}>"
    
Base.metadata.create_all(bind=engine)