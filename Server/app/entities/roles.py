from sqlalchemy import Column, Integer, String
from app.entities.base import BaseModel
from app.db import Base

class Role(Base, BaseModel):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    code = Column(String(255))
    description = Column(String(255), nullable=True)
    
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
    }