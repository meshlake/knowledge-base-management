import logging
from app.dependencies import get_db
from app.models.userDto import User
from app.models.knowledge_item import KnowledgeItem as KnowledgeItemModel
import os
from app.service.s3_file import S3FileLoader
from app.service.supabase_client import create_supabase_client
from app.service.supabase_vector_store import CustomizeSupabaseVectorStore
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from app.models.enums import FileStatus, KnowledgeItemType
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.service.file_manage import update_file_status
from app.service.review import query_similar_knowledge

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
    vector_store = CustomizeSupabaseVectorStore(supabase, embeddings, "knowledge")
    metadata = {
        "type": KnowledgeItemType.MANUALLY.name,
        "source": "",
        "knowledge_base_id": knowledge_base_id,
        "user_id": user.id,
        "tags": model.tags,
    }
    docs = [Document(page_content=model.content, metadata=metadata)]
    CustomizeSupabaseVectorStore.limit_size_add_documents(vector_store, documents=docs, knowledge_base_id=knowledge_base_id)
    logging.info(f"knowledge item created: {model}")
    return model


def get_knowledge_items(
    knowledge_base_id: int, page: int, size: int, filepath: str = None
):
    print(filepath)
    supabase = create_supabase_client()
    offset = (page - 1) * size
    if filepath:
        response = (
            supabase.table("knowledge")
            .select("id, content, metadata")
            .eq("metadata->knowledge_base_id", knowledge_base_id)
            .eq("metadata->>source", filepath)
            .limit(size)
            .range(offset, offset + size)
            .execute()
        )
        total_res = (
            supabase.table("knowledge")
            .select("*", count="exact")
            .eq("metadata->knowledge_base_id", knowledge_base_id)
            .eq("metadata->>source", filepath)
            .execute()
        )
    else:
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


def create_knowledge_items_for_file(knowledge_base_id: int, user: User, filepath: str):
    logging.info(f"后台执行Embedding:{filepath}")
    try:
        db = next(get_db())
        update_file_status(db=db, filepath=filepath, status=FileStatus.EMBEDDING)
        db.close()

        supabase = create_supabase_client()
        embeddings = create_embedding_client()

        bucket_name, key = filepath.split("/", 1)
        loader = S3FileLoader(bucket_name, key)

        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=0)
        docs = text_splitter.split_documents(documents)

        metadata = {
            "type": KnowledgeItemType.FILE.name,
            "source": filepath,
            "knowledge_base_id": knowledge_base_id,
            "user_id": user.id,
            "tags": None,
        }
        # 因为S3Loader加载文件是下载后从临时文件夹中获取的，所以metadata中的source是临时文件夹中的文件路径，需要修改为S3中的文件路径
        for doc in docs:
            doc.metadata = metadata

        vector_store = CustomizeSupabaseVectorStore(supabase, embeddings, "knowledge")

        CustomizeSupabaseVectorStore.limit_size_add_documents(vector_store, documents=docs, knowledge_base_id=knowledge_base_id)

        db = next(get_db())
        update_file_status(db=db, filepath=filepath, status=FileStatus.SUCCESS)
        db.close()
        logging.info(f"Embedding成功：{filepath}")
    except Exception as e:
        db = next(get_db())
        update_file_status(db=db, filepath=filepath, status=FileStatus.FAILED)
        db.close()
        logging.error(f"Embedding失败：{e}")
