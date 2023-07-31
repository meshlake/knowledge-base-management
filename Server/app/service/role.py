from fastapi import Depends
from app.dependencies import get_db
from app.crud import roleCurd
from app.models import roleDto
from sqlalchemy.orm import Session

def create_role(role: roleDto.RoleCreate, db: Session = Depends(get_db)):
    role = roleCurd.create_role(db, role)
    return role