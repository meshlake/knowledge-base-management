import logging
import os
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.service.md_to_vector import init_index, init_index_from_local
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
from llama_index import PromptTemplate

from app.service.agents import is_answer_successful
from app.service.chat import chat_with_intent
from app.service.chatbot import get_chatbot

load_dotenv()

CHAT_SERVICE_BASE_URL = os.getenv(
    "CHAT_SERVICE_BASE_URL", "https://knowledge-base.meshlake.com"
)


def fetch_conversations(db: Session, user: User) -> Page[ConversationModel]:
    query = (
        select(*[c for c in ConversationEntity.__table__.c if c.name != "messages"])
        .filter(ConversationEntity.user_id == user.id)
        .filter(ConversationEntity.status == "active")
        .order_by(ConversationEntity.updatedAt.desc())
    )
    return paginate(
        db,
        query,
    )


def fetch_conversation(
    db: Session, id: int, user: User, with_messages: bool = False
) -> ConversationEntity:
    statement = None
    entity = None

    statement = select(ConversationEntity)
    if with_messages:
        statement = statement.join(ConversationEntity.messages)
    statement = statement.filter(ConversationEntity.id == id)
    statement = statement.filter(ConversationEntity.user_id == user.id)
    statement = statement.filter(ConversationEntity.status == "active")
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
        content=model.content, role=model.role, conversation_id=conversation.id
    )
    db.add(entity)

    if conversation.topic is None or conversation.description is None:
        existing_messages = (
            db.query(MessageEntity)
            .filter(MessageEntity.conversation_id == conversation.id)
            .all()
        )
        if conversation.topic is None and len(existing_messages) == 0:
            conversation.topic = model.content
        if conversation.description is None and len(existing_messages) == 1:
            conversation.description = model.content
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


def query_from_index(question: str):
    start_timestamp = datetime.now()
    summary_index = init_index_from_local("summary")
    summary_index_engine = summary_index.as_query_engine(
        similarity_top_k=2, response_mode="refine"
    )
    qa_prompt_tmpl_str = (
        "Context information is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Given the context information and not prior knowledge, answer the query.\n"
        "Answers should be as detailed as possible.\n"
        "If the context contains image links, you do not need to understand the images. \n"
        "You only need to convert the image links to markdown format. Markdown image syntax example: '![](https://www.example.com/images/yourimage. jpg)'.\n"
        "Use Chinese to answer the query and the answer format should be Markdown.\n"
        "Query: {query_str}\n"
        "Answer: "
    )

    qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

    summary_index_engine.update_prompts(
        {
            "response_synthesizer:text_qa_template": qa_prompt_tmpl,
        }
    )

    response_summary = summary_index_engine.query(f"Use Chinese Answer '{question}'")

    summary_response = response_summary.response

    logging.info(f"summary_response: {summary_response}")

    if is_answer_successful(question=question, answer=summary_response):
        logging.info(f"{datetime.now() - start_timestamp} to get answer from summary index")
        return summary_response
    else:
        detail_index = init_index_from_local("detail")
        detail_index_engine = detail_index.as_query_engine(
            similarity_top_k=2, response_mode="refine"
        )
        detail_index_engine.update_prompts(
            {
                "response_synthesizer:text_qa_template": qa_prompt_tmpl,
            }
        )
        response_detail = detail_index_engine.query(f"Use Chinese Answer '{question}'")
        detail_response = response_detail.response
        logging.info(f"{datetime.now() - start_timestamp} to get answer from detail index")
        return detail_response


async def ask_bot(
    model: MessageCreateModel,
    conversation: ConversationEntity,
    user: User,
    db: Session,
) -> MessageCreateModel:
    if user.organization.code != "tec-do":
        if user.username == "admin":
            bot = get_chatbot(db=db, user=user, id=conversation.bot_id)
            reply = chat_with_intent(
                model.content,
                conversation.messages,
                bot.prompt,
                bot.knowledge_bases[0].id,
            )
            return MessageCreateModel(content=reply, role="bot")
        else:
            reply = ""
            async with aiohttp.ClientSession() as session:
                async with build_chat_service_request(
                    model, conversation, user, session
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Failed to infer the reply for the user message, error reason: \n {response.text}",
                        )
                    response_data = await response.json()
                    if is_error_response(response_data):
                        raise HTTPException(
                            status_code=500,
                            detail=f"Failed to infer the reply for the user message, error reason: \n {response_data}",
                        )
                    reply = response_data.get("data")
            return MessageCreateModel(content=reply, role="bot")
    else:
        reply = query_from_index(model.content)
        return MessageCreateModel(content=reply, role="bot")


def build_chat_service_request(
    model: MessageCreateModel,
    conversation: ConversationEntity,
    user: User,
    session: aiohttp.ClientSession,
):
    payload = {
        "content": model.content,
        "user": conversation.id,  # user 是对话标识符，用于查找历史消息，所以传递 conversation.id
        "bot_id": conversation.bot_id,
    }
    return session.post(f"{CHAT_SERVICE_BASE_URL}/query", json=payload)


def is_error_response(response):
    error = response.get("error")
    data = response.get("data")
    return (error is not None and error != "") or data == "error"
