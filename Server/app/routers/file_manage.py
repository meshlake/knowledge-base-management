from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from app.models.files import FileCreate, File as FileModel
from app.models.userDto import User
from app.service.knowledge_item import create_knowledge_items_for_file
from app.service.user import oauth2_scheme, get_current_user
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.service.file_manage import (
    upload_file as upload_file_service,
    get_files as get_files_service,
    create_file as create_file_service,
)
from app.util import uniqueFileName

router = APIRouter(
    tags=["files"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)],
)


@router.post("/files")
def create_file(
    model: FileCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_entity = create_file_service(model, current_user, db)
    background_tasks.add_task(
        create_knowledge_items_for_file,
        model.knowledge_base_id,
        current_user,
        model.path,
    )
    return {"data": file_entity}


@router.post("/files/upload")
async def upload_file(file: UploadFile, current_user: User = Depends(get_current_user)):
    new_file_name = uniqueFileName(file.filename)
    upload_result = upload_file_service(
        file.file, "knowledge-base", f"{current_user.organization.code}/{new_file_name}"
    )
    if not upload_result:
        raise HTTPException(
            status_code=500,
            detail="文件上传失败",
        )
    return {
        "data": {
            "name": file.filename,
            "path": f"knowledge-base/{current_user.organization.code}/{new_file_name}",
        }
    }


@router.get("/files")
def get_files(knowledge_base_id: int, db: Session = Depends(get_db)):
    files: list[FileModel] = get_files_service(knowledge_base_id, db)
    return {"data": files}
