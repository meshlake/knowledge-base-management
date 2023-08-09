from datetime import datetime
import logging
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.models.files import FileCreate
from app.models.userDto import User
from app.entities.files import File as FileEntity
from app.models.enums import FileStatus

load_dotenv()


def upload_file(file_obj, bucket, object_name):
    """Upload a file to an S3 bucket

    :param file_obj: 文件对象，如 SpooledTemporaryFile
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    # Upload the file
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name="cn-northwest-1",
    )
    try:
        file_obj.seek(0)  # 将文件指针移至开头
        s3_client.upload_fileobj(file_obj, bucket, object_name)
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
