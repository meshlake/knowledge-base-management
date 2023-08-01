from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from app.entities.knowledge_bases import KnowledgeBase as KnowledgeBaseEntity
from app.models.knowledge_base import KnowledgeBase as KnowledgeBaseModel
from app.db import engine
from app.service.user import oauth2_scheme, get_db

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
        select(KnowledgeBaseEntity)
            .order_by(KnowledgeBaseEntity.createdAt.desc())
    )
