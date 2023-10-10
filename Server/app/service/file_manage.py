from datetime import datetime
import io
import logging
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.models.files import FileCreate
from app.models.userDto import User
from app.entities.files import File as FileEntity
from app.models.enums import FileStatus
from unstructured.file_utils.filetype import (
    FileType,
    detect_filetype,
)
import pandas as pd

load_dotenv()


async def validate_excel(file_obj: UploadFile):
    filetype = detect_filetype(file_obj.filename)
    try:
        if (filetype == FileType.XLSX) or (filetype == FileType.XLS):
            file = await file_obj.read()  # 读取文件内容
            data_dict = pd.read_excel(
                io.BytesIO(file), sheet_name=None
            )  # 使用io.BytesIO将字节数据转换为文件对象
            for sheet_name, table in data_dict.items():
                header = table.columns.tolist()
                if set(header) != set(["分类", "标签", "问题", "答案"]):  # 判断表头是否为问题和答案
                    logging.error(f"上传文件错误：{file_obj.filename}表头不符合要求")
                    raise HTTPException(
                        status_code=400,
                        detail="文件格式不符合规范",
                    )
        elif filetype == FileType.CSV:
            file = await file_obj.read()
            data_dict = pd.read_csv(io.BytesIO(file), sep=None, engine="python")
            header = data_dict.columns.tolist()
            if set(header) != set(["分类", "标签", "问题", "答案"]):
                logging.error(f"上传文件错误：{file_obj.filename}表头不符合要求")
                raise HTTPException(
                    status_code=400,
                    detail="文件格式不符合规范",
                )
    except Exception as e:
        logging.error(e)
        raise e


async def upload_file(file_obj: UploadFile, bucket, object_name):
    """Upload a file to an S3 bucket

    :param file_obj: 文件对象，如 SpooledTemporaryFile
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    await validate_excel(file_obj)

    # Upload the file
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name="cn-northwest-1",
    )
    try:
        file_obj.file.seek(0)  # 将文件指针移至开头
        s3_client.upload_fileobj(file_obj.file, bucket, object_name)
    except ClientError as e:
        logging.error(f"上传文件错误：{e}")
        return False
    return True


def create_file(
    file: FileCreate,
    user: User,
    db: Session,
):
    entity = FileEntity(
        name=file.name,
        knowledge_base_id=file.knowledge_base_id,
        user_id=user.id,
        path=file.path,
        status=FileStatus.UPLOADED.name,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def get_files(knowledge_base_id: int, db: Session):
    return (
        db.query(FileEntity)
        .filter(FileEntity.knowledge_base_id == knowledge_base_id)
        .all()
    )


def update_file_status(db: Session, filepath: int, status: FileStatus):
    db.query(FileEntity).filter(FileEntity.path == filepath).update(
        {
            "status": status.name,
        }
    )
    db.commit()
    return True
