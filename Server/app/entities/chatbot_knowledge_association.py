from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db import Base

chatbot_knowledge_association = Table(
    "chatbot_knowledge_association",
    Base.metadata,
    Column("chatbot_id", Integer, ForeignKey("chatbots.id")),
    Column("knowledge_base_id", Integer, ForeignKey("knowledge_bases.id"))
)
