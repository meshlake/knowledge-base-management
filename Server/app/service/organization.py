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
    return organization