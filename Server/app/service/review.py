from datetime import datetime
import logging
from app.dependencies import get_db
from app.entities.users import User
from app.service.embedding_client import create_embedding_client
from app.service.supabase_client import SupabaseClient
from app.entities.similar_knowledge import SimilarKnowledge
from app.models.similar_knowledge import (
    SimilarKnowledgeCreate,
)
from sqlalchemy.orm import Session
from app.models.enums import ReviewStatus, ReviewType, KnowledgeItemType
from langchain.prompts import PromptTemplate
from langchain.llms import AzureOpenAI
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import os
from dotenv import load_dotenv
import json
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from app.service.user import query_user_by_org
from app.service.knowledge_base import get_all_knowledge_base_no_paginate

load_dotenv()


def is_similar_knowledge(new_knowledge_content: str, old_knowledge_content: str):
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_API_BASE")
    os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
    os.environ["OPENAI_API_VERSION"] = "2023-06-01-preview"
    llm = ChatOpenAI(engine="gpt-35-turbo")
    prompt_template = PromptTemplate.from_template(
        "判断两段文字是否表达为相同的含义并给出理由，1、```{new_knowledge_content}```, 2、```{old_knowledge_content}```"
    )
    prompt = prompt_template.format(
        new_knowledge_content=new_knowledge_content,
        old_knowledge_content=old_knowledge_content,
    )
    template = """
    你负责判断给你的两段文字是否表达为相同的含义并给出理由。
    你的返回应该是一段json, 
    例如：{{is_similar: 是否表达相似的含义,布尔值, reason: 你的理由}}
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    chain = LLMChain(llm=llm, prompt=chat_prompt)
    res = chain.run(prompt)
    try:
        res = json.loads(res)
        logging.info(prompt)
        logging.info(res["is_similar"])
        logging.info(res["reason"])
        return res["is_similar"]
    except Exception:
        logging.info(res)
        return True


def query_similar_knowledge(vectors, docs):
    supabase = SupabaseClient()
    no_similar_knowledge_idx = []

    # 查找重复知识
    for idx, embedding in enumerate(vectors):
        knowledge_base_id = docs[idx].metadata["knowledge_base_id"]
        response = supabase.rpc(
            "match_knowledge_with_meta",
            {
                "query_embedding": embedding,
                "match_count": 1,
                "knowledge_base_id": f"{knowledge_base_id}",
            },
        ).execute()
        if len(response.data) > 0:
            old_knowledge = response.data[0]
            if (old_knowledge["similarity"]) > 0.93:
                is_similar = is_similar_knowledge(
                    docs[idx].page_content, old_knowledge["content"]
                )
                if not is_similar:
                    continue
                similar_knowledge = SimilarKnowledgeCreate(
                    new_knowledge=docs[idx].page_content,
                    new_knowledge_tag_id=docs[idx].metadata["tag"],
                    new_knowledge_user_id=docs[idx].metadata["user_id"],
                    old_knowledge_id=old_knowledge["id"],
                    old_knowledge=old_knowledge["content"],
                    old_knowledge_tag_id=old_knowledge["metadata"]["tag"],
                    old_knowledge_user_id=old_knowledge["metadata"]["user_id"],
                    status=ReviewStatus.PENDING.name,
                    source=docs[idx].metadata["source"],
                    knowledge_base_id=knowledge_base_id,
                )
                create_review_item(similar_knowledge)
            else:
                no_similar_knowledge_idx.append(idx)
        else:
            no_similar_knowledge_idx.append(idx)

    new_vectors = []
    new_docs = []
    # 删除重复知识
    for idx in no_similar_knowledge_idx:
        new_vectors.append(vectors[idx])
        new_docs.append(docs[idx])
    return new_vectors, new_docs


def create_review_item(similar_knowledge: SimilarKnowledgeCreate):
    db = next(get_db())
    entity = SimilarKnowledge(
        new_knowledge=similar_knowledge.new_knowledge,
        old_knowledge_id=similar_knowledge.old_knowledge_id,
        old_knowledge=similar_knowledge.old_knowledge,
        new_knowledge_tag_id=similar_knowledge.new_knowledge_tag_id,
        old_knowledge_tag_id=similar_knowledge.old_knowledge_tag_id,
        new_knowledge_user_id=similar_knowledge.new_knowledge_user_id,
        old_knowledge_user_id=similar_knowledge.old_knowledge_user_id,
        source=similar_knowledge.source,
        knowledge_base_id=similar_knowledge.knowledge_base_id,
        status=ReviewStatus.PENDING.name,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    db.close()
    return entity


def validate_knowledge_existed(similar_knowledge: SimilarKnowledge):
    supabase = SupabaseClient()
    res = (
        supabase.table("knowledge")
        .select("*", count="exact")
        .eq("id", similar_knowledge.old_knowledge_id)
        .execute()
    )
    return res.count > 0


def delete_old_knowledge(similar_knowledge: SimilarKnowledge):
    supabase = SupabaseClient()
    supabase.table("knowledge").delete().eq(
        "id", similar_knowledge.old_knowledge_id
    ).execute()


def is_valid_json_with_key(data):
    # 判断字符串是否为空
    if not data:
        return False

    try:
        # 尝试解析字符串为 JSON
        json_data = json.loads(data)

        # 判断是否为字典类型
        if not isinstance(json_data, dict):
            return False

        # 判断是否包含 "knowledge" 键
        return "knowledge" in json_data
    except json.JSONDecodeError:
        return False


def fusion_knowledge(silimar_knowledge: SimilarKnowledge):
    old_knowledge_existed = validate_knowledge_existed(silimar_knowledge)
    if not old_knowledge_existed:
        return

    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_API_BASE")
    os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
    os.environ["OPENAI_API_VERSION"] = "2023-06-01-preview"
    llm = ChatOpenAI(engine="gpt-35-turbo")
    prompt_template = PromptTemplate.from_template(
        "融合以下两段文字，1、```{knowledge1}```, 2、```{knowledge2}```"
    )
    prompt = prompt_template.format(
        knowledge1=silimar_knowledge.new_knowledge,
        knowledge2=silimar_knowledge.old_knowledge,
    )
    template = """你负责融合两段不同的知识，融合后的知识应该是一段新的知识，不需要关注融合后的知识是否有意义。你的返回应该是一段json, 包括这些字段: `knowledge: 融合后的知识`"""
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    chain = LLMChain(llm=llm, prompt=chat_prompt)
    res = chain.run(prompt)
    if is_valid_json_with_key(res):
        silimar_knowledge.new_knowledge = json.loads(res)["knowledge"]
    add_knowledge(silimar_knowledge)
    delete_old_knowledge(silimar_knowledge)


def replace_knowledge(silimar_knowledge: SimilarKnowledge):
    old_knowledge_existed = validate_knowledge_existed(silimar_knowledge)
    if not old_knowledge_existed:
        return

    add_knowledge(silimar_knowledge)
    delete_old_knowledge(silimar_knowledge)


def add_knowledge(silimar_knowledge: SimilarKnowledge):
    supabase = SupabaseClient()
    embedding = create_embedding_client()
    vector = embedding.embed_query(silimar_knowledge.new_knowledge)
    supabase.table("knowledge").insert(
        {
            "content": silimar_knowledge.new_knowledge,
            "metadata": {
                "tag": silimar_knowledge.new_knowledge_tag_id,
                "user_id": silimar_knowledge.new_knowledge_user_id,
                "type": KnowledgeItemType.FILE.name
                if len(silimar_knowledge.source) > 0
                else KnowledgeItemType.MANUALLY.name,
                "source": silimar_knowledge.source,
                "knowledge_base_id": silimar_knowledge.knowledge_base_id,
            },
            "embedding": vector,
        }
    ).execute()


def update_review_item(id: int, db: Session, action: ReviewType):
    entity = db.query(SimilarKnowledge).filter(SimilarKnowledge.id == id).first()
    if action == ReviewType.FUSION.name:
        fusion_knowledge(entity)
    elif action == ReviewType.REPLACE.name:
        replace_knowledge(entity)
    elif action == ReviewType.ADD.name:
        add_knowledge(entity)

    entity.status = ReviewStatus.PROCESSED.name
    entity.updatedAt = datetime.now()
    db.commit()
    db.refresh(entity)
    return entity


def get_review_items(db: Session, user: User):
    user_ids = query_user_by_org(db, user.organization_id)
    knowledge_base = get_all_knowledge_base_no_paginate(db)
    knowledge_base_ids = [item.id for item in knowledge_base]
    return paginate(
        db,
        select(SimilarKnowledge)
        .filter(
            SimilarKnowledge.new_knowledge_user_id.in_(user_ids),
            SimilarKnowledge.old_knowledge_user_id.in_(user_ids),
            SimilarKnowledge.knowledge_base_id.in_(knowledge_base_ids),
        )
        .order_by(SimilarKnowledge.createdAt.desc()),
    )
