from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.userDto import User
from app.models.chatbot import ChatbotBase, ChatbotUpdate
from app.entities.chatbots import Chatbot as ChatbotEntity
from app.entities.knowledge_bases import KnowledgeBase as KnowledgeBaseEntity
import app.crud.chatbot as chatbotCurd


def create_chatbot(db: Session, user: User, model: ChatbotBase):
    chatbot = ChatbotBase(
        name=model.name, description=model.description, user_id=user.id)
    return chatbotCurd.create_chatbot(db=db, model=chatbot)


def update_chatbot(db: Session, user: User, id: int, model: ChatbotUpdate):
    db_chatbot = db.query(ChatbotEntity).filter(ChatbotEntity.id == id).first()
    if db_chatbot is None:
        raise HTTPException(
            status_code=404, detail=f"chatbot with id {id} not found")

    for field, value in model.dict(exclude_unset=True).items():
        if field != "knowledgeBaseList":
            if field == "promptConfig":
                setattr(db_chatbot, 'prompt_config', value)
            else:
                setattr(db_chatbot, field, value)

    if model.knowledgeBaseList is not None:  # 更新知识库
        db_chatbot.knowledge_bases = []
        knowledgeBaseList = list(set(model.knowledgeBaseList))
        for knowledge_base_id in knowledgeBaseList:
            db_knowledge_base = db.query(KnowledgeBaseEntity).filter(
                KnowledgeBaseEntity.id == knowledge_base_id).first()
            if db_knowledge_base is None:
                raise HTTPException(
                    status_code=404, detail=f"knowledge base with id {knowledge_base_id} not found")
            db_chatbot.knowledge_bases.append(db_knowledge_base)

    db.commit()
    db.refresh(db_chatbot)
    return db_chatbot


def get_all_chatbot(db: Session, user: User):
    db_chatbots = db.query(ChatbotEntity).order_by(
        ChatbotEntity.createdAt.desc()).all()
    return db_chatbots


def get_chatbot(db: Session, user: User, id: int):
    db_chatbot = db.query(ChatbotEntity).filter(ChatbotEntity.id == id).first()
    if db_chatbot is None:
        raise HTTPException(
            status_code=404, detail=f"chatbot with id {id} not found")
    return db_chatbot


def delete_chatbot(db: Session, user: User, id: int):
    db_chatbot = db.query(ChatbotEntity).filter(ChatbotEntity.id == id).first()
    if db_chatbot is None:
        raise HTTPException(
            status_code=404, detail=f"chatbot with id {id} not found")
    db.knowledge_bases = []
    db.delete(db_chatbot)
    db.commit()