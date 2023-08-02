from sqlalchemy.orm import Session
from app.models.knowledge_base import KnowledgeBase as KnowledgeBaseModel
from app.entities.knowledge_bases import KnowledgeBase as KnowledgeBaseEntity

def create_knowledge_base(db: Session, knowledge_base: KnowledgeBaseModel):
    db_knowledge_base = KnowledgeBaseEntity(
        title=knowledge_base.title,
        content=knowledge_base.content,
        userId=knowledge_base.userId
    )
    db.add(db_knowledge_base)
    db.commit()
    db.refresh(db_knowledge_base)
    return db_knowledge_base