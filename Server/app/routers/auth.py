import re
from fastapi import APIRouter, Depends, Request
from app.dependencies import get_db
from app.service.casbinEnforcer import enforcer
from app.service.user import oauth2_scheme
from app.crud import userCurd
from sqlalchemy.orm import Session
import json
import os

router = APIRouter(
    tags=["auth"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)],
)


# 修改角色权限
@router.put("/auth/roles/{role}/permissions")
def update_role_permissions(role: str, permissions: list):
    enforcer.delete_permissions_for_user(role)
    for permission in permissions:
        enforcer.add_permission_for_user(
            role, permission["type"], permission["route"], permission["method"]
        )
    permissions = enforcer.get_permissions_for_user(role)
    return {"data": permissions}


@router.get("/auth/permissions")
def get_all_permissions():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = "../auth.json"
    absolute_path = os.path.join(current_dir, relative_path)
    with open(absolute_path, "r") as file:
        data = json.load(file)
    return {"data": data}


@router.get("/auth/roles/{role}/permissions")
def get_role_permissions(role: str):
    permissions = enforcer.get_permissions_for_user(role)
    return {"data": permissions}
