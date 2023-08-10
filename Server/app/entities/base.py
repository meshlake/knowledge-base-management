from app.db import Base
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.event import listens_for


# 定义模型基类
class BaseModel:

    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    updatedAt = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


@listens_for(Base, "before_insert")
def before_insert_listener(mapper, connection, target):
    target.createdAt = datetime.utcnow()
    target.updatedAt = datetime.utcnow()


@listens_for(Base, "before_update")
def before_update_listener(mapper, connection, target):
    target.updatedAt = datetime.utcnow()
