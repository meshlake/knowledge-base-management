from sqlalchemy import select
from sqlalchemy.orm import Session, defer
from sqlalchemy.engine.row import Row
from app.models.userDto import User
from datetime import datetime
from fastapi import HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from app.models.conversation import (
    ConversationModel,
    MessageModel, 
    MessageCreateModel,
)

from app.entities.conversations import (
    Conversation as ConversationEntity,
    Message as MessageEntity,
)
    
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
    
    conversation.updatedAt = datetime.utcnow()

    db.commit()
    db.refresh(entity)
    db.refresh(conversation)
    
    return entity

def ask_bot(
    db: Session,
    model: MessageCreateModel,
    conversation: ConversationEntity,
) -> MessageCreateModel:
    "TODO: Implement asking bot for user message"
    
    result = MessageCreateModel(
        content=f"[Bot] {model.content}",
        role="bot",
    )

    return result

