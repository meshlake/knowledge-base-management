from datetime import datetime
from app.dependencies import get_db
from app.service.embedding_client import create_embedding_client
from app.service.supabase_client import create_supabase_client
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

load_dotenv()


def query_similar_knowledge(vectors, docs):
    supabase = create_supabase_client()
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
            if (old_knowledge["similarity"]) > 0.8:
                similar_knowledge = SimilarKnowledgeCreate(
                    new_knowledge=docs[idx].page_content,
                    new_knowledge_tags=docs[idx].metadata["tags"],
                    new_knowledge_user=docs[idx].metadata["user_id"],
                    old_knowledge_id=old_knowledge["id"],
                    old_knowledge=old_knowledge["content"],
                    old_knowledge_tags=old_knowledge["metadata"]["tags"],
                    old_knowledge_user=old_knowledge["metadata"]["user_id"],
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
        new_knowledge_tags=similar_knowledge.new_knowledge_tags,
        old_knowledge_tags=similar_knowledge.old_knowledge_tags,
        new_knowledge_user_id=similar_knowledge.new_knowledge_user,
        old_knowledge_user_id=similar_knowledge.old_knowledge_user,
        source=similar_knowledge.source,
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
    supabase = create_supabase_client()
    res = supabase.table("knowledge").select("*",count="exact").eq("id", similar_knowledge.old_knowledge_id).execute()
    return res.count > 0

def fusion_knowledge(silimar_knowledge: SimilarKnowledge):
    old_knowledge_existed = validate_knowledge_existed(silimar_knowledge)
    if not old_knowledge_existed:
        return
    
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_API_BASE")
    os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
    os.environ["OPENAI_API_VERSION"] = "2023-05-15"
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
    
    silimar_knowledge.new_knowledge = json.loads(res)["knowledge"]
    add_knowledge(silimar_knowledge)


def replace_knowledge(silimar_knowledge: SimilarKnowledge):
    old_knowledge_existed = validate_knowledge_existed(silimar_knowledge)
    if not old_knowledge_existed:
        return
    
    add_knowledge(silimar_knowledge)
    supabase = create_supabase_client()
    supabase.table("knowledge").delete().eq(
        "id", silimar_knowledge.old_knowledge_id
    ).execute()


def add_knowledge(silimar_knowledge: SimilarKnowledge):
    supabase = create_supabase_client()
    embedding = create_embedding_client()
    vector = embedding.embed_query(silimar_knowledge.new_knowledge)
    supabase.table("knowledge").insert(
        {
            "content": silimar_knowledge.new_knowledge,
            "metadata": {
                "tags": silimar_knowledge.new_knowledge_tags,
                "user_id": silimar_knowledge.new_knowledge_user_id,
                "type": KnowledgeItemType.FILE.name
                if silimar_knowledge.source != None
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
