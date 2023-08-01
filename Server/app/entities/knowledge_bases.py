from sqlalchemy import Column, Integer, String
from app.db import Base, engine
from app.entities.base import BaseModel

class KnowledgeBase(Base, BaseModel): 

    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    user_id = Column(Integer, name="user_id")

    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, name={self.name}, description={self.description}, user_id={self.user_id}), createdAt={self.createdAt}, updatedAt={self.updatedAt}>"

Base.metadata.create_all(bind=engine)