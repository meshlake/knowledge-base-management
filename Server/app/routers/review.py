from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from app.entities.similar_knowledge import SimilarKnowledge
from app.models.similar_knowledge import SimilarKnowledge as SimilarKnowledgeModel
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.enums import ReviewType
from app.service.user import oauth2_scheme
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from app.service.review import update_review_item

router = APIRouter(
    tags=["review"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)],
)


# 获取相似知识分页
@router.get("/review", response_model=Page[SimilarKnowledgeModel])
def get_similar_knowledge(db: Session = Depends(get_db)):
    return paginate(
        db,
        select(SimilarKnowledge).order_by(SimilarKnowledge.createdAt.desc()),
    )


@router.put("/review/{id}")
def review_knowledge(
    id: int, action: str, db: Session = Depends(get_db)
):
    update_review_item(id=id, action=action, db=db)
    return {"data": True}
