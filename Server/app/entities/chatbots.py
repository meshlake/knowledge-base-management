from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from app.db import Base
from app.entities.base import BaseModel


chatbot_knowledge_association = Table(
    "chatbot_knowledge_association",
    Base.metadata,
    Column("chatbot_id", Integer, ForeignKey("chatbots.id")),
    Column("knowledge_base_id", Integer, ForeignKey("knowledge_bases.id")),
)


class Chatbot(Base, BaseModel):
    __tablename__ = "chatbots"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(255), nullable=True)
    user_id = Column(Integer, name="user_id")
    prompt_config = Column(JSON)
    upgraded = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)

    knowledge_bases = relationship(
        "KnowledgeBase", secondary=chatbot_knowledge_association, back_populates="chatbots")

    def __repr__(self):
        return f"<Chatbot(id={self.id}, name={self.name}, description={self.description}>"
    
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
    }

