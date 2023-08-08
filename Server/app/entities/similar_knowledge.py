from sqlalchemy import Column, Integer, String, Text
from app.entities.base import BaseModel
from app.db import Base, engine


class SimilarKnowledge(Base, BaseModel):
    __tablename__ = "similar_knowledge"

    id = Column(Integer, primary_key=True)
    new_knowledge = Column(Text)
    old_knowledge_id = Column(Integer)
    old_knowledge = Column(Text)
    status = Column(String(255))

    __table_args__ = {
        "mysql_charset": "utf8mb4",
    }

Base.metadata.create_all(bind=engine)