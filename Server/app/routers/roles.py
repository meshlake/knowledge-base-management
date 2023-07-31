from fastapi import APIRouter, Depends
from app.dependencies import get_db
from app.entities import roles
from app.db import engine
from app.crud import roleCurd
from app.models import roleDto
from app.service.user import oauth2_scheme
from sqlalchemy.orm import Session
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from app.service.role import create_role

router = APIRouter(
    tags=["roles"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)],
)


# 创建角色
@router.post("/roles")
def create_roles(role: roleDto.RoleCreate, db: Session = Depends(get_db)):
    role = create_role(role, db)
    return {"data": role}


# 获取所有角色
@router.get("/roles/all")
def get_all_roles(db: Session = Depends(get_db)):
    roles = roleCurd.get_roles(db)
    return {"data": roles}


# 获取所有角色
@router.get("/roles", response_model=Page[roleDto.Role])
def get_all_roles(db: Session = Depends(get_db)):
    return paginate(
        db,
        select(roles.Role).order_by(roles.Role.createdAt.desc()),
    )
