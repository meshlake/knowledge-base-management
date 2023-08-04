from sqlalchemy import Column, Integer, String
from app.db import Base, engine
from app.entities.base import BaseModel

class File(Base, BaseModel): 

    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    path = Column(String(255), unique=True)
    knowledge_base_id = Column(Integer, name="knowledge_base_id")
    user_id = Column(Integer, name="user_id")
    
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
    }

Base.metadata.create_all(bind=engine)