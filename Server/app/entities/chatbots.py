from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db import Base, engine
from app.entities.base import BaseModel
from app.entities.chatbot_knowledge_association import chatbot_knowledge_association

class Chatbot(Base, BaseModel):
    __tablename__ = "chatbots"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    user_id = Column(Integer, name="user_id")

    knowledge_bases = relationship(
        "KnowledgeBase", secondary=chatbot_knowledge_association, back_populates="chatbots")

    def __repr__(self):
        return f"<Chatbot(id={self.id}, name={self.name}, description={self.description}>"


Base.metadata.create_all(bind=engine)
