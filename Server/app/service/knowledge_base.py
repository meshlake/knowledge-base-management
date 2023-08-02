from sqlalchemy.orm import Session
from app.models.userDto import User
from app.models.knowledge_base import (
    KnowledgeBase as KnowledgeBaseModel,
    KnowledgeBaseUpdate,
)
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


def get_knowledge_base(db: Session, knowledge_base_id):
    return (
        db.query(KnowledgeBaseEntity)
        .filter(KnowledgeBaseEntity.id == knowledge_base_id)
        .first()
    )


def update_knowledge_base(
    db: Session,
    model: KnowledgeBaseUpdate,
    id: int,
):
    knowledge_base_entity = get_knowledge_base(db=db, knowledge_base_id=id)
    if knowledge_base_entity:
        knowledge_base_entity.name = model.name
        knowledge_base_entity.description = model.description
        knowledge_base_entity.updatedAt = datetime.now()
        db.commit()
        db.refresh(knowledge_base_entity)
    return knowledge_base_entity
