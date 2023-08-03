import logging
from app.models.userDto import User
from app.models.knowledge_item import KnowledgeItem as KnowledgeItemModel
import os
from app.service.supabase_client import create_supabase_client
from app.service.supabase_vector_store import SupabaseVectorStore
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from app.models.enums import KnowledgeItemType


def create_embedding_client():
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_API_BASE")
    os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
    os.environ["OPENAI_API_VERSION"] = "2023-05-15"
    embeddings = OpenAIEmbeddings(deployment="text-embedding-ada-002", chunk_size=1)
    return embeddings


def create_knowledge_item(
    knowledge_base_id: int, user: User, model: KnowledgeItemModel
):
    supabase = create_supabase_client()
    embeddings = create_embedding_client()
    vector_store = SupabaseVectorStore(supabase, embeddings, "knowledge")
    metadata = {
        "type": KnowledgeItemType.MANUALLY.name,
        "source": "",
        "knowledge_base_id": knowledge_base_id,
        "user_id": user.id,
        "tags": model.tags,
    }
    docs = [Document(page_content=model.content, metadata=metadata)]
    SupabaseVectorStore.add_documents(vector_store, documents=docs)
    logging.info(f"knowledge item created: {model}")
    return model


def get_knowledge_items(knowledge_base_id: int, page: int, size: int):
    supabase = create_supabase_client()
    offset = (page - 1) * size
    response = (
        supabase.table("knowledge")
        .select("id, content, metadata")
        .eq("metadata->knowledge_base_id", knowledge_base_id)
        .limit(size)
        .range(offset, offset + size)
        .execute()
    )
    total_res = (
        supabase.table("knowledge")
        .select("*", count="exact")
        .eq("metadata->knowledge_base_id", knowledge_base_id)
        .execute()
    )
    logging.info(f"knowledge items: {response}")
    return {
        "items": response.data,
        "total": total_res.count,
        "page": page,
        "size": size,
        "pages": total_res.count // size + 1,
    }


def delete_knowledge_item(item_id: int):
    supabase = create_supabase_client()
    supabase.table("knowledge").delete().eq("id", item_id).execute()
    return item_id


def update_knowledge_item(item_id: int, model: KnowledgeItemModel):
    supabase = create_supabase_client()
    embeddings = create_embedding_client()
    vector = embeddings.embed_query(model.content)
    metadata = get_knowledge_item(item_id)["metadata"]
    metadata["tags"] = model.tags
    supabase.table("knowledge").update(
        {
            "metadata": metadata,
            "content": model.content,
            "embedding": vector,
        }
    ).eq("id", item_id).execute()
    return model


def get_knowledge_item(item_id: int):
    supabase = create_supabase_client()
    response = (
        supabase.table("knowledge")
        .select("id, content, metadata")
        .eq("id", item_id)
        .execute()
    )
    return response.data[0]
