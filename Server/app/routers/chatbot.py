import logging
from fastapi import Depends, APIRouter, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.models.userDto import User
from app.entities.chatbots import Chatbot as ChatbotEntity
from app.models.chatbot import ChatbotBase as ChatbotModel
import app.service.chatbot as chatbotService
from app.service.user import (
    oauth2_scheme,
    get_db,
    get_current_user
)

router = APIRouter(
    tags=["chatbot"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)],
)


@router.post("/chatbots", dependencies=[Depends(oauth2_scheme)], response_model=ChatbotModel)
def create_chatbot(
    model: ChatbotModel,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return chatbotService.create_chatbot(db, user, model)


@router.get("/chatbots/all", dependencies=[Depends(oauth2_scheme)], response_model=List[ChatbotModel])
def get_all_chatbots(db: Session = Depends(get_db)):
    chatbots = db.query(ChatbotEntity).order_by(
        ChatbotEntity.createdAt.desc()).all()
    return chatbots


@router.get("/chatbots/{id}", dependencies=[Depends(oauth2_scheme)], response_model=ChatbotModel)
def get_chatbot(id: int, db: Session = Depends(get_db)):
    chatbot = db.query(ChatbotEntity).filter(ChatbotEntity.id == id).first()
    if chatbot is None:
        raise HTTPException(
            status_code=404, detail=f"chatbot with id {id} not found")
    return chatbot


@router.put("/chatbots/{id}", dependencies=[Depends(oauth2_scheme)], response_model=ChatbotModel)
def update_chatbot(
    id: int,
    model: ChatbotModel,
    db: Session = Depends(get_db)
):
    chatbot = db.query(ChatbotEntity).filter(ChatbotEntity.id == id).first()
    if chatbot is None:
        raise HTTPException(
            status_code=404, detail=f"chatbot with id {id} not found")
    else:
        chatbot.name = model.name
        chatbot.description = model.description
        db.commit()
        db.refresh(chatbot)
    return chatbot


@router.delete("/chatbots/{id}", dependencies=[Depends(oauth2_scheme)])
def delete_chatbots(
    id: int,
    db: Session = Depends(get_db),
):
    count: int = (
        db.query(ChatbotEntity).filter(ChatbotEntity.id == id).delete()
    )
    if count == 0:
        raise HTTPException(
            status_code=404, detail=f"chatbot with id {id} not found")
    db.commit()
    return {"message": "success"}
