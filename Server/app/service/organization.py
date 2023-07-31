from fastapi import Depends
from sqlalchemy.orm import Session
from app.crud import organizationCurd
from app.dependencies import get_db
from app.models import organizationDto

def create_organization(organizationcreate: organizationDto.OrganizationCreate, db: Session = Depends(get_db)):
    organization = organizationDto.OrganizationCreate(
        name=organizationcreate.name,
        code=organizationcreate.code
    )
    organization = organizationCurd.create_organization(db, organization)
    # application = applicationDto.ApplicationCreate(
    #     name=f"{organization.name}后台",
    #     category="MANAGEMENT_PLATFORM",
    #     description=f"{organization.name}后台",
    #     owner=organization.code,
    #     model_id=0,
    #     properties={},
    # )
    # appManage.create_app(application, db)
    return organization