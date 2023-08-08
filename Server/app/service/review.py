from datetime import datetime

from app.service.supabase_client import create_supabase_client
from app.entities.similar_knowledge import SimilarKnowledge
from app.models.similar_knowledge import SimilarKnowledge as SimilarKnowledgeModel
from sqlalchemy.orm import Session

def query_similar_knowledge(vectors, docs, knowledge_base_id):
    supabase = create_supabase_client()
    no_similar_knowledge_idx = []

    # 查找重复知识
    for idx, embedding in enumerate(vectors):
        response = supabase.rpc(
            "match_knowledge_with_meta",
            {
                "query_embedding": embedding,
                "match_count": 1,
                "knowledge_base_id": f"{knowledge_base_id}",
            },
        ).execute()
        if(len(response.data) > 0):
            old_knowledge = response.data[0]
            if(old_knowledge.similarity) > 0.8:
                similar_knowledge = SimilarKnowledgeModel(
                    new_knowledge=docs[idx].page_content,
                    old_knowledge_id=old_knowledge.id,
                    old_knowledge=old_knowledge.content,
                )
                create_review_item(similar_knowledge, Session())
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

def create_review_item(similar_knowledge:SimilarKnowledgeModel, db: Session):
    entity = SimilarKnowledge(
        new_knowledge=similar_knowledge.new_knowledge,
        old_knowledge_id=similar_knowledge.old_knowledge_id,
        old_knowledge=similar_knowledge.old_knowledge,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity

