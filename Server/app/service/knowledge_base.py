import json
import logging
import tempfile
import time
from typing import Union

from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.userDto import User
from app.models.knowledge_base import (
    KnowledgeBase as KnowledgeBaseModel,
    KnowledgeBaseUpdate,
    KnowledgeBaseTag as KnowledgeBaseTagModel,
)
from app.entities.knowledge_bases import (
    KnowledgeBase as KnowledgeBaseEntity,
    KnowledgeBaseTag as KnowledgeBaseTagEntity,
)
from fastapi import HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from datetime import datetime, timedelta
from app.service.user import query_user_by_org
from app.service.supabase_client import SupabaseClient
import openpyxl
import boto3
import os
from app.models.enums import KnowledgeStructure
from app.util import get_pages


def get_all_knowledge_base(
    db: Session,
    user: User,
):
    user_ids = query_user_by_org(db, user.organization.id)
    return paginate(
        db,
        select(KnowledgeBaseEntity)
        .filter(KnowledgeBaseEntity.user_id.in_(user_ids))
        .order_by(KnowledgeBaseEntity.createdAt.desc()),
    )


def get_all_knowledge_base_no_paginate(db: Session):
    return db.query(KnowledgeBaseEntity).all()


def create_knowledge_base(
    db: Session,
    user: User,
    model: KnowledgeBaseModel,
):
    entity = KnowledgeBaseEntity(
        name=model.name,
        description=model.description,
        user_id=user.id,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def get_knowledge_base(db: Session, knowledge_base_id):
    return (
        db.query(KnowledgeBaseEntity)
        .filter(KnowledgeBaseEntity.id == knowledge_base_id)
        .first()
    )


def is_knowledge_base_available(db: Session, knowledge_base_id):
    return get_knowledge_base(db, knowledge_base_id) is not None


def update_knowledge_base(
    db: Session,
    model: KnowledgeBaseUpdate,
    id: int,
):
    knowledge_base_entity = get_knowledge_base(db=db, knowledge_base_id=id)
    if knowledge_base_entity:
        knowledge_base_entity.name = model.name
        knowledge_base_entity.description = model.description
        knowledge_base_entity.updatedAt = datetime.now()
        db.commit()
        db.refresh(knowledge_base_entity)
    return knowledge_base_entity


def get_knowledge_base_tags(
    db: Session, knowledge_base_id: int, parent_id: int | None = None
) -> Page[KnowledgeBaseTagModel]:
    logging.debug(f"Fetching tags on knowledge base {knowledge_base_id}...")
    query = db.query(KnowledgeBaseTagEntity)
    query = query.filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
    if parent_id is not None:
        query = query.filter(KnowledgeBaseTagEntity.parent_id == parent_id)
    query.order_by(KnowledgeBaseTagEntity.createdAt.desc())
    return paginate(db, query)


def get_knowledge_base_tags_without_parent(
    db: Session, knowledge_base_id: int
) -> Page[KnowledgeBaseTagModel]:
    logging.debug(f"Fetching tags on knowledge base {knowledge_base_id}...")
    query = db.query(KnowledgeBaseTagEntity)
    query = query.filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
    query = query.filter(KnowledgeBaseTagEntity.parent_id == None)
    query.order_by(KnowledgeBaseTagEntity.createdAt.desc())
    return paginate(db, query)


def get_knowledge_base_tags_all(
    db: Session,
    knowledge_base_id: int,
) -> Page[KnowledgeBaseTagModel]:
    logging.debug("Fetching all tags")
    query = db.query(KnowledgeBaseTagEntity)
    query = query.filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
    query.order_by(KnowledgeBaseTagEntity.createdAt.desc())
    return query.all()


def get_knowledge_base_tag(
    db: Session,
    id: int,
    knowledge_base: int,
) -> KnowledgeBaseTagEntity:
    logging.info(f"Fetching tag {id} on knowledge base {knowledge_base}...")
    return (
        db.query(KnowledgeBaseTagEntity)
        .filter(KnowledgeBaseTagEntity.id == id)
        .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base)
        .first()
    )


def get_knowledge_base_tags_by_ids(
    db: Session,
    ids: list,
    knowledge_base: int,
) -> KnowledgeBaseTagEntity:
    logging.info(f"Fetching tag {ids} on knowledge base {knowledge_base}...")
    return (
        db.query(KnowledgeBaseTagEntity)
        .filter(KnowledgeBaseTagEntity.id.in_(ids))
        .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base)
        .all()
    )


def is_tag_available(
    db: Session,
    knowledge_base_id: int,
    id: int | None = None,
    name: str | None = None,
    parent_id: int | None = None,
) -> bool:
    if id is not None:
        return get_knowledge_base_tag(db, id, knowledge_base_id) is not None

    query = db.query(KnowledgeBaseTagEntity)
    query = query.filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)

    if name is not None:
        if parent_id is not None:
            query = query.filter(KnowledgeBaseTagEntity.name == name).filter(
                KnowledgeBaseTagEntity.parent_id == parent_id
            )
            return query.first() is not None
        else:
            query = query.filter(KnowledgeBaseTagEntity.name == name)
            return query.first() is not None

    raise ValueError("Either id or name must be provided.")


def create_knowledge_base_tag(
    db: Session,
    knowledge_base_id: int,
    model: KnowledgeBaseTagModel,
    user: User,
):
    if not is_knowledge_base_available(db, knowledge_base_id):
        raise HTTPException(
            status_code=400,
            detail=f"Knowledge base {knowledge_base_id} is not available.",
        )
    if is_tag_available(
        db, knowledge_base_id, name=model.name, parent_id=model.parentId
    ):
        raise HTTPException(
            status_code=400, detail=f"Tag {model.name} is already available."
        )
    if model.parentId is not None:
        parent = get_knowledge_base_tag(db, model.parentId, knowledge_base_id)
        if parent is None:
            raise HTTPException(
                status_code=400, detail=f"Parent tag {model.parentId} is not available."
            )
    entity = KnowledgeBaseTagEntity(
        name=model.name,
        knowledge_base_id=knowledge_base_id,
        parent_id=model.parentId,
        description=model.description,
        user_id=user.id,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def partial_update_tag_by_id(
    db: Session,
    knowledge_base_id: int,
    tag_id: int,
    model: KnowledgeBaseTagModel,
) -> bool:
    entity = get_knowledge_base_tag(db, tag_id, knowledge_base_id)
    if entity is None:
        raise HTTPException(
            status_code=400,
            detail=f"Tag (/knowledge_bases/{knowledge_base_id}/tags/{tag_id}) is not available.",
        )
    modified = False
    if model.name is not None and model.name != entity.name:
        modified = True
        entity.name = model.name
    if model.description is not None and model.description != entity.description:
        modified = True
        entity.description = model.description
    if modified:
        entity.updatedAt = datetime.now()
        db.commit()
        db.refresh(entity)
        return True
    return False


def delete_tag_by_id(
    db: Session,
    id: int,
    knowledge_base_id: int,
) -> int:
    tag = (
        db.query(KnowledgeBaseTagEntity).filter(KnowledgeBaseTagEntity.id == id).first()
    )
    if tag is None:
        logging.info(
            f"knowledge base tag with id {id} not found, nothing deleted, and ignore exploring this information"
        )
        return 0
    supabase = SupabaseClient()
    if tag.parent_id is not None:
        count_query = (
            supabase.table("knowledge")
            .select("*", count="exact")
            .eq("metadata->knowledge_base_id", knowledge_base_id)
            .eq("metadata->tag", id)
        )
        count_response = count_query.execute()
        logging.info(
            f"find {count_response.count} knowledges with tag {id}, nothing deleted, and ignore exploring this information"
        )
        if int(count_response.count) > 0:
            raise HTTPException(
                status_code=499,
                detail=f"Tag {tag.name} used by knowledge.",
            )
    else:
        all_children_tags = (
            db.query(KnowledgeBaseTagEntity)
            .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
            .filter(KnowledgeBaseTagEntity.parent_id == id)
            .all()
        )
        all_children_tags_ids = [tag.id for tag in all_children_tags]
        count_query = (
            supabase.table("knowledge")
            .select("*", count="exact")
            .eq("metadata->knowledge_base_id", knowledge_base_id)
            .in_("metadata->tag", all_children_tags_ids)
        )
        count_response = count_query.execute()
        logging.info(
            f"find {count_response.count} knowledges in tags {all_children_tags_ids}, nothing deleted, and ignore exploring this information"
        )
        if int(count_response.count) > 0:
            raise HTTPException(
                status_code=499,
                detail=f"Tag {tag.name}'s children tags used by knowledge.",
            )

    count = (
        db.query(KnowledgeBaseTagEntity)
        .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
        .filter(
            or_(KnowledgeBaseTagEntity.id == id, KnowledgeBaseTagEntity.parent_id == id)
        )
        .delete()
    )
    # if count == 0:
    #     logging.info(
    #         f"knowledge base tag with id {id} not found, nothing deleted, and ignore exploring this information"
    #     )
    db.commit()
    return count


def is_tags_unique(tags: list):
    dict_tags = {}
    for tag in tags:
        if tag["tag"] not in dict_tags:
            dict_tags[tag["tag"]] = tag["parentTag"]
        else:
            if dict_tags[tag["tag"]] != tag["parentTag"]:
                return False
    return True


def batch_create_knowledge_base_tag(
    knowledge_base_id: int,
    tags: list,
    user_id: int,
):
    if len(tags) == 0:
        return []
    # # 判断相同的标签是否存在不同的分类
    # if not is_tags_unique(tags):
    #     logging.error("Tags has diffrent parent.")
    #     raise Exception("Tags has diffrent parent.")

    db = next(get_db())

    # 获取所有的父标签
    parent_tags = [tag["parentTag"] for tag in tags]
    parent_tags = list(set(parent_tags))
    # 获取数据库中已经存在的父标签
    existing_parent_tags = (
        db.query(KnowledgeBaseTagEntity)
        .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
        .filter(KnowledgeBaseTagEntity.parent_id == None)
        .filter(KnowledgeBaseTagEntity.name.in_(parent_tags))
        .all()
    )
    existing_parent_tags_names = [tag.name for tag in existing_parent_tags]

    # 创建不存在的父标签
    create_parent_tags = [
        tag for tag in parent_tags if tag not in existing_parent_tags_names
    ]
    if len(create_parent_tags) > 0:
        create_parent_tags = [
            KnowledgeBaseTagEntity(
                name=tag,
                knowledge_base_id=knowledge_base_id,
                parent_id=None,
                description=None,
                user_id=user_id,
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
            for tag in create_parent_tags
        ]
        db.add_all(create_parent_tags)
        db.commit()

    # 获取数据库中已经存在的父标签
    new_existing_parent_tags = (
        db.query(KnowledgeBaseTagEntity)
        .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
        .filter(KnowledgeBaseTagEntity.parent_id == None)
        .filter(KnowledgeBaseTagEntity.name.in_(parent_tags))
        .all()
    )

    # 获取所有的子标签
    children_tags = [tag["tag"] for tag in tags]
    existing_children_tags = (
        db.query(KnowledgeBaseTagEntity)
        .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
        .filter(KnowledgeBaseTagEntity.parent_id != None)
        .filter(KnowledgeBaseTagEntity.name.in_(children_tags))
        .all()
    )

    # existing_children_tags_names = [tag.name for tag in existing_children_tags]

    # create_children_tags = [
    #     tag for tag in tags if tag["tag"] not in existing_children_tags_names
    # ]
    create_children_tags = []

    for tag in tags:
        existing_children_tags_parent_id = [
            existing_tag.parent_id
            for existing_tag in existing_children_tags
            if existing_tag.name == tag["tag"]
        ]

        if len(existing_children_tags_parent_id) == 0:
            create_children_tags.append(tag)
            continue

        time.sleep(1)
        finded_existing_parent_tag = (
            db.query(KnowledgeBaseTagEntity)
            .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
            .filter(KnowledgeBaseTagEntity.id.in_(existing_children_tags_parent_id))
            .all()
        )
        existing_children_tags_parent_name = [
            existing_tag.name for existing_tag in finded_existing_parent_tag
        ]
        if tag["parentTag"] not in existing_children_tags_parent_name:
            create_children_tags.append(tag)

    # 创建子标签
    if len(create_children_tags) > 0:
        create_children_tags = [
            KnowledgeBaseTagEntity(
                name=tag["tag"],
                knowledge_base_id=knowledge_base_id,
                parent_id=[
                    parent_tag
                    for parent_tag in new_existing_parent_tags
                    if parent_tag.name == tag["parentTag"]
                ][0].id,
                description=None,
                user_id=user_id,
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
            for tag in create_children_tags
        ]
        db.add_all(create_children_tags)
        db.commit()

    new_existing_children_tags = (
        db.query(KnowledgeBaseTagEntity)
        .filter(KnowledgeBaseTagEntity.knowledge_base_id == knowledge_base_id)
        .filter(KnowledgeBaseTagEntity.parent_id != None)
        .filter(KnowledgeBaseTagEntity.name.in_(children_tags))
        .all()
    )

    for tag in new_existing_children_tags:
        tag.parent = [
            parent_tag
            for parent_tag in new_existing_parent_tags
            if parent_tag.id == tag.parent_id
        ][0]

    db.close()
    return new_existing_children_tags


def export_knowledge_base_to_excel(
    db: Session, knowledge_base_id: int, current_user: User
):
    size = 1000
    supabase = SupabaseClient()

    count_query = (
        supabase.table("knowledge")
        .select("*", count="exact")
        .eq("metadata->knowledge_base_id", knowledge_base_id)
    )

    count_response = count_query.execute()

    cycle = get_pages(count_response.count, size)

    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建一个新的Excel工作簿
        workbook = openpyxl.Workbook()

        # 创建一个工作表
        worksheet = workbook.active

        # 在工作表中写入数据
        worksheet["A1"] = "分类"
        worksheet["B1"] = "标签"
        worksheet["C1"] = "问题"
        worksheet["D1"] = "回答/知识点"
        for i in range(cycle):
            offset = i * size
            query = (
                supabase.table("knowledge")
                .select("id, content, metadata")
                .eq("metadata->knowledge_base_id", knowledge_base_id)
            )
            response = (
                query.order("id", desc=True).range(offset, offset + size).execute()
            )
            tags = [item["metadata"]["tag"] for item in response.data]
            unique_tags = list(set(tags))

            tag_entities = get_knowledge_base_tags_by_ids(
                db, unique_tags, knowledge_base_id
            )
            parent_tags = [
                tag.parent_id for tag in tag_entities if tag.parent_id != None
            ]
            unique_parent_tags = list(set(parent_tags))
            parent_tag_entities = get_knowledge_base_tags_by_ids(
                db, unique_parent_tags, knowledge_base_id
            )

            data = []
            for item in response.data:
                tag_id = item["metadata"]["tag"]
                content = item["content"]
                structure = (
                    item["metadata"]["structure"]
                    if "structure" in item["metadata"]
                    else None
                )
                # 知识库中单条知识的标签
                found_tags = [tag for tag in tag_entities if tag.id == tag_id]
                if found_tags.__len__() > 0:
                    tag_name = found_tags[0].name
                    parent_tag_id = found_tags[0].parent_id
                    parent_tag = [
                        tag for tag in parent_tag_entities if tag.id == parent_tag_id
                    ][0]
                    parent_tag_name = parent_tag.name
                else:
                    tag_name = ""
                    parent_tag_name = ""
                if structure != None and structure == KnowledgeStructure.QA.name:
                    content = json.loads(content)
                    question = content["question"]
                    answer = content["answer"]
                    data.append((parent_tag_name, tag_name, question, answer))
                else:
                    data.append((parent_tag_name, tag_name, "", content))

            for row_num, (category, label, question, answer) in enumerate(
                data, start=2
            ):
                worksheet[f"A{row_num + i * size}"] = category
                worksheet[f"B{row_num + i * size}"] = label
                worksheet[f"C{row_num + i * size}"] = question
                worksheet[f"D{row_num + i * size}"] = answer

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # 保存工作簿到文件
        workbook.save(f"{temp_dir}/result_{timestamp}.xlsx")

        # 关闭工作簿
        workbook.close()
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name="cn-northwest-1",
        )
        s3_client.upload_file(
            f"{temp_dir}/result_{timestamp}.xlsx",
            "knowledge-base",
            f"{current_user.organization.code}/result_{timestamp}.xlsx",
        )

        # 生成预签名 URL 的过期时间
        expiration = int(timedelta(minutes=5).total_seconds())

        # 生成预签名 URL
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": "knowledge-base",
                "Key": f"{current_user.organization.code}/result_{timestamp}.xlsx",
            },
            ExpiresIn=expiration,
        )
        logging.info(f"presigned_url: {presigned_url}")
    return presigned_url
