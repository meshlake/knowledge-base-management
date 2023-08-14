import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from app.entities.knowledge_bases import KnowledgeBase as KnowledgeBaseEntity
from app.models.knowledge_base import (
    KnowledgeBase as KnowledgeBaseModel,
    KnowledgeBaseUpdate,
    KnowledgeBaseTag as KnowledgeBaseTagModel,
)
from app.models.knowledge_item import KnowledgeItem
from app.models.userDto import User
from app.db import engine
from app.service.user import oauth2_scheme, get_db, get_current_user
from app.service.knowledge_base import (
    create_knowledge_base,
    get_knowledge_base,
    update_knowledge_base,
    create_knowledge_base_tag,
    get_knowledge_base_tags,
    get_knowledge_base_tag,
    partial_update_tag_by_id,
    delete_tag_by_id,
    get_knowledge_base_tags_all,
)

from app.service.knowledge_item import (
    create_knowledge_item,
    get_knowledge_items,
    delete_knowledge_item as delete_knowledge_item_service,
    update_knowledge_item as update_knowledge_item_service,
)
from typing import Union

router = APIRouter(
    tags=["knowledge_bases"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)],
)


@router.get(
    "/knowledge_bases",
    dependencies=[Depends(oauth2_scheme)],
    response_model=Page[KnowledgeBaseModel],
)
def retrieve_knowledge_bases(db: Session = Depends(get_db)):
    return paginate(
        db, select(KnowledgeBaseEntity).order_by(KnowledgeBaseEntity.createdAt.desc())
    )


@router.post(
    "/knowledge_bases",
    dependencies=[Depends(oauth2_scheme)],
    response_model=KnowledgeBaseModel,
)
def post(
    model: KnowledgeBaseModel,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """POST /knowledge_bases

        Sample payload:
        ```
        {
            "name": "product feedback faq",
            "description": "this is a FAQ for product feedback"
        }
        ```
    Args:
        entity (KnowledgeBaseModel): knowledge base entity
        db (Session, optional): sqlalchemy database session. Defaults to Depends(get_db).
        user (User, optional): current user's information. Defaults to Depends(get_current_user).

    Returns:
        _type_: KnowledgeBaseModel
    """
    return create_knowledge_base(db, user, model)


@router.delete(
    "/knowledge_bases/{id}",
    dependencies=[Depends(oauth2_scheme)],
)
def delete(
    id: int,
    db: Session = Depends(get_db),
):
    """DELETE /knowledge_bases/{id}

    Args:
        id (int): knowledge base id
        db (Session, optional): sqlalchemy database session. Defaults to Depends(get_db).
    """
    count: int = (
        db.query(KnowledgeBaseEntity).filter(KnowledgeBaseEntity.id == id).delete()
    )
    if count == 0:
        logging.info(
            f"knowledge base with id {id} not found, nothing deleted, and ignore exploring this information"
        )
    db.commit()
    return {"message": "knowledge base deleted"}


@router.put("/knowledge_bases/{id}", dependencies=[Depends(oauth2_scheme)])
def update(id: int, knowledge_base: KnowledgeBaseUpdate, db: Session = Depends(get_db)):
    knowledge_base = update_knowledge_base(db, knowledge_base, id)
    return {"data": knowledge_base}


@router.get("/knowledge_bases/{id}", dependencies=[Depends(oauth2_scheme)])
def get(id: int, db: Session = Depends(get_db)):
    knowledge_base = get_knowledge_base(db, id)
    return {"data": knowledge_base}


@router.post("/knowledge_bases/{id}/item", dependencies=[Depends(oauth2_scheme)])
def create_one_piece_of_knowledge(
    id: int, model: KnowledgeItem, user: User = Depends(get_current_user)
):
    knowledge_item, is_need_review = create_knowledge_item(id, user, model)
    return {"data": {**knowledge_item.__dict__, "isNeedReview": is_need_review}}


@router.get("/knowledge_bases/{id}/item", dependencies=[Depends(oauth2_scheme)])
def get_knowledge(
    id: int, filepath: Union[str, None] = None, page: int = 1, size: int = 15
):
    knowledge_items = get_knowledge_items(id, page, size, filepath)
    return knowledge_items


@router.put("/knowledge_bases/item/{item_id}", dependencies=[Depends(oauth2_scheme)])
def update_knowledge_item(item_id: int, model: KnowledgeItem):
    knowledge_item = update_knowledge_item_service(item_id, model)
    return {"data": knowledge_item}


@router.delete("/knowledge_bases/item/{item_id}", dependencies=[Depends(oauth2_scheme)])
def delete_knowledge_item(item_id: int):
    delete_knowledge_item_service(item_id)
    return {"data": "success"}


@router.get(
    "/knowledge_bases/{id}/tags",
    response_model=Page[KnowledgeBaseTagModel],
    dependencies=[Depends(oauth2_scheme)],
)
def retrieve_knowledge_base_tags(
    id: int, parent_id: Union[int, None] = None, db: Session = Depends(get_db)
):
    return get_knowledge_base_tags(db, id, parent_id)


@router.get(
    "/knowledge_bases/{id}/tags/{tag_id}",
    response_model=KnowledgeBaseTagModel,
    dependencies=[Depends(oauth2_scheme)],
)
def retrieve_knowledge_base_tag(id: int, tag_id: int, db: Session = Depends(get_db)):
    return get_knowledge_base_tag(db, tag_id, id)


@router.post(
    "/knowledge_bases/{knowledge_base_id}/tags",
    response_model=KnowledgeBaseTagModel,
    dependencies=[Depends(oauth2_scheme)],
)
def post_kb_tags(
    knowledge_base_id: int,
    model: KnowledgeBaseTagModel,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_knowledge_base_tag(db, knowledge_base_id, model, user)


@router.patch(
    "/knowledge_bases/{knowledge_base_id}/tags/{tag_id}",
    dependencies=[Depends(oauth2_scheme)],
)
def partial_update_kb_tag(
    knowledge_base_id: int,
    tag_id: int,
    model: KnowledgeBaseTagModel,
    db: Session = Depends(get_db),
):
    result = partial_update_tag_by_id(db, knowledge_base_id, tag_id, model)
    if result:
        logging.info(f"tag {tag_id} updated")
    return {"message": "tag updated"}


@router.delete(
    "/knowledge_bases/{knowledge_base_id}/tags/{tag_id}",
    dependencies=[Depends(oauth2_scheme)],
)
def delete_kb_tag(knowledge_base_id: int, tag_id: int, db: Session = Depends(get_db)):
    count = delete_tag_by_id(db, tag_id, knowledge_base_id)
    if count > 0:
        logging.info(f"tag {tag_id} or all tags associated with {tag_id} deleted")
    return {"message": "tag deleted"}


@router.get("/knowledge_bases/{knowledge_base_id}/all/tags", dependencies=[Depends(oauth2_scheme)])
def retrieve_knowledge_base_tags_all(knowledge_base_id: int, db: Session = Depends(get_db)):
    return get_knowledge_base_tags_all(db, knowledge_base_id)
