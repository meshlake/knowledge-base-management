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
import pandas as pd
import lxml.html

from .xlsx_loader import xlsx_loader

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
                elements: List[Element] = []
                if (filetype == FileType.XLSX) or (filetype == FileType.XLS):
                    elements = xlsx_loader(file_path)
                else:
                    elements = loader.load()
                metadata = loader._get_metadata()
                text = "\n\n".join([str(el) for el in elements])
                docs = [Document(page_content=text, metadata=metadata)]
                return docs
        except Exception as e:
            print(e)
            raise e
