from sqlalchemy import Column, ForeignKey, Integer, String, Text
from app.entities.base import BaseModel
from app.db import Base, engine
from sqlalchemy.orm import relationship

class SimilarKnowledge(Base, BaseModel):
    __tablename__ = "similar_knowledge"

    id = Column(Integer, primary_key=True)
    new_knowledge = Column(Text)
    new_knowledge_user_id = Column(Integer, ForeignKey("users.id"))
    new_knowledge_tag_id = Column(Integer, ForeignKey("knowledge_base_tags.id"))
    new_knowledge_structure = Column(String(255))
    old_knowledge_id = Column(Integer)
    old_knowledge = Column(Text)
    old_knowledge_user_id = Column(Integer, ForeignKey("users.id"))
    old_knowledge_tag_id = Column(Integer, ForeignKey("knowledge_base_tags.id"))
    old_knowledge_structure = Column(String(255))
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"))
    status = Column(String(255))
    source = Column(String(255))

    new_knowledge_user = relationship("User", backref="new_knowledge_user", foreign_keys="SimilarKnowledge.new_knowledge_user_id")
    old_knowledge_user = relationship("User", backref="old_knowledge_user", foreign_keys="SimilarKnowledge.old_knowledge_user_id")

    old_knowledge_tag = relationship("KnowledgeBaseTag", backref="old_knowledge_tag", foreign_keys="SimilarKnowledge.old_knowledge_tag_id")
    new_knowledge_tag = relationship("KnowledgeBaseTag", backref="new_knowledge_tag", foreign_keys="SimilarKnowledge.new_knowledge_tag_id")

    knowledge_base = relationship("KnowledgeBase", backref="knowledge_base", foreign_keys="SimilarKnowledge.knowledge_base_id")

    __table_args__ = {
        "mysql_charset": "utf8mb4",
    }


Base.metadata.create_all(bind=engine)
