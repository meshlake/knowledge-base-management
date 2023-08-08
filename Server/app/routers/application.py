from fastapi import APIRouter, Depends
from typing import List
from app.entities.users import User
from app.dependencies import get_db
from sqlalchemy.orm import Session
from app.entities import applications
from app.models.application import Application, ApplicationCreate, ApplicationUpdate
from app.service.user import get_current_user, oauth2_scheme
import app.service.application as applicationService
from app.db import engine


applications.Base.metadata.create_all(bind=engine)

router = APIRouter(
    tags=["application"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)],
)


@router.get("/applications/all", dependencies=[Depends(oauth2_scheme)], response_model=List[Application])
def get_all_applications(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)):
    return applicationService.get_all_applications(db, user)


@router.get("/applications/{id}", dependencies=[Depends(oauth2_scheme)], response_model=Application)
def get_application(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return applicationService.get_application(id, db, user)


@router.post("/applications", dependencies=[Depends(oauth2_scheme)], response_model=Application)
def create_application(
    model: ApplicationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return applicationService.create_application(model, db, user)


@router.put("/applications/{id}", dependencies=[Depends(oauth2_scheme)], response_model=Application)
def update_application(
    id: int,
    model: ApplicationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return applicationService.update_application(id, model, db, user)


@router.delete("/applications/{id}", dependencies=[Depends(oauth2_scheme)])
def delete_application(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return applicationService.delete_application(id, db, user)
