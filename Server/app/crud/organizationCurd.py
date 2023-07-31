from sqlalchemy.orm import Session

from app.entities.organizations import Organization
from app.models.organizationDto import OrganizationCreate


# 创建组织
def create_organization(db: Session, organization_create: OrganizationCreate):
    organization = Organization(name=organization_create.name, code=organization_create.code)
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization


# 获取所有组织
def get_organizations(db: Session):
    organizations = db.query(Organization).all()
    return organizations


# 获取单个组织
def get_organization(db: Session, organization_id):
    organization = (
        db.query(Organization).filter(Organization.id == organization_id).first()
    )
    return organization


# 更新组织
def update_organization(db: Session, organization_id, new_name):
    organization = get_organization(db=db, organization_id=organization_id)
    if organization:
        organization.name = new_name
        db.commit()
        db.refresh(organization)
    return organization


# 删除组织
def delete_organization(db: Session, organization_id):
    organization = get_organization(db=db, organization_id=organization_id)
    if organization:
        db.delete(organization)
        db.commit()
    return organization
