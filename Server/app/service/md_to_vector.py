import logging
from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
    set_global_service_context,
)
from llama_index.embeddings import AzureOpenAIEmbedding
from llama_index.node_parser import SimpleNodeParser
from llama_index.indices import TreeIndex
from llama_index.llms import AzureOpenAI, OpenAI
from langchain.text_splitter import MarkdownHeaderTextSplitter
from llama_index.schema import Document
from llama_index.node_parser.extractors import (
    MetadataExtractor,
    TitleExtractor,
    QuestionsAnsweredExtractor,
    SummaryExtractor,
)
from app.service.supabase_client import SupabaseClient
from app.prompts.llama_index_summary_extractor import CHINESE_SUMMARY_EXTRACT_TEMPLATE
from llama_index.vector_stores import SupabaseVectorStore
import urllib.parse
from app.util import retry
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from supabase.client import ClientOptions

load_dotenv()

os.environ["LLAMA_INDEX_CACHE_DIR"] = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "nltk_data"
)

embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name="text-embedding-ada-002",
    api_key="49c6eee59eb642f29857eb571b0fb729",
    azure_endpoint="https://seedlings.openai.azure.com/",
    api_version="2023-05-15",
)

# llm = AzureOpenAI(
#     azure_endpoint="https://seedlings-ejp.openai.azure.com/",
#     api_key="2cb70053536b4e1b8d76dfdb09ad2459",
#     engine="gpt-4",
#     model="gpt-4",
#     api_version="2023-05-15",
# )

llm = AzureOpenAI(
    engine="gpt-4-1106-preview",
    api_version="2023-05-15",
    azure_endpoint="https://seedlings-eus2.openai.azure.com/",
    api_key="ed30b886f2ac4f909a5b015be01393e6",
)

# llm = OpenAI(
#     model="gpt-4-1106-preview",
# )

# llm = OpenAI(
#     model="gpt-4",
# )

service_context = ServiceContext.from_defaults(
    llm=llm,
    embed_model=embed_model,
)

set_global_service_context(service_context)


def generate_collection_name(knowledge_id: int, file_id: int, type: str = "summary"):
    return f"knowledge_{knowledge_id}_file_{file_id}_{type}"


def init_index(knowledge_id: int, file_id: int, type: str = "summary"):
    logging.info(f"Start init index for knowledge {knowledge_id} file {file_id}")
    # 编码密码为URL编码格式
    encoded_password = urllib.parse.quote_plus("Meshlake@2023")

    collection_name = generate_collection_name(knowledge_id, file_id, type)

    vector_store = SupabaseVectorStore(
        postgres_connection_string=(
            f"postgresql://postgres:{encoded_password}@db.mheiowdzrzlnpdsdpqyx.supabase.co:5432/postgres"
        ),
        collection_name=collection_name,
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # build index
    index = retry(
        VectorStoreIndex,
        [],
        storage_context=storage_context,
        show_progress=True,
        service_context=service_context,
    )

    logging.info(f"Finish init index for knowledge {knowledge_id} file {file_id}")
    return index


def init_index_from_local(type: str = "summary"):
    storage_context = StorageContext.from_defaults(
        persist_dir=f"app/storage/storage_{type}",
    )

    loaded_index = load_index_from_storage(storage_context)
    return loaded_index


def md_file_to_documents(md_content: str):
    logging.info(f"Start split md file to documents {md_content[:50]}")

    headers_to_split_on = [("#", "Header")]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )

    documents = []
    md_header_splits = markdown_splitter.split_text(md_content)
    # print(md_header_splits[0])

    for i in range(len(md_header_splits)):
        documents.append(
            Document(
                text=f"\n\n{md_header_splits[i].metadata['Header']}\n{md_header_splits[i].page_content}",
                metadata={},
            )
        )

    logging.info(f"Finish split md file to documents {md_content[:50]}")

    return documents


def build_node_parser(chunk_size: int, chunk_overlap: int, type: str = "summary"):
    if type == "summary":
        metadata_extractor = MetadataExtractor(
            extractors=[
                # QuestionsAnsweredExtractor(
                #     questions=1, llm=llm, prompt_template=CHINESE_QUESTION_GEN_TMPL
                # ),
                SummaryExtractor(
                    llm=llm, prompt_template=CHINESE_SUMMARY_EXTRACT_TEMPLATE
                ),
            ]
        )
        parser = SimpleNodeParser.from_defaults(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            metadata_extractor=metadata_extractor,
        )
    else:
        parser = SimpleNodeParser.from_defaults(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    return parser


def insert_documents_to_index(
    index: VectorStoreIndex,
    documents: list,
    node_parser: SimpleNodeParser,
    table_name: str,
    client: Client,
    chunk_size: int = 1,
):
    # nodes = node_parser.get_nodes_from_documents(documents, show_progress=True)
    # vx = vecs.create_client(f"postgresql://postgres:{encoded_password}@db.mheiowdzrzlnpdsdpqyx.supabase.co:5432/postgres")

    for i in range(0, len(documents), chunk_size):
        documents_chunk = documents[i : i + chunk_size]
        nodes = node_parser.get_nodes_from_documents(
            documents_chunk, show_progress=True
        )

        logging.info(f"Adding chunk {i} to {i + chunk_size}")

        # rows = [
        #     {
        #         "id": node.id_,
        #         "vec": node.embedding,
        #         "metadata": node.metadata,
        #     }
        #     for node in nodes_chunk
        # ]

        # try:
        #     client.from_(table_name).insert(rows).execute()
        # except Exception as e:
        #     logging.error(e)
        #     client.from_(table_name).insert(rows).execute()

        retry(index.insert_nodes, nodes, show_progress=True)


def create_summary_index(
    md_content: str,
    knowledge_id: int,
    file_id: int,
    supabase_client: Client,
):
    summary_index = init_index(knowledge_id, file_id, "summary")

    node_parser = build_node_parser(6000, 20, "summary")

    documents = md_file_to_documents(md_content)

    collection_name = generate_collection_name(knowledge_id, file_id, "summary")

    insert_documents_to_index(
        summary_index, documents, node_parser, collection_name, supabase_client
    )


def create_detail_index(
    md_content: str,
    knowledge_id: int,
    file_id: int,
    supabase_client: Client,
):
    summary_index = init_index(knowledge_id, file_id, "detail")

    node_parser = build_node_parser(2048, 20, "detail")

    documents = md_file_to_documents(md_content)

    collection_name = generate_collection_name(knowledge_id, file_id, "detail")

    insert_documents_to_index(
        summary_index, documents, node_parser, collection_name, supabase_client
    )


def create_index(
    md_content: str,
    knowledge_id: int,
    file_id: int,
):
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    option = ClientOptions(
        postgrest_client_timeout=60, storage_client_timeout=60, schema="vecs"
    )
    supabase_client: Client = create_client(supabase_url, supabase_key, option)

    logging.info(
        f"Start create summary index for knowledge {knowledge_id} file {file_id}"
    )
    create_summary_index(md_content, knowledge_id, file_id, supabase_client)
    logging.info(
        f"Finish create summary index for knowledge {knowledge_id} file {file_id}"
    )

    logging.info(
        f"Start create detail index for knowledge {knowledge_id} file {file_id}"
    )
    create_detail_index(md_content, knowledge_id, file_id, supabase_client)
    logging.info(
        f"Finish create detail index for knowledge {knowledge_id} file {file_id}"
    )
