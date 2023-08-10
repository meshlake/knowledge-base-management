from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db import Base, engine
from app.entities.base import BaseModel
from app.entities.chatbots import chatbot_knowledge_association

class KnowledgeBase(Base, BaseModel):

    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    user_id = Column(Integer, name="user_id")

    chatbots = relationship(
        "Chatbot", secondary=chatbot_knowledge_association, back_populates="knowledge_bases")

    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, name={self.name}, description={self.description}, user_id={self.user_id}), createdAt={self.createdAt}, updatedAt={self.updatedAt}>"

class KnowledgeBaseTag(Base, BaseModel):

    __tablename__ = "knowledge_base_tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    knowledge_base_id = Column(Integer, name="knowledge_base_id", nullable=False)
    parent_id = Column(Integer, name="parent_id")
    description = Column(String(255))
    user_id = Column(Integer, name="user_id")

Base.metadata.create_all(bind=engine)