from sqlalchemy import Column, Integer, String
from app.db import Base, engine
from app.entities.base import BaseModel

class KnowledgeBase(Base, BaseModel): 

    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(255))


Base.metadata.create_all(bind=engine)