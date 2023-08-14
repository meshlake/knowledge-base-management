import os
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.userDto import User
from datetime import datetime
from fastapi import HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from app.models.conversation import (
    ConversationModel,
    MessageCreateModel,
)
from app.entities.conversations import (
    Conversation as ConversationEntity,
    Message as MessageEntity,
)
from dotenv import load_dotenv

load_dotenv()

CHAT_SERVICE_BASE_URL = os.getenv("CHAT_SERVICE_BASE_URL", "https://doc-search.meshlake.com")
    
def fetch_conversations(
    db: Session,
    user: User
) -> Page[ConversationModel]:
    query = (
        select(*[c for c in ConversationEntity.__table__.c if c.name != 'messages'])
            .filter(ConversationEntity.user_id == user.id)
            .filter(ConversationEntity.status == 'active')
            .order_by(ConversationEntity.updatedAt.desc())
    ) 
    return paginate(
        db, 
        query, 
    )

def fetch_conversation(
    db: Session,
    id: int, 
    user: User, 
    with_messages: bool = False
) -> ConversationEntity:
    statement = None 
    entity = None 
    
    statement = select(ConversationEntity)
    if with_messages:
        statement = statement.join(ConversationEntity.messages)    
    statement = statement.filter(ConversationEntity.id == id)
    statement = statement.filter(ConversationEntity.user_id == user.id)
    statement = statement.filter(ConversationEntity.status == 'active')
    if with_messages:
        statement = statement.order_by(MessageEntity.createdAt.asc())
    entity: ConversationEntity = db.scalars(statement).first()
    
    if entity is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return entity

def persist_message(
    db: Session,
    model: MessageCreateModel,
    conversation: ConversationEntity,
) -> MessageEntity: 
    
    entity = MessageEntity(
        content=model.content,
        role=model.role,
        conversation_id=conversation.id
    )
    db.add(entity)
    
    if conversation.topic is None or conversation.description is None:
        existing_messages = db.query(MessageEntity).filter(MessageEntity.conversation_id == conversation.id).all()
        if conversation.topic is None and len(existing_messages) >= 1: 
            conversation.topic = existing_messages[0].content
        if conversation.description is None and len(existing_messages) >= 2:
            conversation.description = existing_messages[1].content

    conversation.updatedAt = datetime.utcnow()

    db.commit()
    db.refresh(entity)
    db.refresh(conversation)
    
    return entity

import aiohttp

async def ask_bot(
    model: MessageCreateModel,
    conversation: ConversationEntity,
    user: User,
) -> MessageCreateModel:
    reply = ""
    async with aiohttp.ClientSession() as session:
        async with build_chat_service_request(model, conversation, user, session) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to infer the reply for the user message, error reason: \n {response.text}"
                )
            response_data = await response.json()
            if is_error_response(response_data):
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to infer the reply for the user message, error reason: \n {response_data}"
                )
            reply = response_data.get("data")
    return MessageCreateModel(content=reply, role="bot")

def build_chat_service_request(
    model : MessageCreateModel, 
    conversation: ConversationEntity, 
    user: User, 
    session: aiohttp.ClientSession
):
    payload = {
        "content": model.content, 
        "user": user.id,
        "bot_id": conversation.bot_id,
    }
    return session.post(
        f"{CHAT_SERVICE_BASE_URL}/query",
        json=payload
    )

def is_error_response(response):
    error = response.get("error")
    data = response.get("data")
    return (error is not None and error != "") or data == "error"