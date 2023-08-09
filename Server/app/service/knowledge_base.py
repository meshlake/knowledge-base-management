import logging

from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.userDto import User
from app.models.knowledge_base import (
    KnowledgeBase as KnowledgeBaseModel,
    KnowledgeBaseUpdate,
    KnowledgeBaseTag as KnowledgeBaseTagModel,
)
from app.entities.knowledge_bases import (
    KnowledgeBase as KnowledgeBaseEntity, 
    KnowledgeBaseTag as KnowledgeBaseTagEntity
)
from fastapi import HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
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

def is_knowledge_base_available(db: Session, knowledge_base_id): 
    return get_knowledge_base(db, knowledge_base_id) is not None

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

def get_knowledge_base_tags(
        db: Session, 
        knowledge_base_id: int, 
        parent_id: int | None = None
) -> Page[KnowledgeBaseTagModel]:
    
    logging.debug(f"Fetching tags on knowledge base {knowledge_base_id}...")
    query = db.query(KnowledgeBaseTagEntity)
    query = query.filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
    if parent_id is not None:
        query = query.filter(KnowledgeBaseTagEntity.parent_id == parent_id)
    query.order_by(KnowledgeBaseTagEntity.createdAt.desc())
    return paginate(db, query)

def get_knowledge_base_tag(
    db: Session,
    id: int,
    knowledge_base: int,
) -> KnowledgeBaseTagEntity:
    
    logging.info(f"Fetching tag {id} on knowledge base {knowledge_base}...")
    return (
        db.query(KnowledgeBaseTagEntity)
        .filter(KnowledgeBaseTagEntity.id == id)
        .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base)
        .first()
    )

def is_tag_available(
        db: Session, 
        knowledge_base_id: int,
        id: int | None = None,
        name: str | None = None,
) -> bool:
    if id is not None:
        return get_knowledge_base_tag(db, id, knowledge_base_id) is not None
    
    query = db.query(KnowledgeBaseTagEntity)
    query = query.filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)

    if name is not None:
        query = query.filter(KnowledgeBaseTagEntity.name == name)
        return query.first() is not None

    raise ValueError("Either id or name must be provided.")

def create_knowledge_base_tag(
    db: Session,
    knowledge_base_id: int,
    model: KnowledgeBaseTagModel,
    user: User,
):
    if not is_knowledge_base_available(db, knowledge_base_id):
        raise HTTPException(
            status_code=400,
            detail=f"Knowledge base {knowledge_base_id} is not available."
        )
    if is_tag_available(db, knowledge_base_id, name=model.name):
        raise HTTPException(
            status_code=400,
            detail=f"Tag {model.name} is already available."
        )
    if model.parentId is not None:
        parent = get_knowledge_base_tag(db, model.parentId, knowledge_base_id)
        if parent is None:
            raise HTTPException(
                status_code=400,
                detail=f"Parent tag {model.parentId} is not available."
            )
    entity = KnowledgeBaseTagEntity(
        name=model.name,
        knowledge_base_id=knowledge_base_id,
        parent_id=model.parentId,
        description=model.description,
        user_id=user.id,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity

def partial_update_tag_by_id (
    db: Session,
    knowledge_base_id: int,
    tag_id: int,
    model: KnowledgeBaseTagModel,
) -> bool: 
    entity = get_knowledge_base_tag(db, tag_id, knowledge_base_id)
    if entity is None:
        raise HTTPException(
            status_code=400,
            detail=f"Tag (/knowledge_bases/{knowledge_base_id}/tags/{tag_id}) is not available."
        )
    modified = False
    if model.name is not None and model.name != entity.name:
        modified = True
        entity.name = model.name
    if model.description is not None and model.description != entity.description:
        modified = True
        entity.description = model.description
    if modified:
        entity.updatedAt = datetime.now()
        db.commit()
        db.refresh(entity)
        return True
    return False

def delete_tag_by_id(
    db: Session,
    id: int,
    knowledge_base_id: int,
) -> int: 
    count = (
        db.query(KnowledgeBaseTagEntity)
        .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
        .filter(or_(KnowledgeBaseTagEntity.id == id, KnowledgeBaseTagEntity.parent_id == id))
        .delete()
    )
    if count == 0:
        logging.info(
            f"knowledge base tag with id {id} not found, nothing deleted, and ignore exploring this information"
        )
    db.commit()
    return count