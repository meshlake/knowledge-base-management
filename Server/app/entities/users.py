from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from app.entities.base import BaseModel
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base, BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    nickname = Column(String(255))
    email = Column(String(255))
    phone_number = Column(String(20))
    password = Column(String(255))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    disabled = Column(Boolean)
    role_id = Column(Integer, ForeignKey("roles.id"))

    role = relationship("Role", backref="users")
    organization = relationship("Organization", backref="users")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
    
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
    }