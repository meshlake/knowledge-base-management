import logging
from app.dependencies import get_db
from app.models.userDto import User
from app.models.knowledge_item import KnowledgeItem as KnowledgeItemModel
import os
from app.service.s3_file import S3FileLoader
from app.service.supabase_client import SupabaseClient
from app.service.supabase_vector_store import CustomizeSupabaseVectorStore
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from app.models.enums import FileStatus, KnowledgeItemType, KnowledgeStructure
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import MarkdownHeaderTextSplitter
from app.service.file_manage import update_file_status
from app.service.embedding_client import create_embedding_client
from unstructured.file_utils.filetype import (
    FileType,
    detect_filetype,
)
from app.service.user import query_users_by_ids
from app.util import get_pages


def create_knowledge_item(
    knowledge_base_id: int, user: User, model: KnowledgeItemModel
):
    supabase = SupabaseClient()
    embeddings = create_embedding_client()
    vector_store = CustomizeSupabaseVectorStore(supabase, embeddings, "knowledge")
    metadata = {
        "type": KnowledgeItemType.MANUALLY.name,
        "source": "",
        "knowledge_base_id": knowledge_base_id,
        "user_id": user.id,
        "tag": model.tag,
        "structure": model.structure.name
    }
    docs = [Document(page_content=model.content, metadata=metadata)]
    ids = CustomizeSupabaseVectorStore.limit_size_add_documents(
        vector_store, documents=docs
    )
    logging.debug(f"knowledge item created: {model}")
    return model, len(ids) == 0


def search_knowledge_item(
    knowledge_base_id: int,
    page: int,
    size: int,
    search: str,
):
    supabase = SupabaseClient()
    offset = (page - 1) * size
    embeddings = create_embedding_client()
    vector = embeddings.embed_query(search)
    response = supabase.rpc(
        "search_knowledge_with_pagination",
        {
            "query_embedding": vector,
            "size": 10,
            "off": offset,
            "knowledge_base_id": f"{knowledge_base_id}",
        },
    ).execute()
    # count_res = supabase.rpc(
    #     "count_knowledge_with_search",
    #     {
    #         "query_embedding": vector,
    #         "knowledge_base_id": f"{knowledge_base_id}",
    #     },
    # ).execute()
    total_res = response.data.__len__()
    return response, total_res


def search_knowledge_item_by_user_id(
    knowledge_base_id: int,
    page: int,
    size: int,
    user_id: int,
    search: str,
):
    supabase = SupabaseClient()
    offset = (page - 1) * size
    embeddings = create_embedding_client()
    vector = embeddings.embed_query(search)
    response = supabase.rpc(
        "user_search_knowledge_with_pagination",
        {
            "query_embedding": vector,
            "size": 10,
            "off": offset,
            "knowledge_base_id": f"{knowledge_base_id}",
            "user_id": f"{user_id}",
        },
    ).execute()
    # count_res = supabase.rpc(
    #     "user_count_knowledge_with_search",
    #     {
    #         "query_embedding": vector,
    #         "knowledge_base_id": f"{knowledge_base_id}",
    #         "user_id": f"{user_id}",
    #     },
    # ).execute()
    # total_res = count_res.data[0]
    total_res = response.data.__len__()
    return response, total_res


def default_get_knowledge_items(
    knowledge_base_id: int,
    page: int,
    size: int,
    filepath: str = None,
    tag_id: int = None,
    user: User = None,
):
    supabase = SupabaseClient()
    offset = (page - 1) * size
    list_query = (
        supabase.table("knowledge")
        .select("id, content, metadata")
        .eq("metadata->knowledge_base_id", knowledge_base_id)
    )
    count_query = (
        supabase.table("knowledge")
        .select("*", count="exact")
        .eq("metadata->knowledge_base_id", knowledge_base_id)
    )

    if user and user.role.code == "user":
        list_query = list_query.eq("metadata->user_id", user.id)
        count_query = count_query.eq("metadata->user_id", user.id)

    if filepath:
        list_query = list_query.eq("metadata->>source", filepath)
        count_query = count_query.eq("metadata->>source", filepath)
    elif tag_id:
        list_query = list_query.eq("metadata->tag", tag_id)
        count_query = count_query.eq("metadata->tag", tag_id)

    response = list_query.order("id", desc=True).range(offset, offset + size).execute()
    total_res = count_query.execute()
    return response, total_res


def get_knowledge_items(
    knowledge_base_id: int,
    page: int,
    size: int,
    filepath: str = None,
    tag_id: int = None,
    user: User = None,
    search: str = None,
):
    # 相似搜索
    if search:
        # 普通用户只能看到自己创建的知识
        if user and user.role.code == "user":
            response, total_res = search_knowledge_item_by_user_id(
                knowledge_base_id, page, size, user.id, search
            )
            user_ids = [user.id]
            users = query_users_by_ids(next(get_db()), user_ids)
            for item in response.data:
                item["metadata"]["user"] = {'nickname': users[0].nickname} 
            return {
                "items": response.data,
                "total": total_res,
                "page": page,
                "size": size,
                "pages": get_pages(int(total_res), size),
            }
        else:
            response, total_res = search_knowledge_item(
                knowledge_base_id, page, size, search
            )
            user_ids = list(set([item["metadata"]["user_id"] for item in response.data])) 
            users = query_users_by_ids(next(get_db()), user_ids)
            for item in response.data:
                found_user = [user for user in users if user.id == item["metadata"]["user_id"]]
                item["metadata"]["user"] = {'nickname': found_user[0].nickname} 
            return {
                "items": response.data,
                "total": total_res,
                "page": page,
                "size": size,
                "pages": get_pages(int(total_res), size),
            }
    else:
        response, total_res = default_get_knowledge_items(
            knowledge_base_id, page, size, filepath, tag_id, user
        )
        logging.debug(f"knowledge items: {response}")
        user_ids = list(set([item["metadata"]["user_id"] for item in response.data])) 
        users = query_users_by_ids(next(get_db()), user_ids)
        for item in response.data:
            found_user = [user for user in users if user.id == item["metadata"]["user_id"]]
            item["metadata"]["user"] = {'nickname': found_user[0].nickname}
        return {
            "items": response.data,
            "total": total_res.count,
            "page": page,
            "size": size,
            "pages": get_pages(int(total_res.count), size),
        }


def delete_knowledge_item(item_id: int):
    supabase = SupabaseClient()
    supabase.table("knowledge").delete().eq("id", item_id).execute()
    return item_id


def update_knowledge_item(item_id: int, model: KnowledgeItemModel):
    supabase = SupabaseClient()
    embeddings = create_embedding_client()
    vector = embeddings.embed_query(model.content)
    metadata = get_knowledge_item(item_id)["metadata"]
    metadata["tag"] = model.tag
    supabase.table("knowledge").update(
        {
            "metadata": metadata,
            "content": model.content,
            "embedding": vector,
        }
    ).eq("id", item_id).execute()
    return model


def get_knowledge_item(item_id: int):
    supabase = SupabaseClient()
    response = (
        supabase.table("knowledge")
        .select("id, content, metadata")
        .eq("id", item_id)
        .execute()
    )
    return response.data[0]


def create_knowledge_items_for_file(knowledge_base_id: int, user: User, filepath: str):
    logging.info(f"{user.username}后台执行Embedding:{filepath}")
    try:
        db = next(get_db())
        update_file_status(db=db, filepath=filepath, status=FileStatus.EMBEDDING)
        db.close()

        supabase = SupabaseClient()
        embeddings = create_embedding_client()

        bucket_name, key = filepath.split("/", 1)
        loader = S3FileLoader(bucket_name, key)
        filetype = detect_filetype(filepath)
        embedding_docs = []
        if (
            (filetype == FileType.XLSX)
            or (filetype == FileType.XLS)
            or (filetype == FileType.CSV)
        ):
            documents = loader.excel_load(
                knowledge_base_id=knowledge_base_id, user_id=user.id
            )
            for doc in documents:
                doc.metadata = {
                    "type": KnowledgeItemType.FILE.name,
                    "source": filepath,
                    "knowledge_base_id": knowledge_base_id,
                    "user_id": user.id,
                    "tag": doc.metadata["tag"] if "tag" in doc.metadata else None,
                    "structure": KnowledgeStructure.QA.name,
                }
            embedding_docs = documents
        elif (filetype == FileType.MD):
            documents = loader.load()

            headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
            ]
            markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
            text_splitter = RecursiveCharacterTextSplitter(
                separators=["\n\n", "\n"], chunk_size=500, chunk_overlap=30
            )

            docs = []
            for document in documents:
                md_header_splits = markdown_splitter.split_text(document.page_content)
                splits = text_splitter.split_documents(md_header_splits)
                docs.extend(splits)

            metadata = {
                "type": KnowledgeItemType.FILE.name,
                "source": filepath,
                "knowledge_base_id": knowledge_base_id,
                "user_id": user.id,
                "tag": None,
                "structure": KnowledgeStructure.NORMAL.name,
            }
            # 因为S3Loader加载文件是下载后从临时文件夹中获取的，所以metadata中的source是临时文件夹中的文件路径，需要修改为S3中的文件路径
            for doc in docs:
                doc.metadata = metadata

            embedding_docs = docs
        else:
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                separators=["\n\n", "\n"], chunk_size=500, chunk_overlap=30
            )
            docs = text_splitter.split_documents(documents)

            metadata = {
                "type": KnowledgeItemType.FILE.name,
                "source": filepath,
                "knowledge_base_id": knowledge_base_id,
                "user_id": user.id,
                "tag": None,
                "structure": KnowledgeStructure.NORMAL.name,
            }
            # 因为S3Loader加载文件是下载后从临时文件夹中获取的，所以metadata中的source是临时文件夹中的文件路径，需要修改为S3中的文件路径
            for doc in docs:
                doc.metadata = metadata
            embedding_docs = docs

        vector_store = CustomizeSupabaseVectorStore(supabase, embeddings, "knowledge")

        CustomizeSupabaseVectorStore.limit_size_add_documents(
            vector_store, documents=embedding_docs
        )

        db = next(get_db())
        update_file_status(db=db, filepath=filepath, status=FileStatus.SUCCESS)
        db.close()
        logging.info(f"Embedding成功：{filepath}")
    except Exception as e:
        db = next(get_db())
        update_file_status(db=db, filepath=filepath, status=FileStatus.FAILED)
        db.close()
        logging.error(f"Embedding失败：{e}")
