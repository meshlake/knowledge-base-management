from sqlalchemy import Column, Integer, String
from app.entities.base import BaseModel
from app.db import Base

class Organization(Base, BaseModel):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    code = Column(String(255))
    name = Column(String(255))
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name})>"
    
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
    }
