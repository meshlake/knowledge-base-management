from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.entities import organizations
from app.db import engine
from app.models.organizationDto import (
    Organization,
    OrganizationCreate,
    OrganizationUpdate,
)
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.crud import organizationCurd
from app.service.user import oauth2_scheme
from app.service.organization import create_organization as create_organization_service
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

organizations.Base.metadata.create_all(bind=engine)

router = APIRouter(
    tags=["organizations"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)],
)


# 创建组织
@router.post("/organizations")
def create_organization(
    organization: OrganizationCreate, db: Session = Depends(get_db)
):
    new_organization = create_organization_service(
        db=db, organizationcreate=organization
    )
    return {"data": new_organization}


# 获取所有组织
@router.get("/organizations/all")
def get_organizations(db: Session = Depends(get_db)):
    organizations = organizationCurd.get_organizations(db=db)
    return {"data": organizations}


# 获取组织分页
@router.get("/organizations", response_model=Page[Organization])
def get_all_roles(db: Session = Depends(get_db)):
    return paginate(
        db,
        select(organizations.Organization).order_by(
            organizations.Organization.createdAt.desc()
        ),
    )


# 获取单个组织
@router.get("/organizations/{organization_id}")
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    organization = organizationCurd.get_organization(
        db=db, organization_id=organization_id
    )
    if not organization:
        raise HTTPException(status_code=404, detail="组织未找到")
    return {"data": organization}


# 更新组织
@router.put("/organizations/{organization_id}")
def update_organization(
    organization_id: int,
    organization: OrganizationUpdate,
    db: Session = Depends(get_db),
):
    updated_organization = organizationCurd.update_organization(
        db=db, organization_id=organization_id, new_name=organization.name
    )
    if not updated_organization:
        raise HTTPException(status_code=404, detail="组织未找到")
    return {"data": updated_organization}


# 删除组织
@router.delete("/organizations/{organization_id}")
def delete_organization(organization_id: int, db: Session = Depends(get_db)):
    deleted_organization = organizationCurd.delete_organization(
        db=db, organization_id=organization_id
    )
    if not deleted_organization:
        raise HTTPException(status_code=404, detail="组织未找到")
    return {"message": "删除成功"}
