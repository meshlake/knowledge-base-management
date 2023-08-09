from sqlalchemy import Column, ForeignKey, Integer, String, Text
from app.entities.base import BaseModel
from app.db import Base, engine
from sqlalchemy.orm import relationship

class SimilarKnowledge(Base, BaseModel):
    __tablename__ = "similar_knowledge"

    id = Column(Integer, primary_key=True)
    new_knowledge = Column(Text)
    new_knowledge_user_id = Column(Integer, ForeignKey("users.id"))
    new_knowledge_tags = Column(String(255))
    old_knowledge_id = Column(Integer)
    old_knowledge = Column(Text)
    old_knowledge_user_id = Column(Integer, ForeignKey("users.id"))
    old_knowledge_tags = Column(String(255))
    knowledge_base_id = Column(Integer)
    status = Column(String(255))
    source = Column(String(255))

    __table_args__ = {
        "mysql_charset": "utf8mb4",
    }


Base.metadata.create_all(bind=engine)
