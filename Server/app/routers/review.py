from fastapi import APIRouter, Depends
from app.entities import similar_knowledge
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
@router.get("/review")
def get_similar_knowledge(db: Session = Depends(get_db)):
    return paginate(
        db,
        select(similar_knowledge.SimilarKnowledge).order_by(
            similar_knowledge.SimilarKnowledge.createdAt.desc()
        ),
    )


@router.put("/review/{id}")
def review_knowledge(id: int, type: ReviewType, db: Session = Depends(get_db)):
    update_review_item(id=id, type=type, db=db)
    return {}
