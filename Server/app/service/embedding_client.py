
import os
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def create_embedding_client():
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_API_BASE")
    os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
    os.environ["OPENAI_API_VERSION"] = "2023-05-15"
    embeddings = OpenAIEmbeddings(deployment="text-embedding-ada-002", chunk_size=1)
    return embeddings