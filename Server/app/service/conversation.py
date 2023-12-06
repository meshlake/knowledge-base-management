import asyncio
import logging
import os
from typing import AsyncIterable, Awaitable
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.util import retry
from app.service.md_to_vector import (
    answer_question_streaming,
    init_index,
    init_index_from_local,
    answer_question,
)
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
from llama_index import ChatPromptTemplate, PromptTemplate

from app.service.agents import is_answer_successful
from app.service.chat import chat_with_intent, query_similar_by_supabase
from app.service.chatbot import get_chatbot
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.schema import HumanMessage
import aiohttp

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


def query_from_index(question: str, knowledge_base_id: str) -> AsyncIterable[str]:
    start_timestamp = datetime.now()

    # summary_index = init_index_from_local("summary")
    # summary_index_engine = summary_index.as_query_engine(
    #     similarity_top_k=2, response_mode="refine"
    # )
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

    # summary_index_engine.update_prompts(
    #     {
    #         "response_synthesizer:text_qa_template": qa_prompt_tmpl,
    #     }
    # )

    # response_summary = summary_index_engine.query(f"Use Chinese Answer '{question}'")

    # summary_response = response_summary.response

    # logging.info(f"summary_response: {summary_response}")
    start_query_timestamp = datetime.now()
    context = query_similar_by_supabase(question, knowledge_base_id, 0.9, 1)
    logging.info(f"{datetime.now() - start_query_timestamp} to query similar knowledge")

    if context != "":
        # start_answer_timestamp = datetime.now()
        # logging.info(f"{datetime.now() - start_answer_timestamp} to answer question")
        return answer_question_streaming(question, context)
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
        logging.info(
            f"{datetime.now() - start_timestamp} to get answer from detail index"
        )
        return detail_response

    # start_check_timestamp = datetime.now()
    # if is_answer_successful(question=question, answer=answer):
    #     logging.info(f"{datetime.now() - start_check_timestamp} to check answer")
    #     logging.info(
    #         f"{datetime.now() - start_timestamp} to get answer from summary index"
    #     )
    #     return answer
    # else:
    #     detail_index = init_index_from_local("detail")
    #     detail_index_engine = detail_index.as_query_engine(
    #         similarity_top_k=2, response_mode="refine"
    #     )
    #     detail_index_engine.update_prompts(
    #         {
    #             "response_synthesizer:text_qa_template": qa_prompt_tmpl,
    #         }
    #     )
    #     response_detail = detail_index_engine.query(f"Use Chinese Answer '{question}'")
    #     detail_response = response_detail.response
    #     logging.info(
    #         f"{datetime.now() - start_timestamp} to get answer from detail index"
    #     )
    #     return detail_response


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
        bot = get_chatbot(db=db, user=user, id=conversation.bot_id)
        reply = query_from_index(model.content, bot.knowledge_bases[0].id)
        return MessageCreateModel(content=reply, role="bot")


async def ask_bot_stream(
    model: MessageCreateModel,
    conversation: ConversationEntity,
    user: User,
    db: Session,
) -> AsyncIterable[str]:
    bot = get_chatbot(db=db, user=user, id=conversation.bot_id)

    qa_prompt_tmpl_str = (
        "Context information is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Given the context information and not prior knowledge, answer the query.\n"
        "Answers should be as detailed as possible.\n"
        "If the context contains image links, you do not need to understand the images. \n"
        "You only need to convert the image links to markdown format. Markdown image syntax example: '![](https://www.example.com/images/yourimage. jpg)'.\n"
        "Use Chinese to answer the query.\n"
        "Just return the Markdown style answer and don't use other mark to quote.\n"
        "Query: {query_str}\n"
        "Answer: "
    )

    qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

    context = query_similar_by_supabase(
        model.content, bot.knowledge_bases[0].id, 0.9, 1
    )
    logging.info(f"context: {context}")
    if context != "":
        callback = AsyncIteratorCallbackHandler()

        stream_model = AzureChatOpenAI(
            temperature=0.0,
            azure_deployment="gpt-4-1106-preview",
            openai_api_version="2023-05-15",
            azure_endpoint="https://seedlings-eus2.openai.azure.com/",
            openai_api_key="ed30b886f2ac4f909a5b015be01393e6",
            streaming=True,
            verbose=True,
            callbacks=[callback],
        )

        async def wrap_done(fn: Awaitable, event: asyncio.Event):
            """Wrap an awaitable with a event to signal when it's done or an exception is raised."""
            try:
                await fn
            except Exception as e:
                # TODO: handle exception
                print(f"Caught exception: {e}")
            finally:
                # Signal the aiter to stop.
                event.set()

        # qa_prompt_tmpl_str = (
        #     "Context information is below.\n"
        #     "---------------------\n"
        #     "{context_str}\n"
        #     "---------------------\n"
        #     "Given the context information and not prior knowledge, answer the query.\n"
        #     "Answers should be as detailed as possible.\n"
        #     "If the context contains image links, you do not need to understand the images. \n"
        #     "You only need to convert the image links to markdown format. Markdown image syntax example: '![](https://www.example.com/images/yourimage. jpg)'.\n"
        #     "Use Chinese to answer the query and the answer format should be Markdown.\n"
        #     "Query: {query_str}\n"
        #     "Answer: "
        # )

        # qa_prompt = ChatPromptTemplate.from_template(qa_prompt_tmpl_str)
        # Begin a task that runs in the background.
        task = asyncio.create_task(
            wrap_done(
                stream_model.agenerate(
                    messages=[
                        [
                            HumanMessage(
                                content=qa_prompt_tmpl.format(
                                    context_str=context, query_str=model.content
                                )
                            )
                        ]
                    ]
                ),
                callback.done,
            ),
        )
        message = ""
        async for token in callback.aiter():
            message += token
            # Use server-sent-events to stream the response
            yield f"{token}"
            await asyncio.sleep(0.1)

        await task
        persist_message(db, model, conversation)
        persist_message(
            db, MessageCreateModel(content=message, role="bot"), conversation
        )

    else:
        detail_index = init_index_from_local("detail")
        detail_index_engine = detail_index.as_query_engine(
            similarity_top_k=2, streaming=True, async_mode=True
        )
        detail_index_engine.update_prompts(
            {
                "response_synthesizer:text_qa_template": qa_prompt_tmpl,
            }
        )
        response_detail = detail_index_engine.query(
            f"Use Chinese Answer '{model.content}'"
        )
        message = ""
        try:
            for i in response_detail.response_gen:
                message += i
                yield (i)
                await asyncio.sleep(0.1)
        except asyncio.CancelledError as e:
            print(e)

        persist_message(db, model, conversation)
        persist_message(
            db, MessageCreateModel(content=message, role="bot"), conversation
        )


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
