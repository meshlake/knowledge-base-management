import logging
from fastapi import Depends, APIRouter, HTTPException
from typing import List
from app.db import Base, engine
from sqlalchemy.orm import Session
from app.models.userDto import User
from app.entities import chatbots
from app.models.chatbot import ChatbotBase as ChatbotModel
from app.models.chatbot import ChatbotUpdate
import app.service.chatbot as chatbotService
from app.service.user import (
    oauth2_scheme,
    get_db,
    get_current_user
)

chatbots.Base.metadata.create_all(bind=engine)

router = APIRouter(
    tags=["chatbot"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)],
)


@router.post("/chatbots", dependencies=[Depends(oauth2_scheme)], response_model=ChatbotModel)
def create_chatbot(
        model: ChatbotModel,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)):
    return chatbotService.create_chatbot(db, user, model)


@router.get("/chatbots/all", dependencies=[Depends(oauth2_scheme)], response_model=List[ChatbotModel])
def get_all_chatbot(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)):
    return chatbotService.get_all_chatbot(db, user)


@router.get("/chatbots/{id}", dependencies=[Depends(oauth2_scheme)], response_model=ChatbotModel)
def get_chatbot(
        id: int,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)):
    return chatbotService.get_chatbot(db, user, id)


@router.put("/chatbots/{id}", dependencies=[Depends(oauth2_scheme)], response_model=ChatbotModel)
def update_chatbot(
    id: int,
    model: ChatbotUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return chatbotService.update_chatbot(db, user, id, model)


@router.delete("/chatbots/{id}", dependencies=[Depends(oauth2_scheme)])
def delete_chatbot(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    chatbotService.delete_chatbot(db, user, id)
    return {"message": "success"}
