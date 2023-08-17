import logging
from typing import Union

from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.userDto import User
from app.models.knowledge_base import (
    KnowledgeBase as KnowledgeBaseModel,
    KnowledgeBaseUpdate,
    KnowledgeBaseTag as KnowledgeBaseTagModel,
)
from app.entities.knowledge_bases import (
    KnowledgeBase as KnowledgeBaseEntity,
    KnowledgeBaseTag as KnowledgeBaseTagEntity,
)
from fastapi import HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from datetime import datetime
from app.service.user import query_user_by_org


def get_all_knowledge_base(
    db: Session,
    user: User,
):
    user_ids = query_user_by_org(db, user.organization.id)
    return paginate(
        db,
        select(KnowledgeBaseEntity)
        .filter(KnowledgeBaseEntity.user_id.in_(user_ids))
        .order_by(KnowledgeBaseEntity.createdAt.desc()),
    )


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
    db: Session, knowledge_base_id: int, parent_id: int | None = None
) -> Page[KnowledgeBaseTagModel]:
    logging.debug(f"Fetching tags on knowledge base {knowledge_base_id}...")
    query = db.query(KnowledgeBaseTagEntity)
    query = query.filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
    if parent_id is not None:
        query = query.filter(KnowledgeBaseTagEntity.parent_id == parent_id)
    query.order_by(KnowledgeBaseTagEntity.createdAt.desc())
    return paginate(db, query)


def get_knowledge_base_tags_all(
    db: Session,
    knowledge_base_id: int,
) -> Page[KnowledgeBaseTagModel]:
    logging.debug("Fetching all tags")
    query = db.query(KnowledgeBaseTagEntity)
    query = query.filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
    query = query.filter(KnowledgeBaseTagEntity.parent_id != None)
    query.order_by(KnowledgeBaseTagEntity.createdAt.desc())
    return query.all()


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
    parent_id: int | None = None,
) -> bool:
    if id is not None:
        return get_knowledge_base_tag(db, id, knowledge_base_id) is not None

    query = db.query(KnowledgeBaseTagEntity)
    query = query.filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)

    if name is not None:
        if parent_id is not None:
            query = query.filter(KnowledgeBaseTagEntity.name == name).filter(
                KnowledgeBaseTagEntity.parent_id == parent_id
            )
            return query.first() is not None
        else:
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
            detail=f"Knowledge base {knowledge_base_id} is not available.",
        )
    if is_tag_available(
        db, knowledge_base_id, name=model.name, parent_id=model.parentId
    ):
        raise HTTPException(
            status_code=400, detail=f"Tag {model.name} is already available."
        )
    if model.parentId is not None:
        parent = get_knowledge_base_tag(db, model.parentId, knowledge_base_id)
        if parent is None:
            raise HTTPException(
                status_code=400, detail=f"Parent tag {model.parentId} is not available."
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


def partial_update_tag_by_id(
    db: Session,
    knowledge_base_id: int,
    tag_id: int,
    model: KnowledgeBaseTagModel,
) -> bool:
    entity = get_knowledge_base_tag(db, tag_id, knowledge_base_id)
    if entity is None:
        raise HTTPException(
            status_code=400,
            detail=f"Tag (/knowledge_bases/{knowledge_base_id}/tags/{tag_id}) is not available.",
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
        .filter(
            or_(KnowledgeBaseTagEntity.id == id, KnowledgeBaseTagEntity.parent_id == id)
        )
        .delete()
    )
    if count == 0:
        logging.info(
            f"knowledge base tag with id {id} not found, nothing deleted, and ignore exploring this information"
        )
    db.commit()
    return count


def is_tags_unique(tags: list):
    dict_tags = {}
    for tag in tags:
        if tag["tag"] not in dict_tags:
            dict_tags[tag["tag"]] = tag["parentTag"]
        else:
            if dict_tags[tag["tag"]] != tag["parentTag"]:
                return False
    return True


def batch_create_knowledge_base_tag(
    knowledge_base_id: int,
    tags: list,
    user_id: int,
):
    if len(tags) == 0:
        return []
    # 判断相同的标签是否存在不同的分类
    if not is_tags_unique(tags):
        raise HTTPException(
            status_code=400,
            detail="Tags has diffrent parent.",
        )

    db = next(get_db())

    # 获取所有的父标签
    parent_tags = [tag["parentTag"] for tag in tags]
    parent_tags = list(set(parent_tags))
    # 获取数据库中已经存在的父标签
    existing_parent_tags = (
        db.query(KnowledgeBaseTagEntity)
        .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
        .filter(KnowledgeBaseTagEntity.parent_id == None)
        .filter(KnowledgeBaseTagEntity.name.in_(parent_tags))
        .all()
    )
    existing_parent_tags_names = [tag.name for tag in existing_parent_tags]

    # 创建不存在的父标签
    create_parent_tags = [
        tag for tag in parent_tags if tag not in existing_parent_tags_names
    ]
    if len(create_parent_tags) > 0:
        create_parent_tags = [
            KnowledgeBaseTagEntity(
                name=tag,
                knowledge_base_id=knowledge_base_id,
                parent_id=None,
                description=None,
                user_id=user_id,
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
            for tag in create_parent_tags
        ]
        db.add_all(create_parent_tags)
        db.commit()

    # 获取数据库中已经存在的父标签
    new_existing_parent_tags = (
        db.query(KnowledgeBaseTagEntity)
        .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
        .filter(KnowledgeBaseTagEntity.parent_id == None)
        .filter(KnowledgeBaseTagEntity.name.in_(parent_tags))
        .all()
    )

    # 获取所有的子标签
    children_tags = [tag["tag"] for tag in tags]
    existing_children_tags = (
        db.query(KnowledgeBaseTagEntity)
        .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
        .filter(KnowledgeBaseTagEntity.parent_id != None)
        .filter(KnowledgeBaseTagEntity.name.in_(children_tags))
        .all()
    )

    existing_children_tags_names = [tag.name for tag in existing_children_tags]

    create_children_tags = [
        tag for tag in tags if tag["tag"] not in existing_children_tags_names
    ]

    # 创建子标签
    if len(create_children_tags) > 0:
        create_children_tags = [
            KnowledgeBaseTagEntity(
                name=tag["tag"],
                knowledge_base_id=knowledge_base_id,
                parent_id=[
                    parent_tag
                    for parent_tag in new_existing_parent_tags
                    if parent_tag.name == tag["parentTag"]
                ][0].id,
                description=None,
                user_id=user_id,
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
            for tag in create_children_tags
        ]
        db.add_all(create_children_tags)
        db.commit()

    new_existing_children_tags = (
        db.query(KnowledgeBaseTagEntity)
        .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
        .filter(KnowledgeBaseTagEntity.parent_id != None)
        .filter(KnowledgeBaseTagEntity.name.in_(children_tags))
        .all()
    )

    db.close()
    return new_existing_children_tags
