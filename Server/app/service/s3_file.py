"""Loading logic for loading documents from an s3 file."""
import os
import tempfile
from typing import List
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from unstructured.file_utils.filetype import (
    FileType,
    detect_filetype,
)
import logging

from unstructured.documents.elements import Element, ElementMetadata, Table

from .xlsx_loader import xlsx_loader, csv_loader
from .knowledge_base import batch_create_knowledge_base_tag
import pandas as pd

NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nltk_data")
import nltk
nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

load_dotenv()


class S3FileLoader(BaseLoader):
    """Loading logic for loading documents from s3."""

    def __init__(self, bucket: str, key: str):
        """Initialize with bucket and key name."""
        self.bucket = bucket
        self.key = key

    def load(self) -> List[Document]:
        """Load documents."""
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "Could not import `boto3` python package. "
                "Please install it with `pip install boto3`."
            )
        try:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name="cn-northwest-1",
            )
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = f"{temp_dir}/{self.key}"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                s3.download_file(self.bucket, self.key, file_path)
                loader = UnstructuredFileLoader(file_path)
                filetype = detect_filetype(file_path)
                # if filetype == FileType.TXT:
                #     elements = partition_text(
                #         filename=file_path,
                #         file=None,
                #         encoding=None,
                #         paragraph_grouper=None,
                #     )
                # else:
                #     elements = loader.load()
                elements = loader.load()
                metadata = loader._get_metadata()
                text = "\n\n".join([str(el) for el in elements])
                docs = [Document(page_content=text, metadata=metadata)]
                return docs
        except Exception as e:
            print(e)
            raise e

    def excel_load(self, knowledge_base_id: int, user_id: int) -> List[Document]:
        """Load documents."""
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "Could not import `boto3` python package. "
                "Please install it with `pip install boto3`."
            )
        try:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name="cn-northwest-1",
            )
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = f"{temp_dir}/{self.key}"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                s3.download_file(self.bucket, self.key, file_path)
                filetype = detect_filetype(file_path)

                elements = []
                if (filetype == FileType.XLSX) or (filetype == FileType.XLS):
                    elements = xlsx_loader(file_path, revision=1)
                elif filetype == FileType.CSV:
                    elements = csv_loader(file_path, revision=1)

                documents = []
                tags = []
                for el in elements:
                    for data in el.data:
                        if len(data.tags["分类"]) > 0 and len(data.tags["标签"]) > 0:
                            tags.append(
                                {
                                    "parentTag": data.tags["分类"][0],
                                    "tag": data.tags["标签"][0],
                                }
                            )
                unique_tags = []
                df = pd.DataFrame(tags)
                unique_df = df.drop_duplicates()
                unique_tags = unique_df.to_dict("records")
                tag_entities = batch_create_knowledge_base_tag(
                    knowledge_base_id=knowledge_base_id,
                    user_id=user_id,
                    tags=unique_tags,
                )
                for el in elements:
                    for data in el.data:
                        if len(data.tags["分类"]) > 0 and len(data.tags["标签"]) > 0:
                            metadata = {
                                "tag": [
                                    tag
                                    for tag in tag_entities
                                    if tag.name == data.tags["标签"][0]
                                ][0].id
                            }
                        text = "\n\n".join([str(el) for el in data.data])
                        documents.append(Document(page_content=text, metadata=metadata))
                return documents
        except Exception as e:
            print(e)
            raise e
