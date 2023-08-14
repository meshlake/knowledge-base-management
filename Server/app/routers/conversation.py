from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from app.models.conversation import (
    ConversationModel, 
    ConversationCreateModel,
    MessageCreateModel,
    MessageModel,
)
from app.entities.conversations import (
    Conversation as ConversationEntity,
)
from sqlalchemy.orm import Session
from app.models.userDto import User
from app.service.user import (
    oauth2_scheme,
    get_current_user, 
    get_db
)
from app.service.conversation import (
    fetch_conversations,
    fetch_conversation,
    persist_message, 
    ask_bot
)

router = APIRouter(
    tags=["conversation"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)]
)

@router.get(
    "/conversations", 
    dependencies=[Depends(oauth2_scheme)],
    response_model=Page[ConversationModel]
)
def retrieve_conversations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):  
    return fetch_conversations(db, user) 

@router.post(
    "/conversations",
    dependencies=[Depends(oauth2_scheme)],
    response_model=ConversationModel
)
def post_conversation(
    model: ConversationCreateModel,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entity = ConversationEntity(
        user_id=user.id,
        bot_id=model.bot
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity

@router.get(
    "/conversations/{id}",
    dependencies=[Depends(oauth2_scheme)],
    response_model=ConversationModel
)
def get_conversation(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return fetch_conversation(db, id, user)

@router.delete(
    "/conversations/{id}",
    dependencies=[Depends(oauth2_scheme)],
    response_model=ConversationModel
)
def delete_conversation(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conversation = fetch_conversation(db, id, user)
    conversation.status = 'deleted'
    db.commit()
    return conversation

@router.post(
    "/conversations/{id}/messages",
    dependencies=[Depends(oauth2_scheme)],
    response_model=Page[MessageModel]
)
async def send_message(
    id: int,
    model: MessageCreateModel,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
): 
    conversation = fetch_conversation(db, id, user)
    user_message = persist_message(db, model, conversation)
    bot_reply = await ask_bot(model, conversation, user)
    bot_message = persist_message(db, bot_reply, conversation) if bot_reply else None
    messages = [user_message, bot_message] if bot_message else [user_message]
    return Page(
        items=messages,
        size=len(messages),
        page=1,
        total=1
    )