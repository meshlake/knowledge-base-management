from sqlalchemy.orm import Session
from app.models.userDto import User
from app.models.knowledge_base import KnowledgeBase as KnowledgeBaseModel
from app.entities.knowledge_bases import KnowledgeBase as KnowledgeBaseEntity
from datetime import datetime

def create_knowledge_base(
    db: Session,
    user: User,
    model: KnowledgeBaseModel,
): 
    entity = KnowledgeBaseEntity(
        name=model.name,
        description=model.description,
        user_id=user.id,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity