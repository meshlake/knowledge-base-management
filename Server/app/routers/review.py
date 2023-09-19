import logging
from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from app.entities.users import User
from app.models.similar_knowledge import SimilarKnowledge as SimilarKnowledgeModel
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.service.user import get_current_user, oauth2_scheme
from app.service.review import update_review_item, get_review_items

router = APIRouter(
    tags=["review"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)],
)


# 获取相似知识分页
@router.get("/review", response_model=Page[SimilarKnowledgeModel])
def get_similar_knowledge(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return get_review_items(db, user)


@router.put("/review/{id}")
def review_knowledge(
    id: int,
    action: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logging.info(f"{user.username} review item {id} with action {action}")
    update_review_item(id=id, action=action, db=db)
    return {"data": True}
