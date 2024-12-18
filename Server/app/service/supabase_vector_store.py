from __future__ import annotations
import json
import logging

from langchain.vectorstores.supabase import SupabaseVectorStore
from typing import TYPE_CHECKING, Any, Iterable, List, Optional

from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from app.service.review import query_similar_knowledge
from app.models.enums import KnowledgeStructure

if TYPE_CHECKING:
    import supabase


class CustomizeSupabaseVectorStore(SupabaseVectorStore):
    def limit_size_add_documents(
        self, documents: List[Document], is_find_similar:bool = True, **kwargs: Any
    ) -> List[str]:
        """Run more documents through the embeddings and add to the vectorstore.

        Args:
            documents (List[Document]: Documents to add to the vectorstore.

        Returns:
            List[str]: List of IDs of the added texts.
        """
        # TODO: Handle the case where the user doesn't provide ids on the Collection
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.limit_size_add_texts(
            texts=texts,
            metadatas=metadatas,
            is_find_similar=is_find_similar,
            **kwargs,
        )

    def limit_size_add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict[Any, Any]]] = None,
        is_find_similar:bool = True,
        **kwargs: Any,
    ) -> List[str]:
        docs = self._texts_to_documents(texts, metadatas)
        logging.info(f"Start {len(docs)} embedding")

        embedding_texts = []

        for doc in docs:
            if doc.metadata.get("structure") == KnowledgeStructure.QA.name:
                content = json.loads(doc.page_content)
                if content.get("question"):
                    text = content.get("question")
                    embedding_texts.append(text)
                else:
                    embedding_texts.append(doc.page_content)
            else:
                embedding_texts.append(doc.page_content)

        vectors = self._embedding.embed_documents(list(embedding_texts))
        logging.info(f"Embedding {len(vectors)} successful")
        
        if is_find_similar:
            logging.info("Start query similar knowledge")
            new_vectors, new_docs = query_similar_knowledge(vectors, docs)
            logging.info("Query similar knowledge successful")

            return self.limit_size_add_vectors(new_vectors, new_docs)
        else:
            logging.info("Don't query similar knowledge")
            return self.limit_size_add_vectors(vectors, docs)

    def limit_size_add_vectors(
        self, vectors: List[List[float]], documents: List[Document]
    ) -> List[str]:
        return self._limit_size_add_vectors(
            self._client, self.table_name, vectors, documents
        )

    @staticmethod
    def _limit_size_add_vectors(
        client: supabase.client.Client,
        table_name: str,
        vectors: List[List[float]],
        documents: List[Document],
    ) -> List[str]:
        """Add vectors to Supabase table."""

        rows: List[dict[str, Any]] = [
            {
                "content": documents[idx].page_content,
                "embedding": embedding,
                "metadata": documents[idx].metadata,  # type: ignore
            }
            for idx, embedding in enumerate(vectors)
        ]

        # According to the SupabaseVectorStore JS implementation, the best chunk size
        # is 500
        chunk_size = 100
        id_list: List[str] = []
        for i in range(0, len(rows), chunk_size):
            logging.info(f"Adding chunk {i} to {i + chunk_size}")
            chunk = rows[i : i + chunk_size]

            try:
                result = client.from_(table_name).insert(chunk).execute()  # type: ignore
            except Exception as e:
                logging.error(e)
                result = client.from_(table_name).insert(chunk).execute()  # type: ignore

            if len(result.data) == 0:
                raise Exception("Error inserting: No rows added")

            # VectorStore.add_vectors returns ids as strings
            ids = [str(i.get("id")) for i in result.data if i.get("id")]

            id_list.extend(ids)

        return id_list
