import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from app.entities.knowledge_bases import KnowledgeBase as KnowledgeBaseEntity
from app.models.knowledge_base import KnowledgeBase as KnowledgeBaseModel
from app.models.userDto import User
from app.db import engine
from app.service.user import (
    oauth2_scheme, 
    get_db, 
    get_current_user
)
from app.service.knowledge_base import (
    create_knowledge_base
)

router = APIRouter(
    tags=["knowledge_bases"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)],
)

@router.get(
    "/knowledge_bases", 
    dependencies=[Depends(oauth2_scheme)],
    response_model=Page[KnowledgeBaseModel]
)
def retrieve_knowledge_bases(db: Session = Depends(get_db)):
    return paginate(
        db,
        select(KnowledgeBaseEntity).order_by(KnowledgeBaseEntity.createdAt.desc())
    )

@router.post(
    "/knowledge_bases",
    dependencies=[Depends(oauth2_scheme)],
    response_model=KnowledgeBaseModel
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
    count: int = db.query(KnowledgeBaseEntity).filter(KnowledgeBaseEntity.id == id).delete()
    if count == 0:
        logging.info(f"knowledge base with id {id} not found, nothing deleted, and ignore exploring this information")
    db.commit()
    return {"message": "knowledge base deleted"}
